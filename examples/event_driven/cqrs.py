"""
CQRS (Command Query Responsibility Segregation) implementation for the event-driven architecture example.

This module demonstrates CQRS, where commands (writes) and queries (reads)
are separated into different models.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
from uuid import uuid4

from .events import Event
from .event_bus import EventBus


logger = logging.getLogger(__name__)


# Command-related classes
class Command:
    """Base class for all commands in the system."""
    
    command_type: str = "command"
    
    def validate(self) -> bool:
        """Validate the command.
        
        Returns:
            True if the command is valid, False otherwise
        """
        return True


class CreateUserCommand(Command):
    """Command to create a new user."""
    
    command_type = "create_user"
    
    def __init__(self, username: str, email: str, password: str):
        """Initialize the command.
        
        Args:
            username: The username
            email: The email
            password: The password
        """
        self.username = username
        self.email = email
        self.password = password
    
    def validate(self) -> bool:
        """Validate the command.
        
        Returns:
            True if the command is valid, False otherwise
        """
        # Basic validation
        if not self.username or not self.email or not self.password:
            return False
        if '@' not in self.email:
            return False
        return True


class CreateOrderCommand(Command):
    """Command to create a new order."""
    
    command_type = "create_order"
    
    def __init__(self, user_id: str, items: List[Dict[str, Any]]):
        """Initialize the command.
        
        Args:
            user_id: The user ID
            items: The order items
        """
        self.user_id = user_id
        self.items = items
    
    def validate(self) -> bool:
        """Validate the command.
        
        Returns:
            True if the command is valid, False otherwise
        """
        # Basic validation
        if not self.user_id or not self.items:
            return False
        for item in self.items:
            if 'item_id' not in item or 'quantity' not in item:
                return False
            if item.get('quantity', 0) <= 0:
                return False
        return True


class ProcessPaymentCommand(Command):
    """Command to process a payment."""
    
    command_type = "process_payment"
    
    def __init__(self, order_id: str, amount: float, payment_method: str):
        """Initialize the command.
        
        Args:
            order_id: The order ID
            amount: The payment amount
            payment_method: The payment method
        """
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
    
    def validate(self) -> bool:
        """Validate the command.
        
        Returns:
            True if the command is valid, False otherwise
        """
        # Basic validation
        if not self.order_id or not self.payment_method:
            return False
        if self.amount <= 0:
            return False
        return True


# Command handlers
class CommandHandler:
    """Base class for command handlers."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the command handler.
        
        Args:
            event_bus: The event bus for publishing events
        """
        self.event_bus = event_bus or EventBus()
    
    def handle(self, command: Command) -> bool:
        """Handle a command.
        
        Args:
            command: The command to handle
            
        Returns:
            True if the command was handled successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement handle()")


