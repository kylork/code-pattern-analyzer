"""
Event consumers for the event-driven architecture example.

This module contains components that consume events in the system.
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


class NotificationService:
    """Service for sending notifications based on events."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the notification service.
        
        Args:
            event_bus: Event bus to subscribe to
        """
        self.event_bus = event_bus or EventBus()
        
        # Subscribe to relevant events
        self.event_bus.subscribe("user.created", self.handle_user_created)
        self.event_bus.subscribe("order.created", self.handle_order_created)
        self.event_bus.subscribe("order.status_changed", self.handle_order_status_changed)
        self.event_bus.subscribe("payment.processed", self.handle_payment_processed)
        self.event_bus.subscribe("payment.failed", self.handle_payment_failed)
        
        logger.info("NotificationService initialized and subscribed to events")
    
    def handle_user_created(self, event: UserCreatedEvent) -> None:
        """Handle user created events.
        
        Args:
            event: The user created event
        """
        logger.info(f"Sending welcome email to {event.email}")
        # In a real system, this would send an actual email
        print(f"📧 Welcome email sent to {event.email}")
    
    def handle_order_created(self, event: OrderCreatedEvent) -> None:
        """Handle order created events.
        
        Args:
            event: The order created event
        """
        logger.info(f"Sending order confirmation for order {event.order_id}")
        # In a real system, this would send an actual notification
        print(f"📧 Order confirmation sent for order {event.order_id}")
    
    def handle_order_status_changed(self, event: OrderStatusChangedEvent) -> None:
        """Handle order status changed events.
        
        Args:
            event: The order status changed event
        """
        logger.info(f"Sending status update for order {event.order_id}: {event.old_status} -> {event.new_status}")
        # In a real system, this would send an actual notification
        print(f"📧 Order status update sent: {event.new_status} for order {event.order_id}")
    
    def handle_payment_processed(self, event: PaymentProcessedEvent) -> None:
        """Handle payment processed events.
        
        Args:
            event: The payment processed event
        """
        logger.info(f"Sending payment confirmation for order {event.order_id}")
        # In a real system, this would send an actual notification
        print(f"📧 Payment confirmation sent for order {event.order_id}")
    
    def handle_payment_failed(self, event: PaymentFailedEvent) -> None:
        """Handle payment failed events.
        
        Args:
            event: The payment failed event
        """
        logger.info(f"Sending payment failure notification for order {event.order_id}")
        # In a real system, this would send an actual notification
        print(f"📧 Payment failure notification sent for order {event.order_id}: {event.error_message}")


class AnalyticsService:
    """Service for tracking analytics based on events."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the analytics service.
        
        Args:
            event_bus: Event bus to subscribe to
        """
        self.event_bus = event_bus or EventBus()
        self.stats = {
            "users_created": 0,
            "orders_created": 0,
            "payments_processed": 0,
            "payments_failed": 0,
        }
        
        # Subscribe to all events for analytics
        self.event_bus.subscribe("user.created", self.track_user_created)
        self.event_bus.subscribe("order.created", self.track_order_created)
        self.event_bus.subscribe("payment.processed", self.track_payment_processed)
        self.event_bus.subscribe("payment.failed", self.track_payment_failed)
        
        logger.info("AnalyticsService initialized and subscribed to events")
    
    def track_user_created(self, event: UserCreatedEvent) -> None:
        """Track user created events.
        
        Args:
            event: The user created event
        """
        self.stats["users_created"] += 1
        logger.info(f"Tracked user creation: {event.user_id}")
    
    def track_order_created(self, event: OrderCreatedEvent) -> None:
        """Track order created events.
        
        Args:
            event: The order created event
        """
        self.stats["orders_created"] += 1
        logger.info(f"Tracked order creation: {event.order_id}")
    
    def track_payment_processed(self, event: PaymentProcessedEvent) -> None:
        """Track payment processed events.
        
        Args:
            event: The payment processed event
        """
        self.stats["payments_processed"] += 1
        logger.info(f"Tracked payment processing: {event.payment_id}")
    
    def track_payment_failed(self, event: PaymentFailedEvent) -> None:
        """Track payment failed events.
        
        Args:
            event: The payment failed event
        """
        self.stats["payments_failed"] += 1
        logger.info(f"Tracked payment failure: {event.payment_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current analytics statistics.
        
        Returns:
            Dictionary of statistics
        """
        return self.stats.copy()


class InventoryService:
    """Service for managing inventory based on order events."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the inventory service.
        
        Args:
            event_bus: Event bus to subscribe to
        """
        self.event_bus = event_bus or EventBus()
        self.inventory = {
            "item1": 100,
            "item2": 50,
            "item3": 75,
        }
        
        # Subscribe to relevant events
        self.event_bus.subscribe("order.created", self.handle_order_created)
        self.event_bus.subscribe("order.status_changed", self.handle_order_status_changed)
        
        logger.info("InventoryService initialized and subscribed to events")
    
    def handle_order_created(self, event: OrderCreatedEvent) -> None:
        """Handle order created events by reserving inventory.
        
        Args:
            event: The order created event
        """
        logger.info(f"Reserving inventory for order {event.order_id}")
        
        # Reserve inventory for each item
        for item in event.items:
            item_id = item.get("item_id", "")
            quantity = item.get("quantity", 1)
            
            if item_id in self.inventory:
                # Reserve the inventory
                if self.inventory[item_id] >= quantity:
                    self.inventory[item_id] -= quantity
                    logger.info(f"Reserved {quantity} units of {item_id}")
                else:
                    logger.warning(f"Insufficient inventory for {item_id}: requested {quantity}, have {self.inventory[item_id]}")
    
    def handle_order_status_changed(self, event: OrderStatusChangedEvent) -> None:
        """Handle order status changed events.
        
        Args:
            event: The order status changed event
        """
        # If order is cancelled, restore inventory
        if event.new_status == "cancelled" and event.old_status != "cancelled":
            logger.info(f"Order {event.order_id} cancelled, restoring inventory")
            
            # In a real system, we would look up the order details
            # For this example, we'll just log the event
            print(f"🔄 Would restore inventory for cancelled order {event.order_id}")
    
    def get_inventory_levels(self) -> Dict[str, int]:
        """Get current inventory levels.
        
        Returns:
            Dictionary of inventory levels
        """
        return self.inventory.copy()