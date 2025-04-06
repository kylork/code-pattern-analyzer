"""
Parser for source code that uses tree-sitter to create ASTs.
"""

from typing import Dict, List, Optional, Tuple, Union
import os
import logging
from pathlib import Path

import tree_sitter

from .tree_sitter_manager import TreeSitterManager

logger = logging.getLogger(__name__)

class CodeParser:
    """A parser for source code that uses tree-sitter to create ASTs."""
    
    def __init__(self, languages_dir: Optional[str] = None):
        """Initialize the parser with tree-sitter support.
        
        Args:
            languages_dir: Optional directory to store language definitions.
                If None, uses the default directory.
        """
        self.manager = TreeSitterManager(languages_dir)
    
    def _get_language_by_extension(self, file_path: Union[str, Path]) -> Optional[str]:
        """Determine the language based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The language name or None if the extension is not recognized
        """
        return self.manager.get_language_by_extension(file_path)
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[tree_sitter.Tree]:
        """Parse a source file and return its AST.
        
        Args:
            file_path: Path to the file
            
        Returns:
            A tree-sitter Tree or None if parsing failed
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        language = self._get_language_by_extension(file_path)
        if not language:
            raise ValueError(f"Unsupported file type: {file_path}")
            
        try:
            return self.manager.parse_file(file_path)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return None
    
    def parse_code(self, code: str, language: str) -> Optional[tree_sitter.Tree]:
        """Parse a string of source code and return its AST.
        
        Args:
            code: The source code to parse
            language: The language of the source code
            
        Returns:
            A tree-sitter Tree or None if parsing failed
        """
        if not self.manager.ensure_language_installed(language):
            raise ValueError(f"Unsupported language: {language}")
            
        try:
            return self.manager.parse_code(code, language)
        except Exception as e:
            logger.error(f"Failed to parse code: {e}")
            return None
            
    def query(self, tree: tree_sitter.Tree, query_string: str, language: str) -> List[Dict]:
        """Run a query against a parse tree.
        
        Args:
            tree: The tree-sitter parse tree
            query_string: The query string in tree-sitter query language
            language: The language of the source code
            
        Returns:
            A list of matches, where each match is a dictionary with node details
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
    
    def get_node_text(self, node: tree_sitter.Node, code: Union[str, bytes]) -> str:
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
            A list of supported language names
        """
        return sorted(list(self.manager.get_available_languages()))