class CommandBus:
    """Routes commands to their appropriate handlers."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of CommandBus exists."""
        if cls._instance is None:
            cls._instance = super(CommandBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the command bus if not already initialized."""
        if self._initialized:
            return
            
        self._handlers = {}  # Command type to handler
        self._initialized = True
        logger.info("CommandBus initialized")
    
    def register_handler(self, command_type: str, handler: CommandHandler) -> None:
        """Register a handler for a command type.
        
        Args:
            command_type: The type of command
            handler: The handler for the command
        """
        self._handlers[command_type] = handler
        logger.debug(f"Handler registered for command type {command_type}")
    
    def dispatch(self, command: Command) -> bool:
        """Dispatch a command to its handler.
        
        Args:
            command: The command to dispatch
            
        Returns:
            True if the command was handled successfully, False otherwise
        """
        # Validate the command
        if not command.validate():
            logger.warning(f"Invalid command: {command.command_type}")
            return False
        
        # Find the appropriate handler
        handler = self._handlers.get(command.command_type)
        if not handler:
            logger.warning(f"No handler found for command type {command.command_type}")
            return False
        
        # Handle the command
        try:
            return handler.handle(command)
        except Exception as e:
            logger.error(f"Error handling command {command.command_type}: {e}")
            return False


# Query-related classes
class Query:
    """Base class for all queries in the system."""
    
    query_type: str = "query"


class GetUserQuery(Query):
    """Query to get a user by ID."""
    
    query_type = "get_user"
    
    def __init__(self, user_id: str):
        """Initialize the query.
        
        Args:
            user_id: The user ID
        """
        self.user_id = user_id


class GetUserByEmailQuery(Query):
    """Query to get a user by email."""
    
    query_type = "get_user_by_email"
    
    def __init__(self, email: str):
        """Initialize the query.
        
        Args:
            email: The user's email
        """
        self.email = email


class GetOrderQuery(Query):
    """Query to get an order by ID."""
    
    query_type = "get_order"
    
    def __init__(self, order_id: str):
        """Initialize the query.
        
        Args:
            order_id: The order ID
        """
        self.order_id = order_id


class GetUserOrdersQuery(Query):
    """Query to get all orders for a user."""
    
    query_type = "get_user_orders"
    
    def __init__(self, user_id: str):
        """Initialize the query.
        
        Args:
            user_id: The user ID
        """
        self.user_id = user_id


# Query handlers
class QueryHandler:
    """Base class for query handlers."""
    
    def handle(self, query: Query) -> Any:
        """Handle a query.
        
        Args:
            query: The query to handle
            
        Returns:
            The query result
        """
        raise NotImplementedError("Subclasses must implement handle()")


class QueryBus:
    """Routes queries to their appropriate handlers."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance of QueryBus exists."""
        if cls._instance is None:
            cls._instance = super(QueryBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the query bus if not already initialized."""
        if self._initialized:
            return
            
        self._handlers = {}  # Query type to handler
        self._initialized = True
        logger.info("QueryBus initialized")
    
    def register_handler(self, query_type: str, handler: QueryHandler) -> None:
        """Register a handler for a query type.
        
        Args:
            query_type: The type of query
            handler: The handler for the query
        """
        self._handlers[query_type] = handler
        logger.debug(f"Handler registered for query type {query_type}")
    
    def dispatch(self, query: Query) -> Any:
        """Dispatch a query to its handler.
        
        Args:
            query: The query to dispatch
            
        Returns:
            The query result
        """
        # Find the appropriate handler
        handler = self._handlers.get(query.query_type)
        if not handler:
            logger.warning(f"No handler found for query type {query.query_type}")
            return None
        
        # Handle the query
        try:
            return handler.handle(query)
        except Exception as e:
            logger.error(f"Error handling query {query.query_type}: {e}")
            return None


# Read model (optimized for queries)
class ReadModel:
    """Base class for read models in CQRS."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the read model.
        
        Args:
            event_bus: The event bus to subscribe to
        """
        self.event_bus = event_bus or EventBus()
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events for this read model."""
        pass


class UserReadModel(ReadModel):
    """Read model for user data."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the user read model.
        
        Args:
            event_bus: The event bus to subscribe to
        """
        super().__init__(event_bus)
        self.users_by_id = {}
        self.users_by_email = {}
        self.subscribe_to_events()
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events for this read model."""
        self.event_bus.subscribe("user.created", self.handle_user_created)
        self.event_bus.subscribe("user.updated", self.handle_user_updated)
    
    def handle_user_created(self, event: Event) -> None:
        """Handle user created events.
        
        Args:
            event: The user created event
        """
        data = event.get_event_data()
        user_id = data.get("user_id")
        email = data.get("email")
        
        user = {
            "user_id": user_id,
            "username": data.get("username"),
            "email": email,
            "created_at": event.timestamp.isoformat(),
            "status": "active"
        }
        
        self.users_by_id[user_id] = user
        self.users_by_email[email] = user
    
    def handle_user_updated(self, event: Event) -> None:
        """Handle user updated events.
        
        Args:
            event: The user updated event
        """
        data = event.get_event_data()
        user_id = data.get("user_id")
        updated_fields = data.get("updated_fields", {})
        
        if user_id in self.users_by_id:
            user = self.users_by_id[user_id]
            
            # Update the user
            for key, value in updated_fields.items():
                user[key] = value
            
            # If email was updated, update the email index
            if "email" in updated_fields:
                old_email = user.get("email")
                new_email = updated_fields["email"]
                
                if old_email in self.users_by_email:
                    del self.users_by_email[old_email]
                
                self.users_by_email[new_email] = user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user data or None if not found
        """
        return self.users_by_id.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email.
        
        Args:
            email: The user's email
            
        Returns:
            The user data or None if not found
        """
        return self.users_by_email.get(email)


class OrderReadModel(ReadModel):
    """Read model for order data."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize the order read model.
        
        Args:
            event_bus: The event bus to subscribe to
        """
        super().__init__(event_bus)
        self.orders_by_id = {}
        self.orders_by_user = {}  # User ID to list of order IDs
        self.subscribe_to_events()
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events for this read model."""
        self.event_bus.subscribe("order.created", self.handle_order_created)
        self.event_bus.subscribe("order.status_changed", self.handle_order_status_changed)
    
    def handle_order_created(self, event: Event) -> None:
        """Handle order created events.
        
        Args:
            event: The order created event
        """
        data = event.get_event_data()
        order_id = data.get("order_id")
        user_id = data.get("user_id")
        
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "items": data.get("items", []),
            "total_amount": data.get("total_amount", 0.0),
            "status": "pending",
            "created_at": event.timestamp.isoformat()
        }
        
        self.orders_by_id[order_id] = order
        
        # Add to user's orders
        if user_id not in self.orders_by_user:
            self.orders_by_user[user_id] = []
        self.orders_by_user[user_id].append(order_id)
    
    def handle_order_status_changed(self, event: Event) -> None:
        """Handle order status changed events.
        
        Args:
            event: The order status changed event
        """
        data = event.get_event_data()
        order_id = data.get("order_id")
        new_status = data.get("new_status")
        
        if order_id in self.orders_by_id:
            self.orders_by_id[order_id]["status"] = new_status
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get an order by ID.
        
        Args:
            order_id: The order ID
            
        Returns:
            The order data or None if not found
        """
        return self.orders_by_id.get(order_id)
    
    def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of order data for the user
        """
        order_ids = self.orders_by_user.get(user_id, [])
        return [self.orders_by_id[order_id] for order_id in order_ids if order_id in self.orders_by_id]


# Concrete command handlers
class UserCommandHandler(CommandHandler):
    """Handler for user-related commands."""
    
    def handle(self, command: Command) -> bool:
        """Handle a user command.
        
        Args:
            command: The command to handle
            
        Returns:
            True if the command was handled successfully, False otherwise
        """
        if isinstance(command, CreateUserCommand):
            from .events import UserCreatedEvent
            
            # Generate a user ID
            user_id = str(uuid4())
            
            # Create and publish the event
            event = UserCreatedEvent(
                user_id=user_id,
                username=command.username,
                email=command.email
            )
            self.event_bus.publish(event)
            
            logger.info(f"User created with ID: {user_id}")
            return True
        
        logger.warning(f"Unknown command type: {command.command_type}")
        return False


class OrderCommandHandler(CommandHandler):
    """Handler for order-related commands."""
    
    def handle(self, command: Command) -> bool:
        """Handle an order command.
        
        Args:
            command: The command to handle
            
        Returns:
            True if the command was handled successfully, False otherwise
        """
        if isinstance(command, CreateOrderCommand):
            from .events import OrderCreatedEvent
            
            # Generate an order ID
            order_id = str(uuid4())
            
            # Calculate total amount
            total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in command.items)
            
            # Create and publish the event
            event = OrderCreatedEvent(
                order_id=order_id,
                user_id=command.user_id,
                items=command.items,
                total_amount=total_amount
            )
            self.event_bus.publish(event)
            
            logger.info(f"Order created with ID: {order_id}")
            return True
        
        logger.warning(f"Unknown command type: {command.command_type}")
        return False


