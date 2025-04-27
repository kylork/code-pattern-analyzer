"""
Architectural anti-patterns detection module.

This module contains pattern detectors for recognizing problematic architectural
structures that violate good design principles.
"""

import logging
logger = logging.getLogger(__name__)

from .architectural_anti_pattern_base import ArchitecturalAntiPattern
from .tight_coupling import TightCouplingAntiPattern
from .dependency_cycle import DependencyCycleAntiPattern
from .architectural_erosion import ArchitecturalErosionAntiPattern
from .god_component import GodComponentAntiPattern
from .architectural_anti_pattern_detector import ArchitecturalAntiPatternDetector

logger.info("Architectural anti-patterns module initialized")
logger.debug(f"Loaded patterns: ArchitecturalAntiPattern, TightCouplingAntiPattern, DependencyCycleAntiPattern, ArchitecturalErosionAntiPattern, GodComponentAntiPattern, ArchitecturalAntiPatternDetector")

__all__ = [
    'ArchitecturalAntiPattern',
    'TightCouplingAntiPattern',
    'DependencyCycleAntiPattern',
    'ArchitecturalErosionAntiPattern',
    'GodComponentAntiPattern',
    'ArchitecturalAntiPatternDetector',
]