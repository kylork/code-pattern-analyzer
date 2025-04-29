"""
User controller implementation.

This module handles HTTP requests related to user operations.
"""

import json
from ..services.user_service import UserService

class UserController:
    """Controller for user-related HTTP endpoints."""
    
    def __init__(self, user_service=None):
        """Initialize the controller with a user service.
        
        Args:
            user_service: Service for user business logic
        """
        self.service = user_service or UserService()
    
    def handle_get_users(self, request):
        """Handle GET request for all users.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTTP response with user list
        """
        users = self.service.get_all_users()
        user_dicts = [user.to_dict() for user in users]
        
        return {
            'status': 'success',
            'data': user_dicts
        }
    
    def handle_get_user(self, request, user_id):
        """Handle GET request for a specific user.
        
        Args:
            request: HTTP request object
            user_id: ID of the user to retrieve
            
        Returns:
            HTTP response with user data or error
        """
        user = self.service.get_user(user_id)
        if not user:
            return {
                'status': 'error',
                'message': f'User with ID {user_id} not found'
            }
        
        return {
            'status': 'success',
            'data': user.to_dict()
        }
    
    def handle_create_user(self, request):
        """Handle POST request to create a new user.
        
        Args:
            request: HTTP request object with user data
            
        Returns:
            HTTP response with created user or error
        """
        # In a real app, you'd parse this from request body
        data = request.get('body', {})
        
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return {
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }
        
        try:
            user = self.service.register_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            
            return {
                'status': 'success',
                'data': user.to_dict()
            }
        except ValueError as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def handle_update_user(self, request, user_id):
        """Handle PUT request to update a user.
        
        Args:
            request: HTTP request object with user data
            user_id: ID of the user to update
            
        Returns:
            HTTP response with updated user or error
        """
        # In a real app, you'd parse this from request body
        data = request.get('body', {})
        
        if not data:
            return {
                'status': 'error',
                'message': 'No update data provided'
            }
        
        # Extract allowed fields
        update_data = {}
        allowed_fields = ['email', 'first_name', 'last_name', 'password', 'active']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        try:
            user = self.service.update_user(user_id, **update_data)
            if not user:
                return {
                    'status': 'error',
                    'message': f'User with ID {user_id} not found'
                }
            
            return {
                'status': 'success',
                'data': user.to_dict()
            }
        except ValueError as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def handle_delete_user(self, request, user_id):
        """Handle DELETE request to remove a user.
        
        Args:
            request: HTTP request object
            user_id: ID of the user to delete
            
        Returns:
            HTTP response indicating success or error
        """
        result = self.service.delete_user(user_id)
        
        if not result:
            return {
                'status': 'error',
                'message': f'User with ID {user_id} not found'
            }
        
        return {
            'status': 'success',
            'message': f'User with ID {user_id} deleted successfully'
        }
    
    def handle_authenticate(self, request):
        """Handle authentication request.
        
        Args:
            request: HTTP request with login credentials
            
        Returns:
            HTTP response with authentication result
        """
        # In a real app, you'd parse this from request body
        data = request.get('body', {})
        
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return {
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }
        
        user = self.service.authenticate(
            username=data['username'],
            password=data['password']
        )
        
        if not user:
            return {
                'status': 'error',
                'message': 'Invalid username or password'
            }
        
        return {
            'status': 'success',
            'data': {
                'user': user.to_dict(),
                'token': 'dummy_auth_token'  # In a real app, generate a proper JWT
            }
        }