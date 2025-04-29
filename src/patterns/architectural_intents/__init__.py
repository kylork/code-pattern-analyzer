"""
Architectural intent detection module.

This module contains pattern detectors for recognizing higher-level architectural 
intents beyond specific design patterns.
"""

import logging
logger = logging.getLogger(__name__)

from .separation_of_concerns import SeparationOfConcernsIntent
from .information_hiding import InformationHidingIntent
from .dependency_inversion import DependencyInversionIntent
from .architectural_intent_base import ArchitecturalIntentPattern
from .architectural_intent_detector import ArchitecturalIntentDetector

logger.info("Architectural intent patterns module initialized")
logger.debug(f"Loaded patterns: ArchitecturalIntentPattern, SeparationOfConcernsIntent, InformationHidingIntent, DependencyInversionIntent, ArchitecturalIntentDetector")

__all__ = [
    'SeparationOfConcernsIntent',
    'InformationHidingIntent',
    'DependencyInversionIntent',
    'ArchitecturalIntentPattern',
    'ArchitecturalIntentDetector',
]