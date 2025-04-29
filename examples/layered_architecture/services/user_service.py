"""
User service implementation.

This module provides business logic for user-related operations.
"""

import hashlib
import os
from ..models.user import User
from ..repositories.user_repository import UserRepository

class UserService:
    """Service for user business logic."""
    
    def __init__(self, user_repository=None):
        """Initialize the service with a user repository.
        
        Args:
            user_repository: Repository for user data access
        """
        self.repository = user_repository or UserRepository()
    
    def register_user(self, username, email, password, first_name=None, last_name=None):
        """Register a new user.
        
        Args:
            username: User's login name
            email: User's email address
            password: User's password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Newly created User object
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username or email already exists
        if self.repository.find_by_username(username):
            raise ValueError(f"Username '{username}' is already taken")
        
        if self.repository.find_by_email(email):
            raise ValueError(f"Email '{email}' is already registered")
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Hash the password
        password_hash = self._hash_password(password)
        user.set_password(password_hash)
        
        # Save and return the user
        return self.repository.save(user)
    
    def authenticate(self, username, password):
        """Authenticate a user with username and password.
        
        Args:
            username: User's login name
            password: User's password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = self.repository.find_by_username(username)
        if not user:
            return None
        
        password_hash = self._hash_password(password)
        if user.verify_password(password_hash):
            return user
        
        return None
    
    def get_user(self, user_id):
        """Get a user by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            User object or None if not found
        """
        return self.repository.find_by_id(user_id)
    
    def update_user(self, user_id, **kwargs):
        """Update a user's information.
        
        Args:
            user_id: ID of the user to update
            **kwargs: Fields to update (email, first_name, last_name, etc.)
            
        Returns:
            Updated User object or None if not found
            
        Raises:
            ValueError: If trying to update to an email that already exists
        """
        user = self.repository.find_by_id(user_id)
        if not user:
            return None
        
        # Handle email update separately to check uniqueness
        if 'email' in kwargs and kwargs['email'] != user.email:
            existing_user = self.repository.find_by_email(kwargs['email'])
            if existing_user and existing_user.user_id != user_id:
                raise ValueError(f"Email '{kwargs['email']}' is already registered")
            user.email = kwargs['email']
        
        # Update other fields
        if 'first_name' in kwargs:
            user.first_name = kwargs['first_name']
        if 'last_name' in kwargs:
            user.last_name = kwargs['last_name']
        if 'active' in kwargs:
            user.active = kwargs['active']
        
        # Update password if provided
        if 'password' in kwargs:
            password_hash = self._hash_password(kwargs['password'])
            user.set_password(password_hash)
        
        # Save and return the updated user
        return self.repository.save(user)
    
    def delete_user(self, user_id):
        """Delete a user.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(user_id)
    
    def get_all_users(self):
        """Get all users.
        
        Returns:
            List of all User objects
        """
        return self.repository.find_all()
    
    def _hash_password(self, password):
        """Hash a password.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        # This is a simplified example - use a proper password hashing library in production
        salt = "example_salt"  # In a real app, you'd use a unique salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()