"""
Base classes for pattern definitions.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import os
import logging

import tree_sitter

logger = logging.getLogger(__name__)

class Pattern:
    """Base class for code patterns.
    
    A pattern is a set of rules for matching code structures in an AST.
    Subclasses should implement the match method and define query strings
    for each supported language.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 languages: Optional[List[str]] = None):
        """Initialize a pattern.
        
        Args:
            name: Unique identifier for the pattern
            description: Human-readable description of the pattern
            languages: List of supported languages. If None, supports all languages.
        """
        self.name = name
        self.description = description
        self.languages = set(languages) if languages else None
        
        # Subclasses should define language-specific queries
        # This can be a dictionary mapping language names to query strings
        self.queries: Dict[str, str] = {}
        
    def supports_language(self, language: str) -> bool:
        """Check if this pattern supports a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            True if the pattern supports the language, False otherwise
        """
        if self.languages is None:
            # Check if we have a query for this language
            return language in self.queries
        
        return language in self.languages and language in self.queries
    
    def match(self, 
              tree: tree_sitter.Tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of matches, where each match is a dictionary with details
        """
        raise NotImplementedError("Subclasses must implement match()")
        
    def get_query_string(self, language: str) -> Optional[str]:
        """Get the query string for a specific language.
        
        Args:
            language: The language of the source code
            
        Returns:
            The query string or None if the language is not supported
        """
        return self.queries.get(language)


class QueryBasedPattern(Pattern):
    """A pattern that uses tree-sitter queries for matching.
    
    This is a base class for patterns that use tree-sitter queries to match
    code structures. Subclasses should define language-specific queries and
    can customize the processing of query results.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 languages: Optional[List[str]] = None,
                 queries: Optional[Dict[str, str]] = None):
        """Initialize a query-based pattern.
        
        Args:
            name: Unique identifier for the pattern
            description: Human-readable description of the pattern
            languages: List of supported languages. If None, supports all languages.
            queries: Dictionary mapping language names to query strings
        """
        super().__init__(name, description, languages)
        if queries:
            self.queries = queries
    
    def match(self, 
              tree: tree_sitter.Tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None,
              parser=None) -> List[Dict]:
        """Match this pattern against an AST using tree-sitter queries.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of matches, where each match is a dictionary with details
        """
        if not self.supports_language(language):
            return []
            
        query_string = self.get_query_string(language)
        if not query_string:
            return []
            
        if parser is None:
            from .parser import CodeParser
            parser = CodeParser()
            
        # Run the query
        query_results = parser.query(tree, query_string, language)
        
        # Process the results
        matches = self._process_query_results(query_results, code, language, file_path, parser)
        
        return matches
    
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results into pattern matches.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of matches, where each match is a dictionary with details
        """
        # This is a generic implementation that can be overridden by subclasses
        matches = []
        current_match = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            
            # If this is a new primary capture, create a new match
            if capture == 'name' or capture == 'identifier':
                if current_match and 'name' in current_match:
                    matches.append(current_match)
                    current_match = {}
                
                # Get the text of the node
                text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
                
                current_match = {
                    'type': self.name,
                    'name': text,
                    'line': node.start_point[0] + 1,  # 1-indexed line numbers
                    'column': node.start_point[1],
                    'end_line': node.end_point[0] + 1,
                    'end_column': node.end_point[1],
                }
                
                if file_path:
                    current_match['file'] = file_path
            
            # Add other captures to the current match
            elif current_match:
                # Get the text of the node
                text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
                
                current_match[capture] = {
                    'text': text,
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1],
                    'end_line': node.end_point[0] + 1,
                    'end_column': node.end_point[1],
                }
        
        # Add the last match if there is one
        if current_match and 'name' in current_match:
            matches.append(current_match)
            
        return matches


class CompositePattern(Pattern):
    """A pattern composed of multiple sub-patterns.
    
    This is useful for complex patterns that require multiple queries
    or different matching strategies for different parts.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 patterns: List[Pattern],
                 languages: Optional[List[str]] = None):
        """Initialize a composite pattern.
        
        Args:
            name: Unique identifier for the pattern
            description: Human-readable description of the pattern
            patterns: List of sub-patterns
            languages: List of supported languages. If None, supports all languages.
        """
        super().__init__(name, description, languages)
        self.patterns = patterns
    
    def supports_language(self, language: str) -> bool:
        """Check if this pattern supports a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            True if at least one sub-pattern supports the language, False otherwise
        """
        if self.languages is not None:
            if language not in self.languages:
                return False
                
        # Check if any sub-pattern supports this language
        return any(pattern.supports_language(language) for pattern in self.patterns)
    
    def match(self, 
              tree: tree_sitter.Tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST using all sub-patterns.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of matches, where each match is a dictionary with details
        """
        if not self.supports_language(language):
            return []
            
        # Run all sub-patterns
        matches = []
        for pattern in self.patterns:
            if pattern.supports_language(language):
                pattern_matches = pattern.match(tree, code, language, file_path)
                
                # Add pattern matches to the result
                for match in pattern_matches:
                    # Add composite pattern info
                    match['composite_type'] = self.name
                    match['sub_pattern'] = pattern.name
                    matches.append(match)
                    
        return matches