"""
Events module for the event-driven architecture example.

This module defines the core event types and base classes for the event-driven system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4


@dataclass
class Event:
    """Base class for all events in the system."""
    
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = field(default="event")
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = field(default=1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to a dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "metadata": self.metadata,
            "data": self.get_event_data()
        }
    
    def get_event_data(self) -> Dict[str, Any]:
        """Get the event-specific data.
        
        Subclasses should override this to include their specific data.
        """
        return {}


# User domain events
@dataclass
class UserCreatedEvent(Event):
    """Event emitted when a new user is created."""
    
    user_id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    email: str = ""
    
    def __post_init__(self):
        self.event_type = "user.created"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
        }


@dataclass
class UserUpdatedEvent(Event):
    """Event emitted when a user's information is updated."""
    
    user_id: str = ""
    updated_fields: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.event_type = "user.updated"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "updated_fields": self.updated_fields,
        }


# Order domain events
@dataclass
class OrderCreatedEvent(Event):
    """Event emitted when a new order is created."""
    
    order_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    total_amount: float = 0.0
    
    def __post_init__(self):
        self.event_type = "order.created"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "items": self.items,
            "total_amount": self.total_amount,
        }


@dataclass
class OrderStatusChangedEvent(Event):
    """Event emitted when an order's status changes."""
    
    order_id: str = ""
    old_status: str = ""
    new_status: str = ""
    changed_by: str = ""
    
    def __post_init__(self):
        self.event_type = "order.status_changed"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by,
        }


# Payment domain events
@dataclass
class PaymentProcessedEvent(Event):
    """Event emitted when a payment is processed."""
    
    payment_id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    amount: float = 0.0
    status: str = "processed"
    payment_method: str = ""
    
    def __post_init__(self):
        self.event_type = "payment.processed"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "amount": self.amount,
            "status": self.status,
            "payment_method": self.payment_method,
        }


@dataclass
class PaymentFailedEvent(Event):
    """Event emitted when a payment fails."""
    
    payment_id: str = field(default_factory=lambda: str(uuid4()))
    order_id: str = ""
    amount: float = 0.0
    error_code: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        self.event_type = "payment.failed"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "amount": self.amount,
            "error_code": self.error_code,
            "error_message": self.error_message,
        }