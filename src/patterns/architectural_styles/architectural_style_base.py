"""
Base class for architectural style patterns.

This module provides the base class for detecting higher-level architectural 
styles that combine multiple architectural intent patterns.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
import logging
import networkx as nx
from pathlib import Path

from ...pattern_base import Pattern, CompositePattern

logger = logging.getLogger(__name__)

class ArchitecturalStylePattern(Pattern):
    """Base class for architectural style patterns.
    
    Architectural styles represent higher-level patterns that combine
    multiple architectural intents (like Separation of Concerns,
    Information Hiding, and Dependency Inversion) into recognized 
    architectural approaches.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 languages: Optional[List[str]] = None):
        """Initialize an architectural style pattern.
        
        Args:
            name: Unique identifier for the pattern
            description: Human-readable description of the pattern
            languages: List of supported languages. If None, supports all languages.
        """
        super().__init__(name, description, languages)
        self.component_graph = nx.DiGraph()
        self.architectural_intents = {}
        
    def match(self, 
              tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        For architectural style patterns, individual file analysis is minimal,
        as the patterns are primarily detected across the entire codebase.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of component information dictionaries
        """
        # Most architectural style detection happens at the codebase level
        # Individual file analysis might just tag components for later processing
        return []
    
    def analyze_architecture(self, 
                            results: List[Dict],
                            architectural_intents: Dict,
                            codebase_root: Optional[str] = None) -> Dict:
        """Analyze architectural style across a codebase.
        
        This method combines the results from individual architectural intents
        to identify higher-level architectural styles.
        
        Args:
            results: List of results from analyzing individual files
            architectural_intents: Dictionary of architectural intent results
            codebase_root: The root directory of the codebase
            
        Returns:
            A dictionary containing the detected architectural styles
        """
        # Store the architectural intents for later use
        self.architectural_intents = architectural_intents
        
        # Reset the component graph
        self.component_graph = nx.DiGraph()
        
        # Build the component graph from the combined results
        self._build_component_graph(results)
        
        # Analyze the graph for architectural styles
        return self._analyze_graph()
    
    def _build_component_graph(self, results: List[Dict]) -> None:
        """Build a graph of components and their relationships.
        
        Args:
            results: List of results from analyzing individual files
        """
        logger.info(f"Building component graph from {len(results)} results")
        
        for result in results:
            if "error" in result:
                logger.warning(f"Skipping result with error: {result.get('error', 'Unknown error')}")
                continue
                
            file_path = result.get("file", "")
            patterns = result.get("patterns", {})
            
            # Process each pattern type
            for pattern_name, matches in patterns.items():
                self._process_pattern_matches(pattern_name, matches, file_path)
    
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        Args:
            pattern_name: The name of the pattern
            matches: List of pattern matches
            file_path: Path to the file
        """
        # This is a placeholder - subclasses should implement this
        pass
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for architectural styles.
        
        Returns:
            A dictionary containing the detected architectural style
        """
        # This is a placeholder - subclasses should implement this
        return {
            "type": self.name,
            "confidence": 0.0,
            "components": [],
            "description": "Not implemented"
        }
    
    def get_component_graph(self) -> nx.DiGraph:
        """Get the component graph.
        
        Returns:
            The directed graph of components and relationships
        """
        return self.component_graph