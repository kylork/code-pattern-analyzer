"""
Client code demonstrating how to use the Dependency Inversion Principle.

This module shows how the application is wired together using dependency injection
and factories, while maintaining the Dependency Inversion Principle.
"""

from typing import Dict, Any

from .interfaces import DataSource, NotificationService, LoggingService
from .factories import (
    DataSourceFactory, 
    NotificationServiceFactory,
    LoggingServiceFactory
)
from .high_level import UserService, ReportGenerator, NotificationManager


def create_services(config: Dict[str, Any]):
    """Create services using factories.
    
    Args:
        config: Application configuration
        
    Returns:
        Dictionary of created services
    """
    # Create logging service first
    logging_config = config.get('logging', {})
    logging_service = LoggingServiceFactory.create_logging_service(
        logging_config.get('type', 'console'),
        logging_config
    )
    
    # Create data sources
    user_db_config = config.get('user_database', {})
    user_data_source = DataSourceFactory.create_data_source(
        user_db_config.get('type', 'json'),
        user_db_config
    )
    
    report_db_config = config.get('report_database', {})
    report_data_source = DataSourceFactory.create_data_source(
        report_db_config.get('type', 'json'),
        report_db_config
    )
    
    # Create notification services
    notification_config = config.get('notifications', {})
    primary_notification_service = NotificationServiceFactory.create_notification_service(
        notification_config.get('primary_type', 'email'),
        notification_config.get('primary_config', {})
    )
    
    # Create backup notification service if configured
    backup_notification_service = None
    if 'backup_type' in notification_config:
        backup_notification_service = NotificationServiceFactory.create_notification_service(
            notification_config.get('backup_type'),
            notification_config.get('backup_config', {})
        )
    
    # Create high-level services with their dependencies
    user_service = UserService(
        user_data_source,
        primary_notification_service,
        logging_service
    )
    
    report_generator = ReportGenerator(
        report_data_source,
        logging_service
    )
    
    notification_manager = NotificationManager(
        primary_notification_service,
        backup_notification_service,
        logging_service
    )
    
    return {
        'user_service': user_service,
        'report_generator': report_generator,
        'notification_manager': notification_manager,
        'logger': logging_service
    }


def run_application():
    """Run the application."""
    # Define configuration
    config = {
        'logging': {
            'type': 'console'
        },
        'user_database': {
            'type': 'json',
            'file_path': 'users.json'
        },
        'report_database': {
            'type': 'json',
            'file_path': 'reports.json'
        },
        'notifications': {
            'primary_type': 'email',
            'primary_config': {
                'smtp_server': 'smtp.example.com',
                'username': 'user',
                'password': 'pass'
            },
            'backup_type': 'push',
            'backup_config': {
                'api_key': 'api_key',
                'api_url': 'https://push.example.com/api'
            }
        }
    }
    
    # Create services
    services = create_services(config)
    
    # Use the services
    logger = services['logger']
    user_service = services['user_service']
    report_generator = services['report_generator']
    notification_manager = services['notification_manager']
    
    # Register a user
    logger.log_info("Starting application")
    user_service.register_user({
        'name': 'John Doe',
        'email': 'john@example.com',
        'role': 'user'
    })
    
    # Generate a report
    report = report_generator.generate_report('role=user')
    logger.log_info(f"Generated report: {report}")
    
    # Send a notification
    notification_manager.notify_user(
        'john@example.com',
        'Your report is ready!'
    )
    
    logger.log_info("Application finished")


if __name__ == "__main__":
    run_application()