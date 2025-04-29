"""
User repository implementation.

This module provides data access functionality for user entities.
"""

from ..models.user import User

class UserRepository:
    """Repository for user data access operations."""
    
    def __init__(self, db_connection=None):
        """Initialize the repository with a database connection.
        
        Args:
            db_connection: Connection to the database
        """
        self.db = db_connection
        # For this example, we'll use a simple in-memory store
        self.users = {}
        self.next_id = 1
    
    def find_by_id(self, user_id):
        """Find a user by ID.
        
        Args:
            user_id: The user ID to look for
            
        Returns:
            User object or None if not found
        """
        if user_id in self.users:
            return User.from_dict(self.users[user_id])
        return None
    
    def find_by_username(self, username):
        """Find a user by username.
        
        Args:
            username: The username to look for
            
        Returns:
            User object or None if not found
        """
        for user_data in self.users.values():
            if user_data.get('username') == username:
                return User.from_dict(user_data)
        return None
    
    def find_by_email(self, email):
        """Find a user by email.
        
        Args:
            email: The email to look for
            
        Returns:
            User object or None if not found
        """
        for user_data in self.users.values():
            if user_data.get('email') == email:
                return User.from_dict(user_data)
        return None
    
    def save(self, user):
        """Save a user to the repository.
        
        Args:
            user: The user to save
            
        Returns:
            The saved user with updated ID if new
        """
        if not user.user_id:
            user.user_id = self.next_id
            self.next_id += 1
        
        # Store as dictionary
        self.users[user.user_id] = user.to_dict()
        
        return user
    
    def delete(self, user_id):
        """Delete a user from the repository.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if deleted, False if not found
        """
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    def find_all(self):
        """Get all users in the repository.
        
        Returns:
            List of all User objects
        """
        return [User.from_dict(data) for data in self.users.values()]