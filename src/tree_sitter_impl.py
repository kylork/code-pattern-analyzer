"""
Real tree-sitter implementation for the code pattern analyzer.
This replaces the mock implementation with actual tree-sitter functionality.
"""

from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import os
import logging

import tree_sitter
from tree_sitter import Language, Parser, Tree, Node

from .tree_sitter_manager import TreeSitterManager

logger = logging.getLogger(__name__)

class TreeSitterWrapper:
    """Wrapper for tree-sitter functionality."""
    
    def __init__(self, languages_dir: Optional[str] = None):
        """Initialize the tree-sitter wrapper.
        
        Args:
            languages_dir: Directory to store language definitions. If None,
                uses the default directory.
        """
        self.manager = TreeSitterManager(languages_dir)
    
    def parse_code(self, code: str, language: str) -> Optional[Tree]:
        """Parse code using tree-sitter.
        
        Args:
            code: The source code to parse
            language: The language of the source code
            
        Returns:
            The tree-sitter parse tree
        """
        return self.manager.parse_code(code, language)
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[Tree]:
        """Parse a file using tree-sitter.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The tree-sitter parse tree
        """
        return self.manager.parse_file(file_path)
    
    def query(self, tree: Tree, query_string: str, language: str) -> List[Dict]:
        """Run a query against a parse tree.
        
        Args:
            tree: The tree-sitter parse tree
            query_string: The query string in tree-sitter query language
            language: The language of the source code
            
        Returns:
            A list of dictionaries with query results
        """
        query = self.manager.query(tree, query_string, language)
        captures = query.captures(tree.root_node)
        
        results = []
        for node, capture_name in captures:
            results.append({
                'capture': capture_name,
                'node': node,
                'start_point': (node.start_point[0], node.start_point[1]),
                'end_point': (node.end_point[0], node.end_point[1]),
            })
            
        return results
    
    def get_node_text(self, node: Node, code: Union[str, bytes]) -> str:
        """Get the text of a node from the original source code.
        
        Args:
            node: A tree-sitter node
            code: The original source code
            
        Returns:
            The text corresponding to the node
        """
        return self.manager.get_node_text(node, code)
    
    def get_available_languages(self) -> List[str]:
        """Get a list of available languages.
        
        Returns:
            A list of language names
        """
        return sorted(list(self.manager.get_available_languages()))

def create_wrapper(languages_dir: Optional[str] = None) -> TreeSitterWrapper:
    """Create a tree-sitter wrapper.
    
    Args:
        languages_dir: Directory to store language definitions. If None,
            uses the default directory.
            
    Returns:
        A TreeSitterWrapper instance
    """
    return TreeSitterWrapper(languages_dir)

def replace_mock_implementation() -> callable:
    """Replace the mock implementation with the real tree-sitter implementation.
    
    Returns:
        A function to restore the original implementation
    """
    from .parser import CodeParser
    from .pattern_registry import registry
    from .mock_implementation import patch_analyzer, MockTreeSitterTree
    
    logger.info("Replacing mock implementation with real tree-sitter implementation")
    
    # Get the mock implementation's restore function in case it's already patched
    restore_mock = None
    try:
        restore_mock = patch_analyzer()
    except Exception as e:
        logger.debug(f"No need to restore mock implementation: {e}")
    
    # Create a tree-sitter wrapper
    wrapper = create_wrapper()
    
    # Original methods
    original_methods = {}
    
    # Replace methods in the CodeParser class
    original_methods['CodeParser_parse_file'] = CodeParser.parse_file
    original_methods['CodeParser_parse_code'] = CodeParser.parse_code
    original_methods['CodeParser_query'] = CodeParser.query
    original_methods['CodeParser_get_node_text'] = CodeParser.get_node_text
    
    # Replace the parse_file method
    def real_parse_file(self, file_path):
        logger.debug(f"Using real tree-sitter parser for {file_path}")
        return wrapper.parse_file(file_path)
    CodeParser.parse_file = real_parse_file
    
    # Replace the parse_code method
    def real_parse_code(self, code, language):
        logger.debug(f"Using real tree-sitter parser for {language} code")
        return wrapper.parse_code(code, language)
    CodeParser.parse_code = real_parse_code
    
    # Replace the query method
    def real_query(self, tree, query_string, language):
        logger.debug(f"Using real tree-sitter query for {language}")
        return wrapper.query(tree, query_string, language)
    CodeParser.query = real_query
    
    # Replace the get_node_text method
    def real_get_node_text(self, node, code):
        return wrapper.get_node_text(node, code)
    CodeParser.get_node_text = real_get_node_text
    
    # Replace pattern.match methods to handle both real and mock trees
    for pattern_name, pattern in registry.patterns.items():
        if hasattr(pattern, 'match'):
            original_methods[f'pattern_match_{pattern_name}'] = pattern.match
            
            # Define a wrapper that can handle both real and mock trees
            def make_real_match(pattern, original_match):
                def real_match(self, tree, code, language, file_path=None, parser=None):
                    # Check if we got a mock tree
                    if isinstance(tree, MockTreeSitterTree):
                        logger.debug(f"Converting mock tree to real tree for {pattern.name}")
                        # Parse the code with the real parser
                        if parser is None:
                            from .parser import CodeParser
                            parser = CodeParser()
                        tree = parser.parse_code(code, language)
                    
                    # Call the original match method with the real tree
                    return original_match(self, tree, code, language, file_path, parser)
                
                return real_match
            
            # Patch the method
            original = pattern.match
            pattern.match = make_real_match(pattern, original)
    
    # Return a function to restore the original methods
    def restore():
        logger.info("Restoring original implementation")
        
        # Restore CodeParser methods
        CodeParser.parse_file = original_methods['CodeParser_parse_file']
        CodeParser.parse_code = original_methods['CodeParser_parse_code']
        CodeParser.query = original_methods['CodeParser_query']
        CodeParser.get_node_text = original_methods['CodeParser_get_node_text']
        
        # Restore pattern.match methods
        for pattern_name, pattern in registry.patterns.items():
            if hasattr(pattern, 'match'):
                key = f'pattern_match_{pattern_name}'
                if key in original_methods:
                    pattern.match = original_methods[key]
        
        # Restore mock implementation if it was patched
        if restore_mock:
            restore_mock()
    
    return restore