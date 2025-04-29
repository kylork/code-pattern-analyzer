"""
Event producers for the event-driven architecture example.

This module contains components that produce events in the system.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4

from .events import (
    Event, UserCreatedEvent, UserUpdatedEvent, 
    OrderCreatedEvent, OrderStatusChangedEvent,
    PaymentProcessedEvent, PaymentFailedEvent
)
from .event_bus import EventBus


logger = logging.getLogger(__name__)


class UserService:
    """Service for managing users, acts as an event producer."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the user service.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self.event_bus = event_bus or EventBus()
        self.users = {}  # Simple in-memory store
    
    def create_user(self, username: str, email: str, password: str) -> str:
        """Create a new user and publish an event.
        
        Args:
            username: User's username
            email: User's email
            password: User's password (would be hashed in a real system)
            
        Returns:
            The user ID
        """
        # Generate a user ID
        user_id = str(uuid4())
        
        # Store the user
        self.users[user_id] = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password": password,  # In a real system, this would be hashed
            "created_at": "2023-01-01T00:00:00Z",  # Simplified timestamp
            "status": "active"
        }
        
        # Create and publish the event
        event = UserCreatedEvent(
            user_id=user_id,
            username=username,
            email=email
        )
        self.event_bus.publish(event)
        
        logger.info(f"User created with ID: {user_id}")
        return user_id
    
    def update_user(self, user_id: str, updated_fields: Dict[str, Any]) -> bool:
        """Update a user's information and publish an event.
        
        Args:
            user_id: The ID of the user to update
            updated_fields: Dictionary of fields to update
            
        Returns:
            True if the user was updated, False otherwise
        """
        if user_id not in self.users:
            logger.warning(f"User not found: {user_id}")
            return False
        
        # Update the user
        user = self.users[user_id]
        for key, value in updated_fields.items():
            if key in user and key != "user_id":  # Prevent changing user_id
                user[key] = value
        
        # Create and publish the event
        event = UserUpdatedEvent(
            user_id=user_id,
            updated_fields=updated_fields
        )
        self.event_bus.publish(event)
        
        logger.info(f"User updated: {user_id}")
        return True


class OrderService:
    """Service for managing orders, acts as an event producer."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the order service.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self.event_bus = event_bus or EventBus()
        self.orders = {}  # Simple in-memory store
    
    def create_order(self, user_id: str, items: List[Dict[str, Any]]) -> str:
        """Create a new order and publish an event.
        
        Args:
            user_id: ID of the user placing the order
            items: List of items in the order
            
        Returns:
            The order ID
        """
        # Generate an order ID
        order_id = str(uuid4())
        
        # Calculate total amount
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        # Store the order
        self.orders[order_id] = {
            "order_id": order_id,
            "user_id": user_id,
            "items": items,
            "total_amount": total_amount,
            "status": "pending",
            "created_at": "2023-01-01T00:00:00Z"  # Simplified timestamp
        }
        
        # Create and publish the event
        event = OrderCreatedEvent(
            order_id=order_id,
            user_id=user_id,
            items=items,
            total_amount=total_amount
        )
        self.event_bus.publish(event)
        
        logger.info(f"Order created with ID: {order_id}")
        return order_id
    
    def update_order_status(self, order_id: str, new_status: str, changed_by: str) -> bool:
        """Update an order's status and publish an event.
        
        Args:
            order_id: The ID of the order to update
            new_status: The new status of the order
            changed_by: ID or name of the entity changing the status
            
        Returns:
            True if the order was updated, False otherwise
        """
        if order_id not in self.orders:
            logger.warning(f"Order not found: {order_id}")
            return False
        
        # Update the order
        order = self.orders[order_id]
        old_status = order["status"]
        order["status"] = new_status
        
        # Create and publish the event
        event = OrderStatusChangedEvent(
            order_id=order_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by
        )
        self.event_bus.publish(event)
        
        logger.info(f"Order status updated: {order_id} -> {new_status}")
        return True


class PaymentService:
    """Service for processing payments, acts as an event producer."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the payment service.
        
        Args:
            event_bus: Event bus for publishing events
        """
        self.event_bus = event_bus or EventBus()
        self.payments = {}  # Simple in-memory store
    
    def process_payment(self, order_id: str, amount: float, payment_method: str) -> Dict[str, Any]:
        """Process a payment and publish an event.
        
        Args:
            order_id: ID of the order being paid for
            amount: Amount to charge
            payment_method: Payment method to use
            
        Returns:
            Payment result dictionary
        """
        # Generate a payment ID
        payment_id = str(uuid4())
        
        # In a real system, this would call a payment gateway
        # Simulate a payment with a 90% success rate
        import random
        success = random.random() < 0.9
        
        if success:
            # Payment succeeded
            result = {
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": amount,
                "status": "processed",
                "payment_method": payment_method
            }
            
            # Store the payment
            self.payments[payment_id] = result
            
            # Create and publish the event
            event = PaymentProcessedEvent(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                status="processed",
                payment_method=payment_method
            )
            self.event_bus.publish(event)
            
            logger.info(f"Payment processed: {payment_id}")
        else:
            # Payment failed
            result = {
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": amount,
                "status": "failed",
                "error_code": "PAYMENT_REJECTED",
                "error_message": "Payment was rejected by the payment processor"
            }
            
            # Store the payment
            self.payments[payment_id] = result
            
            # Create and publish the event
            event = PaymentFailedEvent(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                error_code="PAYMENT_REJECTED",
                error_message="Payment was rejected by the payment processor"
            )
            self.event_bus.publish(event)
            
            logger.info(f"Payment failed: {payment_id}")
        
        return result