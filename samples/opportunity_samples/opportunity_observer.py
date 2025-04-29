"""
Sample code that shows an opportunity for applying the Observer pattern.

This file contains code that manually notifies multiple objects when a state
changes, which is a good candidate for refactoring using the Observer pattern.
"""

class User:
    """A user in the system."""
    
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.order_history = []


class Order:
    """An order in the system."""
    
    def __init__(self, order_id, user_id, items, total):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.total = total
        self.status = "pending"


class NotificationService:
    """Service for sending notifications."""
    
    def send_email(self, email, subject, message):
        print(f"Sending email to {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("Email sent successfully!")
    
    def send_sms(self, phone, message):
        print(f"Sending SMS to {phone}")
        print(f"Message: {message}")
        print("SMS sent successfully!")


class AnalyticsService:
    """Service for tracking analytics events."""
    
    def track_event(self, event_name, event_data):
        print(f"Tracking event: {event_name}")
        print(f"Event data: {event_data}")
        print("Event tracked successfully!")


class InventoryService:
    """Service for managing inventory."""
    
    def update_inventory(self, items):
        print("Updating inventory...")
        for item in items:
            print(f"Updating item {item['id']}: {item['quantity']} units")
        print("Inventory updated successfully!")


class OrderService:
    """Service for managing orders."""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.analytics_service = AnalyticsService()
        self.inventory_service = InventoryService()
        self.orders = {}
        self.users = {}
        self.listeners = []
    
    def add_listener(self, listener):
        """Add a service to notify."""
        self.listeners.append(listener)
    
    def add_user(self, user):
        """Add a user to the system."""
        self.users[user.user_id] = user
    
    def create_order(self, order_id, user_id, items, total):
        """Create a new order."""
        order = Order(order_id, user_id, items, total)
        self.orders[order_id] = order
        
        # Get the user
        user = self.users[user_id]
        
        # Add the order to the user's order history
        user.order_history.append(order)
        
        # Notify various components about the new order
        # This is an opportunity to use the Observer pattern
        self.notification_service.send_email(
            user.email,
            "Order Confirmation",
            f"Your order #{order_id} has been received. Total: ${total}"
        )
        
        self.analytics_service.track_event(
            "order_created",
            {
                "order_id": order_id,
                "user_id": user_id,
                "total": total,
                "item_count": len(items)
            }
        )
        
        self.inventory_service.update_inventory(items)
        
        # Notify all listeners
        for listener in self.listeners:
            listener.on_order_created(order)
        
        return order
    
    def update_order_status(self, order_id, new_status):
        """Update the status of an order."""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        old_status = order.status
        order.status = new_status
        
        # Get the user
        user = self.users[order.user_id]
        
        # Notify various components about the status change
        # This is an opportunity to use the Observer pattern
        self.notification_service.send_email(
            user.email,
            "Order Status Update",
            f"Your order #{order_id} status has been updated from {old_status} to {new_status}"
        )
        
        self.analytics_service.track_event(
            "order_status_updated",
            {
                "order_id": order_id,
                "user_id": order.user_id,
                "old_status": old_status,
                "new_status": new_status
            }
        )
        
        # If the order is cancelled, update inventory
        if new_status == "cancelled":
            self.inventory_service.update_inventory([
                {"id": item["id"], "quantity": item["quantity"]}
                for item in order.items
            ])
        
        # Notify all listeners
        for listener in self.listeners:
            listener.on_status_changed(order, old_status, new_status)
        
        return order


# Usage example
if __name__ == "__main__":
    # Create services
    order_service = OrderService()
    
    # Create a user
    user = User(1, "John Doe", "john@example.com")
    order_service.add_user(user)
    
    # Create an order
    items = [
        {"id": 101, "name": "Product 1", "price": 29.99, "quantity": 2},
        {"id": 102, "name": "Product 2", "price": 49.99, "quantity": 1}
    ]
    total = sum(item["price"] * item["quantity"] for item in items)
    
    print("Creating order...")
    order = order_service.create_order(1001, user.user_id, items, total)
    print()
    
    # Update order status
    print("Updating order status to 'shipped'...")
    order_service.update_order_status(1001, "shipped")
    print()
    
    # Cancel the order
    print("Updating order status to 'cancelled'...")
    order_service.update_order_status(1001, "cancelled")