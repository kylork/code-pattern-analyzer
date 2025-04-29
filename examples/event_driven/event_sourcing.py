"""
Event Sourcing implementation for the event-driven architecture example.

This module demonstrates event sourcing, where the state of an entity
is determined by the sequence of events that have occurred.
"""

import logging
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from uuid import uuid4

from .events import Event


logger = logging.getLogger(__name__)


class EventStore:
    """Stores and retrieves events for event sourcing."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of EventStore exists."""
        if cls._instance is None:
            cls._instance = super(EventStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the event store if not already initialized."""
        if self._initialized:
            return
            
        self._events = {}  # Aggregate ID to list of events
        self._initialized = True
        logger.info("EventStore initialized")
    
    def append_event(self, aggregate_id: str, event: Event) -> None:
        """Append an event to an aggregate's event stream.
        
        Args:
            aggregate_id: The ID of the aggregate
            event: The event to append
        """
        if aggregate_id not in self._events:
            self._events[aggregate_id] = []
        self._events[aggregate_id].append(event)
        logger.debug(f"Event {event.event_type} appended to aggregate {aggregate_id}")
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for an aggregate.
        
        Args:
            aggregate_id: The ID of the aggregate
            
        Returns:
            List of events for the aggregate
        """
        return self._events.get(aggregate_id, [])[:]
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type.
        
        Args:
            event_type: The type of events to get
            
        Returns:
            List of events of the specified type
        """
        events = []
        for aggregate_events in self._events.values():
            events.extend([e for e in aggregate_events if e.event_type == event_type])
        return events


class Aggregate:
    """Base class for aggregates in event sourcing."""
    
    def __init__(self, aggregate_id: str):
        """Initialize the aggregate.
        
        Args:
            aggregate_id: The ID of the aggregate
        """
        self.id = aggregate_id
        self.version = 0
        self._changes = []  # Uncommitted events
        self._event_store = EventStore()
    
    def apply_event(self, event: Event, is_new: bool = True) -> None:
        """Apply an event to update the aggregate state.
        
        Args:
            event: The event to apply
            is_new: Whether this is a new event (True) or a historical one (False)
        """
        # Find the appropriate apply method
        event_type = event.event_type.replace(".", "_")
        method_name = f"apply_{event_type}"
        
        if hasattr(self, method_name):
            # Call the apply method to update state
            getattr(self, method_name)(event)
        else:
            logger.warning(f"No apply method found for event type {event.event_type}")
        
        # Increment version and track the event if it's new
        self.version += 1
        if is_new:
            self._changes.append(event)
    
    def load_from_history(self, events: List[Event]) -> None:
        """Load the aggregate state from historical events.
        
        Args:
            events: List of events to apply
        """
        for event in events:
            self.apply_event(event, is_new=False)
    
    def commit_changes(self) -> None:
        """Commit uncommitted events to the event store."""
        for event in self._changes:
            self._event_store.append_event(self.id, event)
        self._changes = []
    
    def get_uncommitted_changes(self) -> List[Event]:
        """Get uncommitted events.
        
        Returns:
            List of uncommitted events
        """
        return self._changes[:]


class UserAggregate(Aggregate):
    """User aggregate for event sourcing."""
    
    def __init__(self, user_id: str):
        """Initialize the user aggregate.
        
        Args:
            user_id: The user ID
        """
        super().__init__(user_id)
        self.username = None
        self.email = None
        self.status = None
        self.created_at = None
        self.updated_at = None
    
    def apply_user_created(self, event: Event) -> None:
        """Apply user created event.
        
        Args:
            event: The user created event
        """
        data = event.get_event_data()
        self.username = data.get("username")
        self.email = data.get("email")
        self.status = "active"
        self.created_at = event.timestamp
        self.updated_at = event.timestamp
    
    def apply_user_updated(self, event: Event) -> None:
        """Apply user updated event.
        
        Args:
            event: The user updated event
        """
        data = event.get_event_data()
        updated_fields = data.get("updated_fields", {})
        
        # Update fields
        for key, value in updated_fields.items():
            if hasattr(self, key) and key not in ["id", "version"]:
                setattr(self, key, value)
        
        self.updated_at = event.timestamp


class OrderAggregate(Aggregate):
    """Order aggregate for event sourcing."""
    
    def __init__(self, order_id: str):
        """Initialize the order aggregate.
        
        Args:
            order_id: The order ID
        """
        super().__init__(order_id)
        self.user_id = None
        self.items = []
        self.total_amount = 0.0
        self.status = None
        self.created_at = None
        self.updated_at = None
    
    def apply_order_created(self, event: Event) -> None:
        """Apply order created event.
        
        Args:
            event: The order created event
        """
        data = event.get_event_data()
        self.user_id = data.get("user_id")
        self.items = data.get("items", [])
        self.total_amount = data.get("total_amount", 0.0)
        self.status = "pending"
        self.created_at = event.timestamp
        self.updated_at = event.timestamp
    
    def apply_order_status_changed(self, event: Event) -> None:
        """Apply order status changed event.
        
        Args:
            event: The order status changed event
        """
        data = event.get_event_data()
        self.status = data.get("new_status")
        self.updated_at = event.timestamp


class Repository:
    """Repository for loading and saving aggregates."""
    
    def __init__(self, aggregate_class: Type[Aggregate]):
        """Initialize the repository.
        
        Args:
            aggregate_class: The class of aggregate to work with
        """
        self.aggregate_class = aggregate_class
        self.event_store = EventStore()
    
    def load(self, aggregate_id: str) -> Aggregate:
        """Load an aggregate by its ID.
        
        Args:
            aggregate_id: The ID of the aggregate to load
            
        Returns:
            The loaded aggregate
        """
        # Create a new instance of the aggregate
        aggregate = self.aggregate_class(aggregate_id)
        
        # Get the aggregate's events from the event store
        events = self.event_store.get_events(aggregate_id)
        
        # Apply the events to rebuild the aggregate state
        aggregate.load_from_history(events)
        
        return aggregate
    
    def save(self, aggregate: Aggregate) -> None:
        """Save an aggregate by committing its changes.
        
        Args:
            aggregate: The aggregate to save
        """
        # Commit the aggregate's changes
        aggregate.commit_changes()