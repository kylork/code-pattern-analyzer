#!/usr/bin/env python3
"""
Example Project Creator

This script generates an example project with a specified architectural style
that can be used to demonstrate and test the Code Pattern Analyzer.

Usage:
    python create_example_project.py --style layered --output ./examples/custom
"""

import os
import sys
import logging
import argparse
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Templates for different architectural styles
TEMPLATES = {
    "layered": {
        "description": "A classic three-tier architecture with UI, business logic, and data access layers",
        "structure": [
            # UI Layer
            {
                "path": "ui/controllers/UserController.py",
                "content": '''"""User Controller for handling user-related HTTP requests."""

from services.UserService import UserService

class UserController:
    """Handles HTTP requests related to users."""
    
    def __init__(self):
        """Initialize the controller with required services."""
        self.user_service = UserService()
    
    def get_user(self, user_id):
        """Get a user by ID."""
        return self.user_service.get_user_by_id(user_id)
    
    def create_user(self, user_data):
        """Create a new user."""
        return self.user_service.create_user(user_data)
    
    def update_user(self, user_id, user_data):
        """Update an existing user."""
        return self.user_service.update_user(user_id, user_data)
    
    def delete_user(self, user_id):
        """Delete a user by ID."""
        return self.user_service.delete_user(user_id)
'''
            },
            {
                "path": "ui/controllers/ProductController.py",
                "content": '''"""Product Controller for handling product-related HTTP requests."""

from services.ProductService import ProductService

class ProductController:
    """Handles HTTP requests related to products."""
    
    def __init__(self):
        """Initialize the controller with required services."""
        self.product_service = ProductService()
    
    def get_product(self, product_id):
        """Get a product by ID."""
        return self.product_service.get_product_by_id(product_id)
    
    def list_products(self, category=None):
        """Get a list of products, optionally filtered by category."""
        return self.product_service.list_products(category)
    
    def create_product(self, product_data):
        """Create a new product."""
        return self.product_service.create_product(product_data)
    
    def update_product(self, product_id, product_data):
        """Update an existing product."""
        return self.product_service.update_product(product_id, product_data)
    
    def delete_product(self, product_id):
        """Delete a product by ID."""
        return self.product_service.delete_product(product_id)
'''
            },
            {
                "path": "ui/views/UserView.py",
                "content": '''"""User view for rendering user-related pages."""

class UserView:
    """Renders user-related pages and forms."""
    
    def render_user_profile(self, user):
        """Render a user profile page."""
        # In a real app, this would use a template engine
        return f"<h1>{user.name}'s Profile</h1>"
    
    def render_user_form(self, user=None):
        """Render a user creation/edit form."""
        # In a real app, this would use a template engine
        if user:
            return f"<form><input name='name' value='{user.name}'></form>"
        return "<form><input name='name'></form>"
'''
            },
            {
                "path": "ui/views/ProductView.py",
                "content": '''"""Product view for rendering product-related pages."""

class ProductView:
    """Renders product-related pages and forms."""
    
    def render_product_details(self, product):
        """Render a product details page."""
        # In a real app, this would use a template engine
        return f"<h1>{product.name}</h1><p>{product.description}</p>"
    
    def render_product_list(self, products):
        """Render a list of products."""
        # In a real app, this would use a template engine
        return f"<h1>Products ({len(products)})</h1><ul>...</ul>"
    
    def render_product_form(self, product=None):
        """Render a product creation/edit form."""
        # In a real app, this would use a template engine
        if product:
            return f"<form><input name='name' value='{product.name}'></form>"
        return "<form><input name='name'></form>"
'''
            },
            # Business Logic Layer
            {
                "path": "services/UserService.py",
                "content": '''"""User service for business logic related to users."""

from repositories.UserRepository import UserRepository

class UserService:
    """Contains business logic for user operations."""
    
    def __init__(self):
        """Initialize the service with required repositories."""
        self.user_repository = UserRepository()
    
    def get_user_by_id(self, user_id):
        """Get a user by ID."""
        return self.user_repository.find_by_id(user_id)
    
    def create_user(self, user_data):
        """Create a new user."""
        # Validate user data
        if not user_data.get('name'):
            raise ValueError("User name is required")
        
        # Create user
        return self.user_repository.create(user_data)
    
    def update_user(self, user_id, user_data):
        """Update an existing user."""
        # Validate user exists
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User not found with ID: {user_id}")
        
        # Update user
        return self.user_repository.update(user_id, user_data)
    
    def delete_user(self, user_id):
        """Delete a user by ID."""
        return self.user_repository.delete(user_id)
'''
            },
            {
                "path": "services/ProductService.py",
                "content": '''"""Product service for business logic related to products."""

from repositories.ProductRepository import ProductRepository

class ProductService:
    """Contains business logic for product operations."""
    
    def __init__(self):
        """Initialize the service with required repositories."""
        self.product_repository = ProductRepository()
    
    def get_product_by_id(self, product_id):
        """Get a product by ID."""
        return self.product_repository.find_by_id(product_id)
    
    def list_products(self, category=None):
        """Get a list of products, optionally filtered by category."""
        if category:
            return self.product_repository.find_by_category(category)
        return self.product_repository.find_all()
    
    def create_product(self, product_data):
        """Create a new product."""
        # Validate product data
        if not product_data.get('name'):
            raise ValueError("Product name is required")
        if not product_data.get('price'):
            raise ValueError("Product price is required")
        
        # Create product
        return self.product_repository.create(product_data)
    
    def update_product(self, product_id, product_data):
        """Update an existing product."""
        # Validate product exists
        product = self.product_repository.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found with ID: {product_id}")
        
        # Update product
        return self.product_repository.update(product_id, product_data)
    
    def delete_product(self, product_id):
        """Delete a product by ID."""
        return self.product_repository.delete(product_id)
'''
            },
            # Data Access Layer
            {
                "path": "repositories/UserRepository.py",
                "content": '''"""User repository for data access related to users."""

from models.User import User

class UserRepository:
    """Handles database operations for users."""
    
    def __init__(self):
        """Initialize the repository."""
        # In a real app, this would be a database connection
        self.users = {}
        self.next_id = 1
    
    def find_by_id(self, user_id):
        """Find a user by ID."""
        return self.users.get(user_id)
    
    def find_by_email(self, email):
        """Find a user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def find_all(self):
        """Get all users."""
        return list(self.users.values())
    
    def create(self, user_data):
        """Create a new user."""
        user_id = self.next_id
        self.next_id += 1
        
        user = User(
            id=user_id,
            name=user_data.get('name'),
            email=user_data.get('email'),
            password=user_data.get('password')
        )
        
        self.users[user_id] = user
        return user
    
    def update(self, user_id, user_data):
        """Update an existing user."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        if 'name' in user_data:
            user.name = user_data['name']
        if 'email' in user_data:
            user.email = user_data['email']
        if 'password' in user_data:
            user.password = user_data['password']
        
        return user
    
    def delete(self, user_id):
        """Delete a user by ID."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
'''
            },
            {
                "path": "repositories/ProductRepository.py",
                "content": '''"""Product repository for data access related to products."""

from models.Product import Product

class ProductRepository:
    """Handles database operations for products."""
    
    def __init__(self):
        """Initialize the repository."""
        # In a real app, this would be a database connection
        self.products = {}
        self.next_id = 1
    
    def find_by_id(self, product_id):
        """Find a product by ID."""
        return self.products.get(product_id)
    
    def find_by_category(self, category):
        """Find products by category."""
        return [p for p in self.products.values() if p.category == category]
    
    def find_all(self):
        """Get all products."""
        return list(self.products.values())
    
    def create(self, product_data):
        """Create a new product."""
        product_id = self.next_id
        self.next_id += 1
        
        product = Product(
            id=product_id,
            name=product_data.get('name'),
            description=product_data.get('description'),
            price=product_data.get('price'),
            category=product_data.get('category')
        )
        
        self.products[product_id] = product
        return product
    
    def update(self, product_id, product_data):
        """Update an existing product."""
        product = self.products.get(product_id)
        if not product:
            return None
        
        if 'name' in product_data:
            product.name = product_data['name']
        if 'description' in product_data:
            product.description = product_data['description']
        if 'price' in product_data:
            product.price = product_data['price']
        if 'category' in product_data:
            product.category = product_data['category']
        
        return product
    
    def delete(self, product_id):
        """Delete a product by ID."""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
'''
            },
            # Domain Models
            {
                "path": "models/User.py",
                "content": '''"""User model representing a user in the system."""

class User:
    """Represents a user in the system."""
    
    def __init__(self, id, name, email, password):
        """Initialize a user with basic attributes."""
        self.id = id
        self.name = name
        self.email = email
        self.password = password  # In a real app, this would be hashed
    
    def __str__(self):
        """Return a string representation of the user."""
        return f"User(id={self.id}, name={self.name}, email={self.email})"
'''
            },
            {
                "path": "models/Product.py",
                "content": '''"""Product model representing a product in the system."""

class Product:
    """Represents a product in the system."""
    
    def __init__(self, id, name, description, price, category=None):
        """Initialize a product with basic attributes."""
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
    
    def __str__(self):
        """Return a string representation of the product."""
        return f"Product(id={self.id}, name={self.name}, price={self.price})"
'''
            },
            # Application entry point
            {
                "path": "app.py",
                "content": '''"""Main application entry point."""

from ui.controllers.UserController import UserController
from ui.controllers.ProductController import ProductController
from ui.views.UserView import UserView
from ui.views.ProductView import ProductView

class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application with controllers and views."""
        self.user_controller = UserController()
        self.product_controller = ProductController()
        self.user_view = UserView()
        self.product_view = ProductView()
    
    def run(self):
        """Run the application."""
        print("Starting layered architecture application...")
        
        # Create sample users and products
        user1 = self.user_controller.create_user({
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        user2 = self.user_controller.create_user({
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'password': 'password456'
        })
        
        product1 = self.product_controller.create_product({
            'name': 'Laptop',
            'description': 'A powerful laptop for development',
            'price': 1200.00,
            'category': 'Electronics'
        })
        
        product2 = self.product_controller.create_product({
            'name': 'Smartphone',
            'description': 'Latest smartphone with advanced features',
            'price': 800.00,
            'category': 'Electronics'
        })
        
        # Display users and products
        print("Users:")
        print(user1)
        print(user2)
        
        print("\nProducts:")
        print(product1)
        print(product2)
        
        print("\nApplication started successfully!")

if __name__ == "__main__":
    app = Application()
    app.run()
'''
            },
            # README file
            {
                "path": "README.md",
                "content": '''# Layered Architecture Example

This project demonstrates a classic three-tier layered architecture with:

1. **Presentation Layer (UI)** - Controllers and Views
2. **Business Logic Layer** - Services
3. **Data Access Layer** - Repositories and Models

## Structure

```
├── app.py                      # Application entry point
├── ui/                         # Presentation Layer
│   ├── controllers/            # Handle user input and HTTP requests
│   │   ├── UserController.py
│   │   └── ProductController.py
│   └── views/                  # Render data for presentation
│       ├── UserView.py
│       └── ProductView.py
├── services/                   # Business Logic Layer
│   ├── UserService.py
│   └── ProductService.py
├── repositories/               # Data Access Layer
│   ├── UserRepository.py
│   └── ProductRepository.py
└── models/                     # Domain Models
    ├── User.py
    └── Product.py
```

## Key Concepts

- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Direction**: Dependencies flow downward (UI → Business Logic → Data)
- **Layer Isolation**: Each layer only communicates with adjacent layers
- **Abstraction**: Higher layers don't know implementation details of lower layers

## Running the Example

```bash
python app.py
```

This will create sample users and products and display them in the console.
'''
            }
        ]
    },
    "hexagonal": {
        "description": "A hexagonal (ports and adapters) architecture with a core domain and adapter interfaces",
        "structure": [
            # Core domain
            {
                "path": "domain/models/User.py",
                "content": '''"""User entity in the domain."""

class User:
    """User entity in the domain."""
    
    def __init__(self, id, name, email):
        """Initialize a user with core attributes."""
        self.id = id
        self.name = name
        self.email = email
    
    def __str__(self):
        """Return a string representation of the user."""
        return f"User(id={self.id}, name={self.name}, email={self.email})"
'''
            },
            {
                "path": "domain/models/Product.py",
                "content": '''"""Product entity in the domain."""

class Product:
    """Product entity in the domain."""
    
    def __init__(self, id, name, price):
        """Initialize a product with core attributes."""
        self.id = id
        self.name = name
        self.price = price
    
    def __str__(self):
        """Return a string representation of the product."""
        return f"Product(id={self.id}, name={self.name}, price={self.price})"
'''
            },
            {
                "path": "domain/services/UserService.py",
                "content": '''"""Core domain service for user operations."""

class UserService:
    """Core domain service for user operations."""
    
    def __init__(self, user_repository):
        """Initialize with a user repository."""
        self.user_repository = user_repository
    
    def get_user(self, user_id):
        """Get a user by ID."""
        return self.user_repository.get_user(user_id)
    
    def create_user(self, name, email):
        """Create a new user."""
        if not name or not email:
            raise ValueError("Name and email are required")
        
        return self.user_repository.create_user(name, email)
    
    def update_user(self, user_id, name=None, email=None):
        """Update a user."""
        user = self.user_repository.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        if name:
            user.name = name
        if email:
            user.email = email
        
        return self.user_repository.update_user(user)
    
    def delete_user(self, user_id):
        """Delete a user."""
        return self.user_repository.delete_user(user_id)
'''
            },
            {
                "path": "domain/services/ProductService.py",
                "content": '''"""Core domain service for product operations."""

class ProductService:
    """Core domain service for product operations."""
    
    def __init__(self, product_repository):
        """Initialize with a product repository."""
        self.product_repository = product_repository
    
    def get_product(self, product_id):
        """Get a product by ID."""
        return self.product_repository.get_product(product_id)
    
    def list_products(self):
        """List all products."""
        return self.product_repository.list_products()
    
    def create_product(self, name, price):
        """Create a new product."""
        if not name:
            raise ValueError("Product name is required")
        if price <= 0:
            raise ValueError("Price must be positive")
        
        return self.product_repository.create_product(name, price)
    
    def update_product(self, product_id, name=None, price=None):
        """Update a product."""
        product = self.product_repository.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        if name:
            product.name = name
        if price is not None:
            if price <= 0:
                raise ValueError("Price must be positive")
            product.price = price
        
        return self.product_repository.update_product(product)
    
    def delete_product(self, product_id):
        """Delete a product."""
        return self.product_repository.delete_product(product_id)
'''
            },
            # Port interfaces
            {
                "path": "domain/ports/UserRepositoryPort.py",
                "content": '''"""Port interface for user repository."""

from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    """Port interface for user repository."""
    
    @abstractmethod
    def get_user(self, user_id):
        """Get a user by ID."""
        pass
    
    @abstractmethod
    def create_user(self, name, email):
        """Create a new user."""
        pass
    
    @abstractmethod
    def update_user(self, user):
        """Update a user."""
        pass
    
    @abstractmethod
    def delete_user(self, user_id):
        """Delete a user."""
        pass
'''
            },
            {
                "path": "domain/ports/ProductRepositoryPort.py",
                "content": '''"""Port interface for product repository."""

from abc import ABC, abstractmethod

class ProductRepositoryPort(ABC):
    """Port interface for product repository."""
    
    @abstractmethod
    def get_product(self, product_id):
        """Get a product by ID."""
        pass
    
    @abstractmethod
    def list_products(self):
        """List all products."""
        pass
    
    @abstractmethod
    def create_product(self, name, price):
        """Create a new product."""
        pass
    
    @abstractmethod
    def update_product(self, product):
        """Update a product."""
        pass
    
    @abstractmethod
    def delete_product(self, product_id):
        """Delete a product."""
        pass
'''
            },
            {
                "path": "domain/ports/UserServicePort.py",
                "content": '''"""Port interface for user service."""

from abc import ABC, abstractmethod

class UserServicePort(ABC):
    """Port interface for user service."""
    
    @abstractmethod
    def get_user(self, user_id):
        """Get a user by ID."""
        pass
    
    @abstractmethod
    def create_user(self, name, email):
        """Create a new user."""
        pass
    
    @abstractmethod
    def update_user(self, user_id, name=None, email=None):
        """Update a user."""
        pass
    
    @abstractmethod
    def delete_user(self, user_id):
        """Delete a user."""
        pass
'''
            },
            {
                "path": "domain/ports/ProductServicePort.py",
                "content": '''"""Port interface for product service."""

from abc import ABC, abstractmethod

class ProductServicePort(ABC):
    """Port interface for product service."""
    
    @abstractmethod
    def get_product(self, product_id):
        """Get a product by ID."""
        pass
    
    @abstractmethod
    def list_products(self):
        """List all products."""
        pass
    
    @abstractmethod
    def create_product(self, name, price):
        """Create a new product."""
        pass
    
    @abstractmethod
    def update_product(self, product_id, name=None, price=None):
        """Update a product."""
        pass
    
    @abstractmethod
    def delete_product(self, product_id):
        """Delete a product."""
        pass
'''
            },
            # Adapters - Infrastructure
            {
                "path": "adapters/repositories/InMemoryUserRepository.py",
                "content": '''"""In-memory implementation of user repository."""

from domain.models.User import User
from domain.ports.UserRepositoryPort import UserRepositoryPort

class InMemoryUserRepository(UserRepositoryPort):
    """In-memory implementation of user repository."""
    
    def __init__(self):
        """Initialize the repository."""
        self.users = {}
        self.next_id = 1
    
    def get_user(self, user_id):
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def create_user(self, name, email):
        """Create a new user."""
        user_id = self.next_id
        self.next_id += 1
        
        user = User(id=user_id, name=name, email=email)
        self.users[user_id] = user
        
        return user
    
    def update_user(self, user):
        """Update a user."""
        if user.id not in self.users:
            return None
        
        self.users[user.id] = user
        return user
    
    def delete_user(self, user_id):
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
'''
            },
            {
                "path": "adapters/repositories/InMemoryProductRepository.py",
                "content": '''"""In-memory implementation of product repository."""

from domain.models.Product import Product
from domain.ports.ProductRepositoryPort import ProductRepositoryPort

class InMemoryProductRepository(ProductRepositoryPort):
    """In-memory implementation of product repository."""
    
    def __init__(self):
        """Initialize the repository."""
        self.products = {}
        self.next_id = 1
    
    def get_product(self, product_id):
        """Get a product by ID."""
        return self.products.get(product_id)
    
    def list_products(self):
        """List all products."""
        return list(self.products.values())
    
    def create_product(self, name, price):
        """Create a new product."""
        product_id = self.next_id
        self.next_id += 1
        
        product = Product(id=product_id, name=name, price=price)
        self.products[product_id] = product
        
        return product
    
    def update_product(self, product):
        """Update a product."""
        if product.id not in self.products:
            return None
        
        self.products[product.id] = product
        return product
    
    def delete_product(self, product_id):
        """Delete a product."""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
'''
            },
            # Adapters - Web
            {
                "path": "adapters/controllers/UserController.py",
                "content": '''"""Web controller for user endpoints."""

class UserController:
    """Web controller for user endpoints."""
    
    def __init__(self, user_service):
        """Initialize with a user service."""
        self.user_service = user_service
    
    def get_user(self, user_id):
        """HTTP handler for GET /users/{id}."""
        try:
            user = self.user_service.get_user(user_id)
            if user:
                return {"status": "success", "data": {"id": user.id, "name": user.name, "email": user.email}}
            return {"status": "error", "message": "User not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_user(self, payload):
        """HTTP handler for POST /users."""
        try:
            name = payload.get("name")
            email = payload.get("email")
            
            user = self.user_service.create_user(name, email)
            return {"status": "success", "data": {"id": user.id, "name": user.name, "email": user.email}}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def update_user(self, user_id, payload):
        """HTTP handler for PUT /users/{id}."""
        try:
            name = payload.get("name")
            email = payload.get("email")
            
            user = self.user_service.update_user(user_id, name, email)
            return {"status": "success", "data": {"id": user.id, "name": user.name, "email": user.email}}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_user(self, user_id):
        """HTTP handler for DELETE /users/{id}."""
        try:
            success = self.user_service.delete_user(user_id)
            if success:
                return {"status": "success", "message": "User deleted"}
            return {"status": "error", "message": "User not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
'''
            },
            {
                "path": "adapters/controllers/ProductController.py",
                "content": '''"""Web controller for product endpoints."""

class ProductController:
    """Web controller for product endpoints."""
    
    def __init__(self, product_service):
        """Initialize with a product service."""
        self.product_service = product_service
    
    def get_product(self, product_id):
        """HTTP handler for GET /products/{id}."""
        try:
            product = self.product_service.get_product(product_id)
            if product:
                return {"status": "success", "data": {"id": product.id, "name": product.name, "price": product.price}}
            return {"status": "error", "message": "Product not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_products(self):
        """HTTP handler for GET /products."""
        try:
            products = self.product_service.list_products()
            return {
                "status": "success", 
                "data": [{"id": p.id, "name": p.name, "price": p.price} for p in products]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_product(self, payload):
        """HTTP handler for POST /products."""
        try:
            name = payload.get("name")
            price = payload.get("price")
            
            product = self.product_service.create_product(name, price)
            return {"status": "success", "data": {"id": product.id, "name": product.name, "price": product.price}}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def update_product(self, product_id, payload):
        """HTTP handler for PUT /products/{id}."""
        try:
            name = payload.get("name")
            price = payload.get("price")
            
            product = self.product_service.update_product(product_id, name, price)
            return {"status": "success", "data": {"id": product.id, "name": product.name, "price": product.price}}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_product(self, product_id):
        """HTTP handler for DELETE /products/{id}."""
        try:
            success = self.product_service.delete_product(product_id)
            if success:
                return {"status": "success", "message": "Product deleted"}
            return {"status": "error", "message": "Product not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
'''
            },
            # Application
            {
                "path": "app.py",
                "content": '''"""Main application entry point."""

# Domain
from domain.services.UserService import UserService
from domain.services.ProductService import ProductService

# Adapters
from adapters.repositories.InMemoryUserRepository import InMemoryUserRepository
from adapters.repositories.InMemoryProductRepository import InMemoryProductRepository
from adapters.controllers.UserController import UserController
from adapters.controllers.ProductController import ProductController

class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application with ports and adapters."""
        # Repositories (driven adapters)
        self.user_repository = InMemoryUserRepository()
        self.product_repository = InMemoryProductRepository()
        
        # Domain services
        self.user_service = UserService(self.user_repository)
        self.product_service = ProductService(self.product_repository)
        
        # Controllers (driving adapters)
        self.user_controller = UserController(self.user_service)
        self.product_controller = ProductController(self.product_service)
    
    def run(self):
        """Run the application."""
        print("Starting hexagonal architecture application...")
        
        # Simulate API calls
        print("\n--- Creating users ---")
        create_john = self.user_controller.create_user({"name": "John Doe", "email": "john@example.com"})
        print(f"POST /users: {create_john}")
        
        create_jane = self.user_controller.create_user({"name": "Jane Smith", "email": "jane@example.com"})
        print(f"POST /users: {create_jane}")
        
        print("\n--- Creating products ---")
        create_laptop = self.product_controller.create_product({"name": "Laptop", "price": 1200.00})
        print(f"POST /products: {create_laptop}")
        
        create_phone = self.product_controller.create_product({"name": "Smartphone", "price": 800.00})
        print(f"POST /products: {create_phone}")
        
        print("\n--- Getting users ---")
        get_john = self.user_controller.get_user(1)
        print(f"GET /users/1: {get_john}")
        
        print("\n--- Getting products ---")
        get_products = self.product_controller.list_products()
        print(f"GET /products: {get_products}")
        
        print("\n--- Updating user ---")
        update_john = self.user_controller.update_user(1, {"name": "John Updated", "email": "john_new@example.com"})
        print(f"PUT /users/1: {update_john}")
        
        print("\n--- Deleting product ---")
        delete_product = self.product_controller.delete_product(1)
        print(f"DELETE /products/1: {delete_product}")
        
        print("\n--- Final product list ---")
        final_products = self.product_controller.list_products()
        print(f"GET /products: {final_products}")
        
        print("\nApplication finished successfully!")

if __name__ == "__main__":
    app = Application()
    app.run()
'''
            },
            # README file
            {
                "path": "README.md",
                "content": '''# Hexagonal Architecture Example

This project demonstrates a hexagonal (ports and adapters) architecture with:

1. **Domain Core** - Models and Services
2. **Ports** - Interface definitions for adapters
3. **Adapters** - Implementation of ports for different contexts

## Structure

```
├── app.py                              # Application entry point
├── domain/                             # Domain core
│   ├── models/                         # Domain entities
│   │   ├── User.py
│   │   └── Product.py
│   ├── services/                       # Domain services
│   │   ├── UserService.py
│   │   └── ProductService.py
│   └── ports/                          # Port interfaces
│       ├── UserRepositoryPort.py       # Driven ports
│       ├── ProductRepositoryPort.py
│       ├── UserServicePort.py          # Driving ports
│       └── ProductServicePort.py
└── adapters/                           # Adapters
    ├── repositories/                   # Driven adapters
    │   ├── InMemoryUserRepository.py
    │   └── InMemoryProductRepository.py
    └── controllers/                    # Driving adapters
        ├── UserController.py
        └── ProductController.py
```

## Key Concepts

- **Domain Independence**: The core domain is completely isolated from external concerns
- **Ports as Interfaces**: Domain defines interfaces (ports) that adapters must implement
- **Inversion of Control**: Domain depends on abstractions, not concrete implementations
- **Testability**: Each component can be tested in isolation
- **Flexibility**: Easy to swap out adapters (e.g., change from in-memory to database repository)

## Running the Example

```bash
python app.py
```

This will simulate a series of API calls to the application and display the results.
'''
            }
        ]
    },
    "clean": {
        "description": "Clean architecture with entities, use cases, interfaces, and frameworks layers",
        "structure": [
            # Entities layer
            {
                "path": "entities/User.py",
                "content": '''"""User entity in the domain."""

class User:
    """Core user entity."""
    
    def __init__(self, id, name, email):
        """Initialize a user with core attributes."""
        self.id = id
        self.name = name
        self.email = email
    
    def validate(self):
        """Validate user data."""
        if not self.name or not self.email:
            return False
            
        # Basic email format validation
        if '@' not in self.email:
            return False
            
        return True
    
    def __str__(self):
        """Return a string representation of the user."""
        return f"User(id={self.id}, name={self.name}, email={self.email})"
'''
            },
            {
                "path": "entities/Product.py",
                "content": '''"""Product entity in the domain."""

class Product:
    """Core product entity."""
    
    def __init__(self, id, name, price, category=None):
        """Initialize a product with core attributes."""
        self.id = id
        self.name = name
        self.price = price
        self.category = category
    
    def validate(self):
        """Validate product data."""
        if not self.name:
            return False
            
        if self.price is None or self.price < 0:
            return False
            
        return True
    
    def __str__(self):
        """Return a string representation of the product."""
        return f"Product(id={self.id}, name={self.name}, price={self.price})"
'''
            },
            # Use case layer
            {
                "path": "use_cases/user_use_cases.py",
                "content": '''"""Use cases for user operations."""

class CreateUserUseCase:
    """Use case for creating a user."""
    
    def __init__(self, user_repository):
        """Initialize with a user repository."""
        self.user_repository = user_repository
    
    def execute(self, name, email):
        """Execute the use case."""
        from entities.User import User
        
        # Create and validate user
        user = User(id=None, name=name, email=email)
        if not user.validate():
            raise ValueError("Invalid user data")
        
        # Store user
        return self.user_repository.create(user)


class GetUserUseCase:
    """Use case for getting a user."""
    
    def __init__(self, user_repository):
        """Initialize with a user repository."""
        self.user_repository = user_repository
    
    def execute(self, user_id):
        """Execute the use case."""
        return self.user_repository.get_by_id(user_id)


class UpdateUserUseCase:
    """Use case for updating a user."""
    
    def __init__(self, user_repository):
        """Initialize with a user repository."""
        self.user_repository = user_repository
    
    def execute(self, user_id, name=None, email=None):
        """Execute the use case."""
        # Get existing user
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        # Update user attributes
        if name:
            user.name = name
        if email:
            user.email = email
        
        # Validate updated user
        if not user.validate():
            raise ValueError("Invalid user data")
        
        # Store updated user
        return self.user_repository.update(user)


class DeleteUserUseCase:
    """Use case for deleting a user."""
    
    def __init__(self, user_repository):
        """Initialize with a user repository."""
        self.user_repository = user_repository
    
    def execute(self, user_id):
        """Execute the use case."""
        return self.user_repository.delete(user_id)
'''
            },
            {
                "path": "use_cases/product_use_cases.py",
                "content": '''"""Use cases for product operations."""

class CreateProductUseCase:
    """Use case for creating a product."""
    
    def __init__(self, product_repository):
        """Initialize with a product repository."""
        self.product_repository = product_repository
    
    def execute(self, name, price, category=None):
        """Execute the use case."""
        from entities.Product import Product
        
        # Create and validate product
        product = Product(id=None, name=name, price=price, category=category)
        if not product.validate():
            raise ValueError("Invalid product data")
        
        # Store product
        return self.product_repository.create(product)


class GetProductUseCase:
    """Use case for getting a product."""
    
    def __init__(self, product_repository):
        """Initialize with a product repository."""
        self.product_repository = product_repository
    
    def execute(self, product_id):
        """Execute the use case."""
        return self.product_repository.get_by_id(product_id)


class ListProductsUseCase:
    """Use case for listing products."""
    
    def __init__(self, product_repository):
        """Initialize with a product repository."""
        self.product_repository = product_repository
    
    def execute(self, category=None):
        """Execute the use case."""
        if category:
            return self.product_repository.get_by_category(category)
        return self.product_repository.get_all()


class UpdateProductUseCase:
    """Use case for updating a product."""
    
    def __init__(self, product_repository):
        """Initialize with a product repository."""
        self.product_repository = product_repository
    
    def execute(self, product_id, name=None, price=None, category=None):
        """Execute the use case."""
        # Get existing product
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Update product attributes
        if name:
            product.name = name
        if price is not None:
            product.price = price
        if category is not None:
            product.category = category
        
        # Validate updated product
        if not product.validate():
            raise ValueError("Invalid product data")
        
        # Store updated product
        return self.product_repository.update(product)


class DeleteProductUseCase:
    """Use case for deleting a product."""
    
    def __init__(self, product_repository):
        """Initialize with a product repository."""
        self.product_repository = product_repository
    
    def execute(self, product_id):
        """Execute the use case."""
        return self.product_repository.delete(product_id)
'''
            },
            # Interface adapters layer
            {
                "path": "interface_adapters/repositories/user_repository_interface.py",
                "content": '''"""Interface for user repository."""

from abc import ABC, abstractmethod

class UserRepositoryInterface(ABC):
    """Interface for user repository."""
    
    @abstractmethod
    def get_by_id(self, user_id):
        """Get a user by ID."""
        pass
    
    @abstractmethod
    def get_by_email(self, email):
        """Get a user by email."""
        pass
    
    @abstractmethod
    def get_all(self):
        """Get all users."""
        pass
    
    @abstractmethod
    def create(self, user):
        """Create a new user."""
        pass
    
    @abstractmethod
    def update(self, user):
        """Update a user."""
        pass
    
    @abstractmethod
    def delete(self, user_id):
        """Delete a user."""
        pass
'''
            },
            {
                "path": "interface_adapters/repositories/product_repository_interface.py",
                "content": '''"""Interface for product repository."""

from abc import ABC, abstractmethod

class ProductRepositoryInterface(ABC):
    """Interface for product repository."""
    
    @abstractmethod
    def get_by_id(self, product_id):
        """Get a product by ID."""
        pass
    
    @abstractmethod
    def get_by_category(self, category):
        """Get products by category."""
        pass
    
    @abstractmethod
    def get_all(self):
        """Get all products."""
        pass
    
    @abstractmethod
    def create(self, product):
        """Create a new product."""
        pass
    
    @abstractmethod
    def update(self, product):
        """Update a product."""
        pass
    
    @abstractmethod
    def delete(self, product_id):
        """Delete a product."""
        pass
'''
            },
            {
                "path": "interface_adapters/controllers/user_controller.py",
                "content": '''"""Controller for user endpoints."""

from use_cases.user_use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    UpdateUserUseCase,
    DeleteUserUseCase
)

class UserController:
    """Controller for user endpoints."""
    
    def __init__(self, user_repository):
        """Initialize with required repositories."""
        self.user_repository = user_repository
        
        # Initialize use cases
        self.create_user_use_case = CreateUserUseCase(user_repository)
        self.get_user_use_case = GetUserUseCase(user_repository)
        self.update_user_use_case = UpdateUserUseCase(user_repository)
        self.delete_user_use_case = DeleteUserUseCase(user_repository)
    
    def create_user(self, request_data):
        """Handle create user request."""
        try:
            name = request_data.get('name')
            email = request_data.get('email')
            
            if not name or not email:
                return {'success': False, 'error': 'Name and email are required'}
            
            user = self.create_user_use_case.execute(name, email)
            
            return {
                'success': True,
                'data': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            }
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def get_user(self, user_id):
        """Handle get user request."""
        try:
            user = self.get_user_use_case.execute(user_id)
            
            if not user:
                return {'success': False, 'error': f'User not found: {user_id}'}
            
            return {
                'success': True,
                'data': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def update_user(self, user_id, request_data):
        """Handle update user request."""
        try:
            name = request_data.get('name')
            email = request_data.get('email')
            
            user = self.update_user_use_case.execute(user_id, name, email)
            
            return {
                'success': True,
                'data': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            }
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def delete_user(self, user_id):
        """Handle delete user request."""
        try:
            success = self.delete_user_use_case.execute(user_id)
            
            if not success:
                return {'success': False, 'error': f'User not found: {user_id}'}
            
            return {'success': True, 'message': f'User {user_id} deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
'''
            },
            {
                "path": "interface_adapters/controllers/product_controller.py",
                "content": '''"""Controller for product endpoints."""

from use_cases.product_use_cases import (
    CreateProductUseCase,
    GetProductUseCase,
    ListProductsUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase
)

class ProductController:
    """Controller for product endpoints."""
    
    def __init__(self, product_repository):
        """Initialize with required repositories."""
        self.product_repository = product_repository
        
        # Initialize use cases
        self.create_product_use_case = CreateProductUseCase(product_repository)
        self.get_product_use_case = GetProductUseCase(product_repository)
        self.list_products_use_case = ListProductsUseCase(product_repository)
        self.update_product_use_case = UpdateProductUseCase(product_repository)
        self.delete_product_use_case = DeleteProductUseCase(product_repository)
    
    def create_product(self, request_data):
        """Handle create product request."""
        try:
            name = request_data.get('name')
            price = request_data.get('price')
            category = request_data.get('category')
            
            if not name or price is None:
                return {'success': False, 'error': 'Name and price are required'}
            
            product = self.create_product_use_case.execute(name, price, category)
            
            return {
                'success': True,
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'category': product.category
                }
            }
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def get_product(self, product_id):
        """Handle get product request."""
        try:
            product = self.get_product_use_case.execute(product_id)
            
            if not product:
                return {'success': False, 'error': f'Product not found: {product_id}'}
            
            return {
                'success': True,
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'category': product.category
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def list_products(self, category=None):
        """Handle list products request."""
        try:
            products = self.list_products_use_case.execute(category)
            
            return {
                'success': True,
                'data': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'price': p.price,
                        'category': p.category
                    } for p in products
                ]
            }
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def update_product(self, product_id, request_data):
        """Handle update product request."""
        try:
            name = request_data.get('name')
            price = request_data.get('price')
            category = request_data.get('category')
            
            product = self.update_product_use_case.execute(
                product_id, name, price, category
            )
            
            return {
                'success': True,
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'category': product.category
                }
            }
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
    
    def delete_product(self, product_id):
        """Handle delete product request."""
        try:
            success = self.delete_product_use_case.execute(product_id)
            
            if not success:
                return {'success': False, 'error': f'Product not found: {product_id}'}
            
            return {'success': True, 'message': f'Product {product_id} deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {e}'}
'''
            },
            # Frameworks layer
            {
                "path": "frameworks/db/memory/memory_user_repository.py",
                "content": '''"""In-memory implementation of user repository."""

from interface_adapters.repositories.user_repository_interface import UserRepositoryInterface

class MemoryUserRepository(UserRepositoryInterface):
    """In-memory implementation of user repository."""
    
    def __init__(self):
        """Initialize repository."""
        self.users = {}
        self.next_id = 1
    
    def get_by_id(self, user_id):
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def get_by_email(self, email):
        """Get a user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_all(self):
        """Get all users."""
        return list(self.users.values())
    
    def create(self, user):
        """Create a new user."""
        # Assign ID
        user.id = self.next_id
        self.next_id += 1
        
        # Store user
        self.users[user.id] = user
        return user
    
    def update(self, user):
        """Update a user."""
        if user.id not in self.users:
            return None
            
        self.users[user.id] = user
        return user
    
    def delete(self, user_id):
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
'''
            },
            {
                "path": "frameworks/db/memory/memory_product_repository.py",
                "content": '''"""In-memory implementation of product repository."""

from interface_adapters.repositories.product_repository_interface import ProductRepositoryInterface

class MemoryProductRepository(ProductRepositoryInterface):
    """In-memory implementation of product repository."""
    
    def __init__(self):
        """Initialize repository."""
        self.products = {}
        self.next_id = 1
    
    def get_by_id(self, product_id):
        """Get a product by ID."""
        return self.products.get(product_id)
    
    def get_by_category(self, category):
        """Get products by category."""
        return [p for p in self.products.values() if p.category == category]
    
    def get_all(self):
        """Get all products."""
        return list(self.products.values())
    
    def create(self, product):
        """Create a new product."""
        # Assign ID
        product.id = self.next_id
        self.next_id += 1
        
        # Store product
        self.products[product.id] = product
        return product
    
    def update(self, product):
        """Update a product."""
        if product.id not in self.products:
            return None
            
        self.products[product.id] = product
        return product
    
    def delete(self, product_id):
        """Delete a product."""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
'''
            },
            {
                "path": "frameworks/web/api_app.py",
                "content": '''"""API application using the clean architecture."""

from interface_adapters.controllers.user_controller import UserController
from interface_adapters.controllers.product_controller import ProductController
from frameworks.db.memory.memory_user_repository import MemoryUserRepository
from frameworks.db.memory.memory_product_repository import MemoryProductRepository

class ApiApp:
    """Simple API application."""
    
    def __init__(self):
        """Initialize application."""
        # Initialize repositories
        self.user_repository = MemoryUserRepository()
        self.product_repository = MemoryProductRepository()
        
        # Initialize controllers
        self.user_controller = UserController(self.user_repository)
        self.product_controller = ProductController(self.product_repository)
    
    def run(self):
        """Run the application."""
        print("Starting clean architecture API application...")
        
        # Simulate API requests
        
        # Create users
        print("\n--- Creating users ---")
        print("POST /api/users")
        result1 = self.user_controller.create_user({
            'name': 'John Doe',
            'email': 'john@example.com'
        })
        print(f"Response: {result1}")
        
        print("\nPOST /api/users")
        result2 = self.user_controller.create_user({
            'name': 'Jane Smith',
            'email': 'jane@example.com'
        })
        print(f"Response: {result2}")
        
        # Create products
        print("\n--- Creating products ---")
        print("POST /api/products")
        result3 = self.product_controller.create_product({
            'name': 'Laptop',
            'price': 1200.00,
            'category': 'Electronics'
        })
        print(f"Response: {result3}")
        
        print("\nPOST /api/products")
        result4 = self.product_controller.create_product({
            'name': 'Smartphone',
            'price': 800.00,
            'category': 'Electronics'
        })
        print(f"Response: {result4}")
        
        # Get user
        print("\n--- Getting user ---")
        print("GET /api/users/1")
        result5 = self.user_controller.get_user(1)
        print(f"Response: {result5}")
        
        # Get product
        print("\n--- Getting product ---")
        print("GET /api/products/1")
        result6 = self.product_controller.get_product(1)
        print(f"Response: {result6}")
        
        # List products
        print("\n--- Listing products ---")
        print("GET /api/products")
        result7 = self.product_controller.list_products()
        print(f"Response: {result7}")
        
        # Update user
        print("\n--- Updating user ---")
        print("PUT /api/users/1")
        result8 = self.user_controller.update_user(1, {
            'name': 'John Updated',
            'email': 'john_new@example.com'
        })
        print(f"Response: {result8}")
        
        # Delete product
        print("\n--- Deleting product ---")
        print("DELETE /api/products/1")
        result9 = self.product_controller.delete_product(1)
        print(f"Response: {result9}")
        
        # Get updated user
        print("\n--- Getting updated user ---")
        print("GET /api/users/1")
        result10 = self.user_controller.get_user(1)
        print(f"Response: {result10}")
        
        # List products after deletion
        print("\n--- Listing products after deletion ---")
        print("GET /api/products")
        result11 = self.product_controller.list_products()
        print(f"Response: {result11}")
        
        print("\nApplication finished successfully!")
'''
            },
            # Main application file
            {
                "path": "app.py",
                "content": '''"""Main application entry point."""

from frameworks.web.api_app import ApiApp

if __name__ == "__main__":
    app = ApiApp()
    app.run()
'''
            },
            # README file
            {
                "path": "README.md",
                "content": '''# Clean Architecture Example

This project demonstrates Clean Architecture with:

1. **Entities Layer** - Core business models and rules
2. **Use Cases Layer** - Application-specific business rules
3. **Interface Adapters Layer** - Interfaces, controllers, presenters
4. **Frameworks & Drivers Layer** - External frameworks and tools

## Structure

```
├── app.py                                          # Main application entry point
├── entities/                                       # Entities Layer
│   ├── User.py
│   └── Product.py
├── use_cases/                                      # Use Cases Layer
│   ├── user_use_cases.py
│   └── product_use_cases.py
├── interface_adapters/                             # Interface Adapters Layer
│   ├── controllers/
│   │   ├── user_controller.py
│   │   └── product_controller.py
│   └── repositories/
│       ├── user_repository_interface.py
│       └── product_repository_interface.py
└── frameworks/                                     # Frameworks & Drivers Layer
    ├── db/
    │   └── memory/
    │       ├── memory_user_repository.py
    │       └── memory_product_repository.py
    └── web/
        └── api_app.py
```

## Key Concepts

- **Dependency Rule**: Dependencies only point inward, toward higher-level policies
- **Entities**: Contain enterprise-wide business rules
- **Use Cases**: Contain application-specific business rules
- **Interface Adapters**: Convert data between use cases and external formats
- **Frameworks & Drivers**: Interact with external systems and frameworks

## Running the Example

```bash
python app.py
```

This will simulate a series of API calls and display the results.
'''
            }
        ]
    }
}

