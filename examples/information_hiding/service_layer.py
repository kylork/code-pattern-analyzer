"""
Service Layer module demonstrating information hiding principles.

This module implements a service layer with interfaces, dependency injection,
and proper hiding of implementation details.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import hashlib
import os

from .data_access import UserRepository, UserEntity, DataAccessFactory

__all__ = ['UserService', 'ServiceFactory']

# Interface for authentication
class AuthenticationService(ABC):
    """Interface for authentication services."""
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[Any]:
        """Authenticate a user with username and password.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            User information if authentication succeeds, None otherwise
        """
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.
        
        Args:
            token: The token to validate
            
        Returns:
            True if the token is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def create_token(self, user_id: str) -> str:
        """Create an authentication token for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Authentication token
        """
        pass


# Interface for user management
class UserService(ABC):
    """Interface for user management services."""
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID.
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            User information if found, None otherwise
        """
        pass
    
    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Create a new user.
        
        Args:
            username: The username
            email: The email address
            password: The password
            
        Returns:
            New user information if creation succeeds, None otherwise
        """
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a user.
        
        Args:
            user_id: The user ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated user information if update succeeds, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: The user ID to delete
            
        Returns:
            True if deletion succeeds, False otherwise
        """
        pass


# Implementation of the user service
class DefaultUserService(UserService):
    """Default implementation of UserService."""
    
    def __init__(self, user_repository: UserRepository = None):
        """Initialize the service with a user repository.
        
        Args:
            user_repository: The repository for user data access
        """
        self._repository = user_repository or DataAccessFactory.create_user_repository()
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID.
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            User information if found, None otherwise
        """
        user = self._repository.get_by_id(user_id)
        if user:
            return user.to_dict()
        return None
    
    def create_user(self, username: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Create a new user.
        
        Args:
            username: The username
            email: The email address
            password: The password
            
        Returns:
            New user information if creation succeeds, None otherwise
        """
        # Create a new user entity
        user_id = self._generate_id()
        user = UserEntity(user_id, username, email)
        
        # Hash the password
        password_hash = self._hash_password(password)
        user.set_password(password_hash)
        
        # Save the user
        if self._repository.save(user):
            return user.to_dict()
        
        return None
    
    def update_user(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a user.
        
        Args:
            user_id: The user ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated user information if update succeeds, None otherwise
        """
        user = self._repository.get_by_id(user_id)
        if not user:
            return None
        
        # Update user properties
        if 'username' in kwargs:
            user.username = kwargs['username']
        
        if 'email' in kwargs:
            user.email = kwargs['email']
        
        if 'password' in kwargs:
            password_hash = self._hash_password(kwargs['password'])
            user.set_password(password_hash)
        
        # Save the updated user
        if self._repository.save(user):
            return user.to_dict()
        
        return None
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user.
        
        Args:
            user_id: The user ID to delete
            
        Returns:
            True if deletion succeeds, False otherwise
        """
        return self._repository.delete(user_id)
    
    def _generate_id(self) -> str:
        """Generate a unique ID.
        
        Returns:
            A unique ID string
        """
        # Implementation detail hidden
        return hashlib.md5(os.urandom(16)).hexdigest()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password.
        
        Args:
            password: The password to hash
            
        Returns:
            The password hash
        """
        # Implementation detail hidden
        salt = "fixed_salt_for_example"  # In reality, use a per-user salt
        return hashlib.sha256((password + salt).encode()).hexdigest()


# Simple implementation of authentication service
class SimpleAuthService(AuthenticationService):
    """Simple implementation of authentication service."""
    
    def __init__(self, user_repository: UserRepository = None):
        """Initialize the service with a user repository.
        
        Args:
            user_repository: The repository for user data access
        """
        self._repository = user_repository or DataAccessFactory.create_user_repository()
        self._tokens = {}  # token -> user_id mapping
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            User information if authentication succeeds, None otherwise
        """
        # Implementation detail hidden
        # In a real implementation, would find user by username and verify password
        return None
    
    def validate_token(self, token: str) -> bool:
        """Validate an authentication token.
        
        Args:
            token: The token to validate
            
        Returns:
            True if the token is valid, False otherwise
        """
        return token in self._tokens
    
    def create_token(self, user_id: str) -> str:
        """Create an authentication token for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Authentication token
        """
        # Implementation detail hidden
        token = hashlib.sha256(f"{user_id}{os.urandom(16)}".encode()).hexdigest()
        self._tokens[token] = user_id
        return token
    
    def _invalidate_token(self, token: str) -> None:
        """Invalidate a token.
        
        Args:
            token: The token to invalidate
        """
        if token in self._tokens:
            del self._tokens[token]


# Factory for creating service instances
class ServiceFactory:
    """Factory for creating service instances."""
    
    @staticmethod
    def create_user_service(repository: UserRepository = None) -> UserService:
        """Create a user service.
        
        Args:
            repository: Optional repository to use
            
        Returns:
            A UserService implementation
        """
        return DefaultUserService(repository)
    
    @staticmethod
    def create_auth_service(repository: UserRepository = None) -> AuthenticationService:
        """Create an authentication service.
        
        Args:
            repository: Optional repository to use
            
        Returns:
            An AuthenticationService implementation
        """
        return SimpleAuthService(repository)