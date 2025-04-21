"""
Pattern implementations for code pattern analyzer.

This module contains implementations of various code patterns
that can be detected by the pattern analyzer.
"""

from ..pattern_registry import registry
from .function_patterns import AllFunctionsPattern
from .class_patterns import AllClassPatternsPattern 
from .design_patterns import DesignPatternsPattern
from .code_smells import CodeSmellsPattern
from .architectural_intents import ArchitecturalIntentDetector
from .architectural_styles import ArchitecturalStyleDetector

# Register all patterns with the pattern registry
registry.register(AllFunctionsPattern(), ["function_patterns"])
registry.register(AllClassPatternsPattern(), ["class_patterns"])
registry.register(DesignPatternsPattern(), ["design_patterns"])
registry.register(CodeSmellsPattern(), ["code_smells"])

# Register architectural intent patterns
from .architectural_intents import SeparationOfConcernsIntent, InformationHidingIntent, DependencyInversionIntent
registry.register(SeparationOfConcernsIntent(), ["architectural_intents"])
registry.register(InformationHidingIntent(), ["architectural_intents"])
registry.register(DependencyInversionIntent(), ["architectural_intents"])
registry.register(ArchitecturalIntentDetector(), ["architectural_intents"])

# Register architectural style patterns
from .architectural_styles import HexagonalArchitecturePattern, CleanArchitecturePattern, MicroservicesPattern, EventDrivenPattern, LayeredArchitecturePattern
registry.register(HexagonalArchitecturePattern(), ["architectural_styles"])
registry.register(CleanArchitecturePattern(), ["architectural_styles"])
registry.register(MicroservicesPattern(), ["architectural_styles"])
registry.register(EventDrivenPattern(), ["architectural_styles"])
registry.register(LayeredArchitecturePattern(), ["architectural_styles"])
registry.register(ArchitecturalStyleDetector(), ["architectural_styles"])

# Import additional pattern modules to ensure they're registered
from .python_patterns import *

# If enhanced patterns exist, import them too
try:
    from .enhanced import *
except ImportError:
    pass