"""
Information Hiding pattern example package.

This package demonstrates the Information Hiding architectural principle
through a simple user management system.
"""

# Export only the public interfaces and factories
from .data_access import UserRepository, DataAccessFactory
from .service_layer import UserService, ServiceFactory