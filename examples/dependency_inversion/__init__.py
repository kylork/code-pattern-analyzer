"""
Dependency Inversion Principle example package.

This package demonstrates the Dependency Inversion Principle (DIP),
one of the SOLID principles of object-oriented design.

The DIP states that:
1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

Key components:
- interfaces.py: Abstract interfaces that both high and low level modules depend on
- implementations.py: Concrete implementations of the interfaces
- factories.py: Factory classes for creating implementations
- high_level.py: High-level business logic that depends only on abstractions
- client.py: Client code that wires everything together
"""

from .interfaces import DataSource, NotificationService, LoggingService
from .high_level import UserService, ReportGenerator, NotificationManager

# Only expose the interfaces and high-level modules
__all__ = [
    'DataSource',
    'NotificationService',
    'LoggingService',
    'UserService',
    'ReportGenerator',
    'NotificationManager'
]