def create_example_project(style, output_dir):
    """Create an example project with the specified architectural style.
    
    Args:
        style: Architectural style to use
        output_dir: Output directory to create the project in
    
    Returns:
        Path to the created project
    """
    if style not in TEMPLATES:
        raise ValueError(f"Unknown architectural style: {style}")
        
    template = TEMPLATES[style]
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Creating {style} architecture example in {output_path}")
    
    # Create files
    for file_info in template["structure"]:
        file_path = output_path / file_info["path"]
        
        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file content
        with open(file_path, "w") as f:
            f.write(file_info["content"])
            
        logger.info(f"Created {file_path}")
    
    return output_path

def main():
    parser = argparse.ArgumentParser(
        description="Create example projects with specific architectural styles"
    )
    
    parser.add_argument(
        "--style",
        choices=list(TEMPLATES.keys()),
        default="layered",
        help="Architectural style to use"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./examples/generated",
        help="Output directory to create the project in"
    )
    
    args = parser.parse_args()
    
    try:
        output_path = create_example_project(args.style, args.output)
        print(f"\nExample project created successfully at: {output_path}")
        print(f"Architectural style: {args.style}")
        print(f"Description: {TEMPLATES[args.style]['description']}")
        print("\nTo run the example:")
        print(f"cd {output_path} && python app.py")
    except Exception as e:
        logger.error(f"Error creating example project: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())