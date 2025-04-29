"""
Interfaces module demonstrating the Dependency Inversion Principle.

This module defines abstract interfaces that higher-level modules can depend on,
rather than depending on concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DataSource(ABC):
    """Abstract interface for any data source."""
    
    @abstractmethod
    def get_data(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve data from the source.
        
        Args:
            query: Query string to filter the data
            
        Returns:
            List of data records
        """
        pass
    
    @abstractmethod
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to the source.
        
        Args:
            data: Data record to save
            
        Returns:
            True if save was successful, False otherwise
        """
        pass


class NotificationService(ABC):
    """Abstract interface for notification services."""
    
    @abstractmethod
    def send_notification(self, user_id: str, message: str) -> bool:
        """Send a notification to a user.
        
        Args:
            user_id: Identifier for the user
            message: Notification message
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_notification_status(self, notification_id: str) -> str:
        """Get the status of a notification.
        
        Args:
            notification_id: Identifier for the notification
            
        Returns:
            Status string
        """
        pass


class LoggingService(ABC):
    """Abstract interface for logging services."""
    
    @abstractmethod
    def log_info(self, message: str) -> None:
        """Log an informational message.
        
        Args:
            message: Message to log
        """
        pass
    
    @abstractmethod
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message.
        
        Args:
            message: Error message
            error: Optional exception object
        """
        pass