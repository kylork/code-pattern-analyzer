"""
Pattern recognizer for detecting patterns in source code.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import logging

import tree_sitter

from .pattern_base import Pattern
from .pattern_registry import registry, PatternRegistry

logger = logging.getLogger(__name__)

class PatternRecognizer:
    """Recognizes patterns in source code ASTs."""
    
    def __init__(self, registry: Optional[PatternRegistry] = None):
        """Initialize the pattern recognizer with a pattern registry.
        
        Args:
            registry: Optional pattern registry. If None, uses the global registry.
        """
        self.registry = registry or globals().get('registry')
        self.parser = None
    
    def get_available_patterns(self) -> List[str]:
        """Get the names of all available patterns.
        
        Returns:
            A list of pattern names
        """
        return sorted([pattern.name for pattern in self.registry.get_all_patterns()])
    
    def get_available_categories(self) -> List[str]:
        """Get the names of all available pattern categories.
        
        Returns:
            A list of category names
        """
        return sorted(self.registry.get_all_categories())
    
    def get_patterns_by_category(self, category: str) -> List[str]:
        """Get the names of all patterns in a category.
        
        Args:
            category: The category to look up
            
        Returns:
            A list of pattern names in the category
        """
        return sorted([pattern.name for pattern in self.registry.get_patterns_by_category(category)])
    
    def get_patterns_by_language(self, language: str) -> List[str]:
        """Get the names of all patterns that support a language.
        
        Args:
            language: The language to look up
            
        Returns:
            A list of pattern names that support the language
        """
        return sorted([pattern.name for pattern in self.registry.get_patterns_by_language(language)])
    
    def recognize(self, 
                  tree: tree_sitter.Tree, 
                  code: str,
                  language: str,
                  pattern_name: Optional[str] = None,
                  category: Optional[str] = None,
                  file_path: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Recognize patterns in an AST.
        
        Args:
            tree: The AST to analyze
            code: The source code that was parsed
            language: The language of the source code
            pattern_name: If provided, only match this specific pattern
            category: If provided, only match patterns in this category
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary mapping pattern names to lists of matches
        """
        if self.parser is None:
            from .parser import CodeParser
            self.parser = CodeParser()
        
        # Determine which patterns to match
        patterns_to_match = []
        
        if pattern_name:
            # Match a specific pattern
            pattern = self.registry.get_pattern(pattern_name)
            if not pattern:
                raise ValueError(f"Unknown pattern: {pattern_name}")
            patterns_to_match = [pattern]
        elif category:
            # Match all patterns in a category
            patterns_to_match = self.registry.get_patterns_by_category(category)
        else:
            # Match all patterns
            patterns_to_match = self.registry.get_all_patterns()
        
        # Filter patterns by language support
        patterns_to_match = [p for p in patterns_to_match if self._supports_language(p, language)]
        
        logger.debug(f"Matching {len(patterns_to_match)} patterns for {file_path}")
        
        # Apply each pattern
        results: Dict[str, List[Dict]] = {}
        
        for pattern in patterns_to_match:
            try:
                logger.debug(f"Attempting to match pattern {pattern.name} for {file_path}")
                matches = pattern.match(tree, code, language, file_path)
                if matches:
                    results[pattern.name] = matches
                    logger.debug(f"Found {len(matches)} matches for pattern {pattern.name}")
                else:
                    logger.debug(f"No matches found for pattern {pattern.name}")
            except Exception as e:
                logger.error(f"Error matching pattern '{pattern.name}': {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        return results
    
    def _supports_language(self, pattern: Pattern, language: str) -> bool:
        """Check if a pattern supports a language.
        
        Args:
            pattern: The pattern to check
            language: The language to check
            
        Returns:
            True if the pattern supports the language, False otherwise
        """
        if hasattr(pattern, 'supports_language'):
            return pattern.supports_language(language)
        
        # Try to determine support from pattern attributes
        if hasattr(pattern, 'languages') and pattern.languages:
            return language in pattern.languages
        
        if hasattr(pattern, 'queries') and pattern.queries:
            return language in pattern.queries
            
        return False