class PaymentCommandHandler(CommandHandler):
    """Handler for payment-related commands."""
    
    def handle(self, command: Command) -> bool:
        """Handle a payment command.
        
        Args:
            command: The command to handle
            
        Returns:
            True if the command was handled successfully, False otherwise
        """
        if isinstance(command, ProcessPaymentCommand):
            from .events import PaymentProcessedEvent, PaymentFailedEvent
            
            # Generate a payment ID
            payment_id = str(uuid4())
            
            # In a real system, this would call a payment gateway
            # Simulate a payment with a 90% success rate
            import random
            success = random.random() < 0.9
            
            if success:
                # Payment succeeded - publish success event
                event = PaymentProcessedEvent(
                    payment_id=payment_id,
                    order_id=command.order_id,
                    amount=command.amount,
                    status="processed",
                    payment_method=command.payment_method
                )
                self.event_bus.publish(event)
                
                logger.info(f"Payment processed: {payment_id}")
                return True
            else:
                # Payment failed - publish failure event
                event = PaymentFailedEvent(
                    payment_id=payment_id,
                    order_id=command.order_id,
                    amount=command.amount,
                    error_code="PAYMENT_REJECTED",
                    error_message="Payment was rejected by the payment processor"
                )
                self.event_bus.publish(event)
                
                logger.info(f"Payment failed: {payment_id}")
                return False
        
        logger.warning(f"Unknown command type: {command.command_type}")
        return False


# Concrete query handlers
class UserQueryHandler(QueryHandler):
    """Handler for user-related queries."""
    
    def __init__(self, read_model: UserReadModel):
        """Initialize the query handler.
        
        Args:
            read_model: The user read model
        """
        self.read_model = read_model
    
    def handle(self, query: Query) -> Any:
        """Handle a user query.
        
        Args:
            query: The query to handle
            
        Returns:
            The query result
        """
        if isinstance(query, GetUserQuery):
            return self.read_model.get_user_by_id(query.user_id)
        elif isinstance(query, GetUserByEmailQuery):
            return self.read_model.get_user_by_email(query.email)
        
        logger.warning(f"Unknown query type: {query.query_type}")
        return None


class OrderQueryHandler(QueryHandler):
    """Handler for order-related queries."""
    
    def __init__(self, read_model: OrderReadModel):
        """Initialize the query handler.
        
        Args:
            read_model: The order read model
        """
        self.read_model = read_model
    
    def handle(self, query: Query) -> Any:
        """Handle an order query.
        
        Args:
            query: The query to handle
            
        Returns:
            The query result
        """
        if isinstance(query, GetOrderQuery):
            return self.read_model.get_order_by_id(query.order_id)
        elif isinstance(query, GetUserOrdersQuery):
            return self.read_model.get_user_orders(query.user_id)
        
        logger.warning(f"Unknown query type: {query.query_type}")
        return None