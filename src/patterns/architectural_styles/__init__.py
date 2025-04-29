"""
Architectural styles detection module.

This module contains pattern detectors for recognizing higher-level architectural
styles that combine multiple architectural intents.
"""

import logging
logger = logging.getLogger(__name__)

from .architectural_style_base import ArchitecturalStylePattern
from .hexagonal import HexagonalArchitecturePattern
from .clean_architecture import CleanArchitecturePattern
from .microservices import MicroservicesPattern
from .event_driven import EventDrivenPattern
from .layered import LayeredArchitecturePattern
from .architectural_style_detector import ArchitecturalStyleDetector

logger.info("Architectural styles module initialized")
logger.debug(f"Loaded patterns: ArchitecturalStylePattern, HexagonalArchitecturePattern, CleanArchitecturePattern, MicroservicesPattern, EventDrivenPattern, LayeredArchitecturePattern, ArchitecturalStyleDetector")

__all__ = [
    'ArchitecturalStylePattern',
    'HexagonalArchitecturePattern',
    'CleanArchitecturePattern',
    'MicroservicesPattern',
    'EventDrivenPattern',
    'LayeredArchitecturePattern',
    'ArchitecturalStyleDetector',
]