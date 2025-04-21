"""
Data Access module demonstrating information hiding principles.

This module implements a data access layer with clear encapsulation,
interface separation, and module boundaries.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

__all__ = ['DataAccessFactory', 'UserRepository']

class DataEntity:
    """Base class for all data entities."""
    def __init__(self, entity_id: str = None):
        self._id = entity_id
        self._is_dirty = False
    
    @property
    def id(self) -> str:
        """Get the entity ID."""
        return self._id
    
    @property
    def is_dirty(self) -> bool:
        """Check if entity has unsaved changes."""
        return self._is_dirty
    
    def _mark_dirty(self):
        """Mark the entity as having unsaved changes."""
        self._is_dirty = True
    
    def _mark_clean(self):
        """Mark the entity as having no unsaved changes."""
        self._is_dirty = False


class UserEntity(DataEntity):
    """User entity with proper encapsulation."""
    
    def __init__(self, user_id: str = None, username: str = None, email: str = None):
        """Initialize a user entity.
        
        Args:
            user_id: The user's unique identifier
            username: The user's username
            email: The user's email address
        """
        super().__init__(user_id)
        self._username = username
        self._email = email
        self._password_hash = None
        self._last_login = None
    
    @property
    def username(self) -> str:
        """Get the username."""
        return self._username
    
    @username.setter
    def username(self, value: str):
        """Set the username and mark entity as dirty."""
        if value != self._username:
            self._username = value
            self._mark_dirty()
    
    @property
    def email(self) -> str:
        """Get the email address."""
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Set the email address and mark entity as dirty."""
        if value != self._email:
            self._email = value
            self._mark_dirty()
    
    def set_password(self, password_hash: str):
        """Set the password hash.
        
        Args:
            password_hash: The hash of the user's password
        """
        self._password_hash = password_hash
        self._mark_dirty()
    
    def verify_password(self, password_hash: str) -> bool:
        """Verify if the provided password hash matches.
        
        Args:
            password_hash: The hash to verify
            
        Returns:
            True if the password hash matches, False otherwise
        """
        return self._password_hash == password_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary.
        
        Returns:
            Dictionary representation of the entity
        """
        return {
            'id': self._id,
            'username': self._username,
            'email': self._email,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserEntity':
        """Create a user entity from a dictionary.
        
        Args:
            data: Dictionary with user data
            
        Returns:
            A new UserEntity instance
        """
        user = cls(
            user_id=data.get('id'),
            username=data.get('username'),
            email=data.get('email')
        )
        
        if 'password_hash' in data:
            user.set_password(data['password_hash'])
        
        return user


class Repository(ABC):
    """Abstract repository interface."""
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[DataEntity]:
        """Get an entity by ID.
        
        Args:
            entity_id: The entity ID to retrieve
            
        Returns:
            The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def save(self, entity: DataEntity) -> bool:
        """Save an entity.
        
        Args:
            entity: The entity to save
            
        Returns:
            True if the entity was saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if the entity was deleted successfully, False otherwise
        """
        pass


class UserRepository(Repository):
    """Repository for managing user entities."""
    
    def __init__(self, data_source=None):
        """Initialize the repository with a data source.
        
        Args:
            data_source: The data source to use
        """
        self._data_source = data_source or {}
        self._storage = {}
    
    def get_by_id(self, entity_id: str) -> Optional[UserEntity]:
        """Get a user by ID.
        
        Args:
            entity_id: The user ID to retrieve
            
        Returns:
            The user entity if found, None otherwise
        """
        if entity_id in self._storage:
            return self._storage[entity_id]
        
        # Fetch from data source
        user_data = self._fetch_from_data_source(entity_id)
        if user_data:
            user = UserEntity.from_dict(user_data)
            self._storage[entity_id] = user
            return user
        
        return None
    
    def get_by_username(self, username: str) -> Optional[UserEntity]:
        """Get a user by username.
        
        Args:
            username: The username to search for
            
        Returns:
            The user entity if found, None otherwise
        """
        # Implementation omitted for brevity
        return None
    
    def save(self, entity: UserEntity) -> bool:
        """Save a user entity.
        
        Args:
            entity: The user entity to save
            
        Returns:
            True if the user was saved successfully, False otherwise
        """
        if not isinstance(entity, UserEntity):
            raise TypeError("Expected UserEntity")
        
        try:
            # Implementation details hidden
            user_dict = entity.to_dict()
            
            # Save to data source
            if self._save_to_data_source(entity.id, user_dict):
                self._storage[entity.id] = entity
                entity._mark_clean()
                return True
            
            return False
        except Exception:
            return False
    
    def delete(self, entity_id: str) -> bool:
        """Delete a user by ID.
        
        Args:
            entity_id: The ID of the user to delete
            
        Returns:
            True if the user was deleted successfully, False otherwise
        """
        try:
            # Delete from data source
            if self._delete_from_data_source(entity_id):
                if entity_id in self._storage:
                    del self._storage[entity_id]
                return True
            
            return False
        except Exception:
            return False
    
    def get_all(self) -> List[UserEntity]:
        """Get all users.
        
        Returns:
            List of all user entities
        """
        # Implementation omitted for brevity
        return []
    
    def _fetch_from_data_source(self, entity_id: str) -> Dict[str, Any]:
        """Fetch user data from the data source.
        
        Args:
            entity_id: The user ID to fetch
            
        Returns:
            Dictionary with user data
        """
        # Implementation details hidden
        return self._data_source.get(entity_id, {})
    
    def _save_to_data_source(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """Save user data to the data source.
        
        Args:
            entity_id: The user ID
            data: The user data to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        # Implementation details hidden
        self._data_source[entity_id] = data
        return True
    
    def _delete_from_data_source(self, entity_id: str) -> bool:
        """Delete user data from the data source.
        
        Args:
            entity_id: The user ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        # Implementation details hidden
        if entity_id in self._data_source:
            del self._data_source[entity_id]
            return True
        return False


class DataAccessFactory:
    """Factory for creating repository instances."""
    
    @staticmethod
    def create_user_repository(data_source=None) -> UserRepository:
        """Create a user repository.
        
        Args:
            data_source: Optional data source to use
            
        Returns:
            A new UserRepository instance
        """
        return UserRepository(data_source)