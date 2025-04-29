"""
User model implementation.

This module contains the User entity definition.
"""

class User:
    """User entity representing a system user."""
    
    def __init__(self, user_id=None, username=None, email=None, first_name=None, last_name=None):
        """Initialize a user with basic information.
        
        Args:
            user_id: Unique identifier for the user
            username: User's login name
            email: User's email address
            first_name: User's first name
            last_name: User's last name
        """
        self.user_id = user_id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self._password_hash = None
        self.created_at = None
        self.updated_at = None
        self.active = True
    
    @property
    def full_name(self):
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or ""
    
    def set_password(self, password_hash):
        """Store the user's password hash.
        
        Args:
            password_hash: Hashed password value
        """
        self._password_hash = password_hash
    
    def verify_password(self, password_hash):
        """Verify if the provided password hash matches the stored hash.
        
        Args:
            password_hash: Hash to verify
            
        Returns:
            True if the password hash matches, False otherwise
        """
        return self._password_hash == password_hash
    
    def to_dict(self):
        """Convert the user object to a dictionary.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a user object from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            New User instance
        """
        user = cls(
            user_id=data.get('user_id'),
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
        )
        user.active = data.get('active', True)
        user.created_at = data.get('created_at')
        user.updated_at = data.get('updated_at')
        
        if 'password_hash' in data:
            user.set_password(data['password_hash'])
            
        return user