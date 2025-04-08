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
        
        try:
            # Run the query
            if hasattr(parser, 'query'):
                # Use the parser's query method
                query_results = parser.query(tree, query_string, language)
            else:
                # Direct tree-sitter query if parser doesn't provide query method
                query_results = self._direct_tree_sitter_query(tree, query_string, language, code, parser)
            
            # Process the results
            matches = self._process_query_results(query_results, code, language, file_path, parser)
            
            return matches
        except Exception as e:
            logger.error(f"Error running query for pattern {self.name}: {e}")
            return []
            
    def _direct_tree_sitter_query(self, 
                                tree: tree_sitter.Tree, 
                                query_string: str, 
                                language: str, 
                                code: str,
                                parser=None) -> List[Dict]:
        """Run a tree-sitter query directly on the tree.
        
        This is used when the parser doesn't provide a query method.
        
        Args:
            tree: The tree-sitter AST
            query_string: The query string to run
            language: The language of the source code
            code: The source code that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of dictionaries with query results
        """
        from tree_sitter import Query
        
        # Get the language object
        if parser and hasattr(parser, 'manager') and hasattr(parser.manager, 'language_cache'):
            if language in parser.manager.language_cache:
                lang_obj = parser.manager.language_cache[language]
            else:
                # Try to load the language
                if parser.manager.ensure_language_installed(language):
                    lang_obj = parser.manager.language_cache[language]
                else:
                    raise ValueError(f"Language {language} not available")
        else:
            # If we can't get the language object, use the mock implementation fallback
            from .mock_implementation import MockTreeSitterTree
            if isinstance(tree, MockTreeSitterTree):
                # Just return the mock implementation's matches
                return []
            else:
                raise ValueError(f"Cannot get language object for {language}")
        
        # Create the query
        query = Query(lang_obj, query_string)
        
        # Run the query
        captures = query.captures(tree.root_node)
        
        # Format the results like what parser.query would return
        results = []
        for node, capture_name in captures:
            results.append({
                'capture': capture_name,
                'node': node,
                'start_point': (node.start_point[0], node.start_point[1]),
                'end_point': (node.end_point[0], node.end_point[1]),
            })
            
        return results
    
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
        
        # Group captures by their primary identifier
        # This helps handle cases where captures may come in any order
        capture_groups = {}
        primary_captures = ['name', 'identifier', 'function_name', 'class_name', 'method_name']
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            
            # Get node text - handle different node types
            if hasattr(node, 'text'):
                # Direct node.text attribute (might be bytes or string)
                if isinstance(node.text, bytes):
                    text = node.text.decode('utf-8')
                else:
                    text = str(node.text)
            elif parser and hasattr(parser, 'get_node_text'):
                # Use parser's node text extraction
                text = parser.get_node_text(node, code)
            else:
                # Fallback: extract from the original code using source positions
                start_byte = node.start_byte
                end_byte = node.end_byte
                if isinstance(code, str):
                    # Handle string code
                    if start_byte < len(code) and end_byte <= len(code):
                        text = code[start_byte:end_byte]
                    else:
                        # Safety check for byte indices that might be out of range
                        text = f"<node at {node.start_point}-{node.end_point}>"
                elif isinstance(code, bytes):
                    # Handle bytes code
                    if start_byte < len(code) and end_byte <= len(code):
                        text = code[start_byte:end_byte].decode('utf-8', errors='replace')
                    else:
                        text = f"<node at {node.start_point}-{node.end_point}>"
                else:
                    # Unknown code type
                    text = f"<node at {node.start_point}-{node.end_point}>"
            
            # Store the result with extracted text
            result_with_text = {
                'capture': capture,
                'node': node,
                'text': text,
                'start_point': (node.start_point[0], node.start_point[1]),
                'end_point': (node.end_point[0], node.end_point[1]),
            }
            
            # If this is a primary identifier, start a new capture group
            if capture in primary_captures:
                # Generate a unique key for this capture
                key = f"{capture}_{node.start_point[0]}_{node.start_point[1]}"
                if key not in capture_groups:
                    capture_groups[key] = []
                capture_groups[key].append(result_with_text)
            else:
                # Find the closest primary capture to associate with
                closest_key = None
                closest_distance = float('inf')
                
                for key in capture_groups:
                    # Get the primary capture's node
                    primary_result = capture_groups[key][0]
                    primary_node = primary_result['node']
                    
                    # Calculate distance between nodes (using line numbers for simplicity)
                    distance = abs(primary_node.start_point[0] - node.start_point[0])
                    
                    # Update if this is closer
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_key = key
                
                # If we found a group and it's reasonably close (within 10 lines)
                if closest_key is not None and closest_distance <= 10:
                    capture_groups[closest_key].append(result_with_text)
                else:
                    # Create a new group with a generated key
                    key = f"unknown_{node.start_point[0]}_{node.start_point[1]}"
                    if key not in capture_groups:
                        capture_groups[key] = []
                    capture_groups[key].append(result_with_text)
        
        # Process each capture group into a match
        for key, group in capture_groups.items():
            # Look for a primary capture to name the match
            primary_result = None
            for result in group:
                if result['capture'] in primary_captures:
                    primary_result = result
                    break
            
            # Skip groups without a primary identifier
            if not primary_result:
                continue
            
            # Create the match with the primary identifier
            match = {
                'type': self.name,
                'name': primary_result['text'],
                'line': primary_result['start_point'][0] + 1,  # 1-indexed line numbers
                'column': primary_result['start_point'][1],
                'end_line': primary_result['end_point'][0] + 1,
                'end_column': primary_result['end_point'][1],
            }
            
            if file_path:
                match['file'] = file_path
            
            # Add other captures to the match
            for result in group:
                if result is not primary_result:  # Skip the primary result we already processed
                    capture = result['capture']
                    match[capture] = {
                        'text': result['text'],
                        'line': result['start_point'][0] + 1,
                        'column': result['start_point'][1],
                        'end_line': result['end_point'][0] + 1,
                        'end_column': result['end_point'][1],
                    }
            
            matches.append(match)
            
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