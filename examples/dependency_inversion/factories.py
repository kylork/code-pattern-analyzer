"""
Factory module for creating interface implementations.

This module provides factory classes and methods for creating concrete 
implementations of interfaces, further supporting the Dependency Inversion Principle
by centralizing implementation creation.
"""

from typing import Dict, Any, Optional
import os

from .interfaces import DataSource, NotificationService, LoggingService
from .implementations import (
    SqlDataSource, JsonFileDataSource,
    EmailNotificationService, PushNotificationService,
    ConsoleLoggingService, FileLoggingService
)


class DataSourceFactory:
    """Factory for creating DataSource implementations."""
    
    @staticmethod
    def create_data_source(source_type: str, config: Dict[str, Any]) -> DataSource:
        """Create a DataSource implementation.
        
        Args:
            source_type: Type of data source to create ('sql' or 'json')
            config: Configuration parameters for the data source
            
        Returns:
            DataSource implementation
            
        Raises:
            ValueError: If source_type is not supported
        """
        if source_type.lower() == 'sql':
            return SqlDataSource(config.get('connection_string', ''))
        elif source_type.lower() == 'json':
            return JsonFileDataSource(config.get('file_path', 'data.json'))
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")


class NotificationServiceFactory:
    """Factory for creating NotificationService implementations."""
    
    @staticmethod
    def create_notification_service(service_type: str, config: Dict[str, Any]) -> NotificationService:
        """Create a NotificationService implementation.
        
        Args:
            service_type: Type of notification service ('email' or 'push')
            config: Configuration parameters for the service
            
        Returns:
            NotificationService implementation
            
        Raises:
            ValueError: If service_type is not supported
        """
        if service_type.lower() == 'email':
            return EmailNotificationService(
                config.get('smtp_server', ''),
                config.get('username', ''),
                config.get('password', '')
            )
        elif service_type.lower() == 'push':
            return PushNotificationService(
                config.get('api_key', ''),
                config.get('api_url', '')
            )
        else:
            raise ValueError(f"Unsupported notification service type: {service_type}")


class LoggingServiceFactory:
    """Factory for creating LoggingService implementations."""
    
    # Singleton instance
    _console_instance: Optional[ConsoleLoggingService] = None
    _file_instances: Dict[str, FileLoggingService] = {}
    
    @classmethod
    def create_logging_service(cls, service_type: str, config: Dict[str, Any] = None) -> LoggingService:
        """Create a LoggingService implementation.
        
        Args:
            service_type: Type of logging service ('console' or 'file')
            config: Configuration parameters for the service
            
        Returns:
            LoggingService implementation
            
        Raises:
            ValueError: If service_type is not supported
        """
        if config is None:
            config = {}
            
        if service_type.lower() == 'console':
            # Use singleton pattern for console logger
            if cls._console_instance is None:
                cls._console_instance = ConsoleLoggingService()
            return cls._console_instance
            
        elif service_type.lower() == 'file':
            log_file = config.get('log_file_path', 'app.log')
            
            # Reuse existing file logger if possible
            if log_file in cls._file_instances:
                return cls._file_instances[log_file]
                
            # Create new file logger
            logger = FileLoggingService(log_file)
            cls._file_instances[log_file] = logger
            return logger
            
        else:
            raise ValueError(f"Unsupported logging service type: {service_type}")