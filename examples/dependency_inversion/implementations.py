"""
Concrete implementations of the interfaces module.

This module contains concrete implementations of the abstract interfaces,
demonstrating the low-level modules in the Dependency Inversion Principle.
"""

import json
import os
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .interfaces import DataSource, NotificationService, LoggingService


class SqlDataSource(DataSource):
    """SQL database implementation of DataSource."""
    
    def __init__(self, connection_string: str):
        """Initialize with a connection string.
        
        Args:
            connection_string: Database connection string
        """
        self._connection_string = connection_string
        # In a real implementation, we would establish a database connection here
        
    def get_data(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve data from SQL database.
        
        Args:
            query: SQL query string
            
        Returns:
            List of data records
        """
        # In a real implementation, we would execute the SQL query
        # For this example, we'll return mock data
        return [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
        ]
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to SQL database.
        
        Args:
            data: Data record to save
            
        Returns:
            True if save was successful
        """
        # In a real implementation, we would insert the data into the database
        return True


class JsonFileDataSource(DataSource):
    """JSON file implementation of DataSource."""
    
    def __init__(self, file_path: str):
        """Initialize with a file path.
        
        Args:
            file_path: Path to the JSON file
        """
        self._file_path = file_path
        
    def get_data(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve data from JSON file.
        
        Args:
            query: Simple query string to filter by
            
        Returns:
            List of data records
        """
        if not os.path.exists(self._file_path):
            return []
            
        with open(self._file_path, 'r') as f:
            data = json.load(f)
            
        # Simple filtering based on query string
        if query:
            return [item for item in data if query.lower() in str(item).lower()]
        return data
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to JSON file.
        
        Args:
            data: Data record to save
            
        Returns:
            True if save was successful
        """
        existing_data = []
        if os.path.exists(self._file_path):
            with open(self._file_path, 'r') as f:
                existing_data = json.load(f)
                
        existing_data.append(data)
        
        with open(self._file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
        return True


class EmailNotificationService(NotificationService):
    """Email implementation of NotificationService."""
    
    def __init__(self, smtp_server: str, username: str, password: str):
        """Initialize with SMTP server details.
        
        Args:
            smtp_server: SMTP server address
            username: SMTP username
            password: SMTP password
        """
        self._smtp_server = smtp_server
        self._username = username
        self._password = password
        self._sent_notifications = {}
        
    def send_notification(self, user_id: str, message: str) -> bool:
        """Send an email notification.
        
        Args:
            user_id: User's email address
            message: Email message
            
        Returns:
            True if email was sent
        """
        # In a real implementation, we would send an actual email
        notification_id = f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
        self._sent_notifications[notification_id] = {
            "user_id": user_id,
            "message": message,
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
        return True
    
    def get_notification_status(self, notification_id: str) -> str:
        """Get the status of an email notification.
        
        Args:
            notification_id: Email notification ID
            
        Returns:
            Status string
        """
        if notification_id in self._sent_notifications:
            return self._sent_notifications[notification_id]["status"]
        return "unknown"


class PushNotificationService(NotificationService):
    """Push notification implementation of NotificationService."""
    
    def __init__(self, api_key: str, api_url: str):
        """Initialize with API details.
        
        Args:
            api_key: API key for the push notification service
            api_url: API URL for the push notification service
        """
        self._api_key = api_key
        self._api_url = api_url
        self._sent_notifications = {}
        
    def send_notification(self, user_id: str, message: str) -> bool:
        """Send a push notification.
        
        Args:
            user_id: User device ID
            message: Notification message
            
        Returns:
            True if notification was sent
        """
        # In a real implementation, we would make an API call
        notification_id = f"push_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
        self._sent_notifications[notification_id] = {
            "user_id": user_id,
            "message": message,
            "status": "delivered",
            "timestamp": datetime.now().isoformat()
        }
        return True
    
    def get_notification_status(self, notification_id: str) -> str:
        """Get the status of a push notification.
        
        Args:
            notification_id: Push notification ID
            
        Returns:
            Status string
        """
        if notification_id in self._sent_notifications:
            return self._sent_notifications[notification_id]["status"]
        return "unknown"


class ConsoleLoggingService(LoggingService):
    """Console implementation of LoggingService."""
    
    def log_info(self, message: str) -> None:
        """Log an info message to the console.
        
        Args:
            message: Message to log
        """
        print(f"INFO: {message}")
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message to the console.
        
        Args:
            message: Error message
            error: Optional exception object
        """
        if error:
            print(f"ERROR: {message} - {str(error)}")
        else:
            print(f"ERROR: {message}")


class FileLoggingService(LoggingService):
    """File-based implementation of LoggingService."""
    
    def __init__(self, log_file_path: str):
        """Initialize with a log file path.
        
        Args:
            log_file_path: Path to the log file
        """
        self._log_file_path = log_file_path
        # Configure logging
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def log_info(self, message: str) -> None:
        """Log an info message to the file.
        
        Args:
            message: Message to log
        """
        logging.info(message)
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message to the file.
        
        Args:
            message: Error message
            error: Optional exception object
        """
        if error:
            logging.error(f"{message} - {str(error)}")
        else:
            logging.error(message)