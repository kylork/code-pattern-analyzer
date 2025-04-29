"""
Event-Driven Architecture example package.

This package demonstrates Event-Driven Architecture principles,
including event production and consumption, message passing,
and advanced patterns like CQRS and Event Sourcing.
"""

from .events import Event
from .event_bus import EventBus

__all__ = [
    'Event',
    'EventBus',
]