"""
High-level module demonstrating the Dependency Inversion Principle.

This module contains high-level business logic that depends on abstractions
(interfaces) rather than concrete implementations.
"""

from typing import Dict, Any, List, Optional
import json

from .interfaces import DataSource, NotificationService, LoggingService


class UserService:
    """High-level service that manages user operations."""
    
    def __init__(
        self,
        user_data_source: DataSource,
        notification_service: NotificationService,
        logger: LoggingService
    ):
        """Initialize with dependencies.
        
        Args:
            user_data_source: Data source for user data
            notification_service: Service for sending notifications
            logger: Logging service
        """
        self._user_data_source = user_data_source
        self._notification_service = notification_service
        self._logger = logger
        
    def register_user(self, user_data: Dict[str, Any]) -> bool:
        """Register a new user.
        
        Args:
            user_data: User information
            
        Returns:
            True if registration was successful
        """
        try:
            # Log the operation
            self._logger.log_info(f"Registering new user: {user_data.get('email')}")
            
            # Save user data
            success = self._user_data_source.save_data(user_data)
            
            if success:
                # Send welcome notification
                self._notification_service.send_notification(
                    user_data.get('email', ''),
                    f"Welcome {user_data.get('name', 'User')}! Thank you for registering."
                )
                self._logger.log_info(f"User registered successfully: {user_data.get('email')}")
                return True
            else:
                self._logger.log_error(f"Failed to save user data: {user_data.get('email')}")
                return False
                
        except Exception as e:
            self._logger.log_error(f"Error registering user: {user_data.get('email')}", e)
            return False
            
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user information by email.
        
        Args:
            email: User's email address
            
        Returns:
            User data if found, None otherwise
        """
        try:
            self._logger.log_info(f"Getting user by email: {email}")
            
            # Query the data source
            users = self._user_data_source.get_data(f"email={email}")
            
            # Find the matching user
            for user in users:
                if user.get('email') == email:
                    return user
                    
            self._logger.log_info(f"User not found: {email}")
            return None
            
        except Exception as e:
            self._logger.log_error(f"Error getting user by email: {email}", e)
            return None


class ReportGenerator:
    """High-level service that generates reports."""
    
    def __init__(
        self,
        data_source: DataSource,
        logger: LoggingService
    ):
        """Initialize with dependencies.
        
        Args:
            data_source: Data source for report data
            logger: Logging service
        """
        self._data_source = data_source
        self._logger = logger
        
    def generate_report(self, query: str, format_type: str = 'json') -> str:
        """Generate a report.
        
        Args:
            query: Query to filter data
            format_type: Output format ('json' or 'csv')
            
        Returns:
            Formatted report data
        """
        try:
            self._logger.log_info(f"Generating report with query: {query}")
            
            # Get data from the data source
            data = self._data_source.get_data(query)
            
            # Format the data
            if format_type.lower() == 'json':
                report = json.dumps(data, indent=2)
            elif format_type.lower() == 'csv':
                # Simple CSV formatting (in a real implementation, use csv module)
                headers = data[0].keys() if data else []
                rows = [','.join(str(item.get(h, '')) for h in headers) for item in data]
                report = ','.join(headers) + '\n' + '\n'.join(rows)
            else:
                report = str(data)
                
            self._logger.log_info(f"Report generated successfully with {len(data)} records")
            return report
            
        except Exception as e:
            self._logger.log_error(f"Error generating report: {query}", e)
            return "Error generating report"


class NotificationManager:
    """High-level service that manages notifications."""
    
    def __init__(
        self,
        primary_notification_service: NotificationService,
        backup_notification_service: Optional[NotificationService] = None,
        logger: Optional[LoggingService] = None
    ):
        """Initialize with dependencies.
        
        Args:
            primary_notification_service: Primary notification service
            backup_notification_service: Optional backup service
            logger: Optional logging service
        """
        self._primary_service = primary_notification_service
        self._backup_service = backup_notification_service
        self._logger = logger
        
    def notify_user(self, user_id: str, message: str) -> bool:
        """Send a notification to a user.
        
        Args:
            user_id: User identifier
            message: Notification message
            
        Returns:
            True if notification was sent successfully
        """
        # Try the primary service first
        primary_success = self._primary_service.send_notification(user_id, message)
        
        if primary_success:
            if self._logger:
                self._logger.log_info(f"Notification sent to {user_id} using primary service")
            return True
            
        # If primary fails and backup exists, try backup
        if not primary_success and self._backup_service:
            backup_success = self._backup_service.send_notification(user_id, message)
            
            if backup_success:
                if self._logger:
                    self._logger.log_info(f"Notification sent to {user_id} using backup service")
                return True
            else:
                if self._logger:
                    self._logger.log_error(f"Failed to send notification to {user_id} with both services")
                return False
                
        # Primary failed and no backup
        if self._logger:
            self._logger.log_error(f"Failed to send notification to {user_id}")
        return False