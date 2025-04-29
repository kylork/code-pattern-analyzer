"""
Registry of all available patterns.
"""

from typing import Dict, List, Optional, Set, Type, Union
import logging

from .pattern_base import Pattern

logger = logging.getLogger(__name__)

class PatternRegistry:
    """Registry for pattern definitions.
    
    This maintains a catalog of all available patterns and provides methods
    for looking up patterns by name, category, or language.
    """
    
    def __init__(self):
        """Initialize an empty pattern registry."""
        self.patterns: Dict[str, Pattern] = {}
        self.categories: Dict[str, Set[str]] = {}
        self.languages: Dict[str, Set[str]] = {}
    
    def register(self, pattern: Pattern, categories: Optional[List[str]] = None):
        """Register a pattern with the registry.
        
        Args:
            pattern: The pattern to register
            categories: Optional list of categories to assign to the pattern
        """
        # Check if the pattern already exists
        if pattern.name in self.patterns:
            logger.warning(f"Pattern '{pattern.name}' already registered. Overwriting.")
            
        # Register the pattern
        self.patterns[pattern.name] = pattern
        
        # Register categories
        if categories:
            for category in categories:
                if category not in self.categories:
                    self.categories[category] = set()
                self.categories[category].add(pattern.name)
        
        # Register languages
        languages = []
        if hasattr(pattern, 'languages') and pattern.languages:
            languages = pattern.languages
        elif hasattr(pattern, 'queries') and pattern.queries:
            languages = list(pattern.queries.keys())
            
        for language in languages:
            if language not in self.languages:
                self.languages[language] = set()
            self.languages[language].add(pattern.name)
            
        logger.debug(f"Registered pattern '{pattern.name}'")
    
    def bulk_register(self, patterns: List[Pattern], category: Optional[str] = None):
        """Register multiple patterns at once.
        
        Args:
            patterns: The patterns to register
            category: Optional category to assign to all patterns
        """
        categories = [category] if category else None
        for pattern in patterns:
            self.register(pattern, categories)
    
    def register_from_module(self, module, category: Optional[str] = None):
        """Register all patterns from a module.
        
        Args:
            module: A Python module containing pattern classes
            category: Optional category to assign to all patterns from this module
        """
        # Find all Pattern classes in the module
        patterns = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Pattern) and attr != Pattern:
                # Create an instance of the pattern
                try:
                    pattern = attr()
                    patterns.append(pattern)
                except Exception as e:
                    logger.error(f"Failed to instantiate pattern {attr_name}: {e}")
        
        # Register the patterns
        self.bulk_register(patterns, category)
        logger.info(f"Registered {len(patterns)} patterns from module {module.__name__}")
    
    def get_pattern(self, name: str) -> Optional[Pattern]:
        """Get a pattern by name.
        
        Args:
            name: The name of the pattern
            
        Returns:
            The pattern or None if not found
        """
        return self.patterns.get(name)
    
    def get_patterns_by_category(self, category: str) -> List[Pattern]:
        """Get all patterns in a category.
        
        Args:
            category: The category to look up
            
        Returns:
            A list of patterns in the category
        """
        if category not in self.categories:
            return []
            
        return [self.patterns[name] for name in self.categories[category]]
    
    def get_patterns_by_language(self, language: str) -> List[Pattern]:
        """Get all patterns that support a language.
        
        Args:
            language: The language to look up
            
        Returns:
            A list of patterns that support the language
        """
        if language not in self.languages:
            return []
            
        return [self.patterns[name] for name in self.languages[language]]
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all registered patterns.
        
        Returns:
            A list of all patterns
        """
        return list(self.patterns.values())
    
    def get_all_categories(self) -> List[str]:
        """Get all registered categories.
        
        Returns:
            A list of all categories
        """
        return list(self.categories.keys())
    
    def get_all_languages(self) -> List[str]:
        """Get all supported languages.
        
        Returns:
            A list of all languages
        """
        return list(self.languages.keys())


# Create a global registry instance
registry = PatternRegistry()

# Import all patterns
from .patterns.function_patterns import (
    FunctionDefinitionPattern, MethodDefinitionPattern, 
    ConstructorPattern, AllFunctionsPattern
)
from .patterns.class_patterns import (
    ClassDefinitionPattern, InterfaceDefinitionPattern,
    ClassWithInheritancePattern, AllClassPatternsPattern
)
from .patterns.design_patterns import (
    SingletonPattern, FactoryMethodPattern, DesignPatternsPattern
)
from .patterns.code_smells import (
    LongMethodPattern, DeepNestingPattern, 
    ComplexConditionPattern, CodeSmellsPattern
)

# Register basic patterns
registry.register(FunctionDefinitionPattern(), ["functions", "basic"])
registry.register(MethodDefinitionPattern(), ["functions", "basic"])
registry.register(ConstructorPattern(), ["functions", "basic"])
registry.register(AllFunctionsPattern(), ["functions", "composite"])

registry.register(ClassDefinitionPattern(), ["classes", "basic"])
registry.register(InterfaceDefinitionPattern(), ["classes", "basic"])
registry.register(ClassWithInheritancePattern(), ["classes", "basic"])
registry.register(AllClassPatternsPattern(), ["classes", "composite"])

# Register design patterns
registry.register(SingletonPattern(), ["design_patterns"])
registry.register(FactoryMethodPattern(), ["design_patterns"])
registry.register(DesignPatternsPattern(), ["design_patterns", "composite"])

# Register code smells
registry.register(LongMethodPattern(), ["code_smells"])
registry.register(DeepNestingPattern(), ["code_smells"])
registry.register(ComplexConditionPattern(), ["code_smells"])
registry.register(CodeSmellsPattern(), ["code_smells", "composite"])