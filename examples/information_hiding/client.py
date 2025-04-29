"""
Client code that demonstrates using the information hiding interfaces.

This module shows how clients interact with the system through well-defined
interfaces without knowing implementation details.
"""

from typing import Dict, List, Optional, Any

from . import UserService, ServiceFactory

def create_test_user(user_service: UserService) -> Optional[Dict[str, Any]]:
    """Create a test user using the user service.
    
    Args:
        user_service: The user service
        
    Returns:
        The created user information if successful, None otherwise
    """
    return user_service.create_user(
        username="test_user",
        email="test@example.com",
        password="password123"  # In a real system, this would be handled more securely
    )

def update_test_user(user_service: UserService, user_id: str) -> Optional[Dict[str, Any]]:
    """Update a test user using the user service.
    
    Args:
        user_service: The user service
        user_id: The user ID to update
        
    Returns:
        The updated user information if successful, None otherwise
    """
    return user_service.update_user(
        user_id=user_id,
        email="updated@example.com"
    )

def get_user_info(user_service: UserService, user_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a user.
    
    Args:
        user_service: The user service
        user_id: The user ID to retrieve
        
    Returns:
        The user information if found, None otherwise
    """
    return user_service.get_user(user_id)

def demo_user_management():
    """Demonstrate user management through the service layer."""
    # Create a user service - we don't care about the implementation details
    user_service = ServiceFactory.create_user_service()
    
    # Create a test user
    user_info = create_test_user(user_service)
    if user_info:
        print(f"Created user: {user_info}")
        
        # Get the user's ID
        user_id = user_info.get('id')
        
        # Update the user
        updated_user = update_test_user(user_service, user_id)
        if updated_user:
            print(f"Updated user: {updated_user}")
        
        # Get the user info
        retrieved_user = get_user_info(user_service, user_id)
        if retrieved_user:
            print(f"Retrieved user: {retrieved_user}")
        
        # Delete the user
        if user_service.delete_user(user_id):
            print(f"Deleted user {user_id}")
        
        # Verify deletion
        if not user_service.get_user(user_id):
            print(f"User {user_id} no longer exists")
    else:
        print("Failed to create user")

if __name__ == "__main__":
    demo_user_management()