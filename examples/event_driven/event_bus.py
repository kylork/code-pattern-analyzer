"""
Event bus implementation for the event-driven architecture example.

This module provides the central event bus that facilitates communication
between different components in the system through events.
"""

import logging
from typing import Dict, List, Callable, Any, Type, Set
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .events import Event


logger = logging.getLogger(__name__)


class EventBus:
    """Central event bus for publishing and subscribing to events."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of EventBus exists."""
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the event bus if not already initialized."""
        if self._initialized:
            return
            
        self._subscribers = {}  # Event type to list of handlers
        self._type_subscribers = {}  # Event class to list of handlers
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._async_mode = False
        self._event_store = []  # Simple in-memory event store
        self._initialized = True
        logger.info("EventBus initialized")
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe a handler to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The function that will handle the event
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(handler)
        logger.debug(f"Handler {handler.__name__} subscribed to {event_type}")
    
    def subscribe_to(self, event_class: Type[Event], handler: Callable[[Event], None]) -> None:
        """Subscribe a handler to a specific event class.
        
        Args:
            event_class: The class of event to subscribe to
            handler: The function that will handle the event
        """
        if event_class not in self._type_subscribers:
            self._type_subscribers[event_class] = set()
        self._type_subscribers[event_class].add(handler)
        logger.debug(f"Handler {handler.__name__} subscribed to {event_class.__name__}")
    
    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Unsubscribe a handler from a specific event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler to unsubscribe
        """
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type}")
    
    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Store the event
        self._event_store.append(event)
        
        # Get all handlers for this event type
        handlers = set()
        
        # Add handlers subscribed by event type
        if event.event_type in self._subscribers:
            handlers.update(self._subscribers[event.event_type])
        
        # Add handlers subscribed by event class
        for event_class, class_handlers in self._type_subscribers.items():
            if isinstance(event, event_class):
                handlers.update(class_handlers)
        
        if not handlers:
            logger.warning(f"No handlers found for event {event.event_type}")
            return
        
        logger.info(f"Publishing event {event.event_type} to {len(handlers)} handlers")
        
        # If async mode is enabled, use asyncio
        if self._async_mode:
            asyncio.create_task(self._publish_async(event, handlers))
        else:
            self._publish_sync(event, handlers)
    
    def _publish_sync(self, event: Event, handlers: Set[Callable]) -> None:
        """Publish an event synchronously.
        
        Args:
            event: The event to publish
            handlers: Set of handlers to call
        """
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in handler {handler.__name__}: {e}")
    
    async def _publish_async(self, event: Event, handlers: Set[Callable]) -> None:
        """Publish an event asynchronously.
        
        Args:
            event: The event to publish
            handlers: Set of handlers to call
        """
        for handler in handlers:
            try:
                # Check if handler is a coroutine function
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    # Run synchronous handlers in a thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(self._executor, handler, event)
            except Exception as e:
                logger.error(f"Error in handler {handler.__name__}: {e}")
    
    def enable_async_mode(self) -> None:
        """Enable asynchronous event handling."""
        self._async_mode = True
        logger.info("Async mode enabled")
    
    def disable_async_mode(self) -> None:
        """Disable asynchronous event handling."""
        self._async_mode = False
        logger.info("Async mode disabled")
    
    def get_events(self, event_type: str = None) -> List[Event]:
        """Get events from the in-memory store.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            List of events
        """
        if event_type:
            return [e for e in self._event_store if e.event_type == event_type]
        return list(self._event_store)