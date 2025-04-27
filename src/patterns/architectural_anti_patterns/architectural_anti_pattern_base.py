"""
Base class for architectural anti-pattern detection.

This module provides the foundation for detecting architectural anti-patterns in a codebase,
focusing on problematic structures and relationships that violate good design principles.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
import logging
import networkx as nx
from pathlib import Path

from ...pattern_base import Pattern, CompositePattern

logger = logging.getLogger(__name__)

class ArchitecturalAntiPattern(Pattern):
    """Base class for architectural anti-patterns.
    
    Architectural anti-patterns represent problematic structural patterns
    that violate good design principles and lead to maintainability, 
    extensibility, or scalability issues.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 languages: Optional[List[str]] = None):
        """Initialize an architectural anti-pattern detector.
        
        Args:
            name: Unique identifier for the anti-pattern
            description: Human-readable description of the anti-pattern
            languages: List of supported languages. If None, supports all languages.
        """
        super().__init__(name, description, languages)
        self.component_graph = nx.DiGraph()
        self.architectural_styles = {}
        
    def match(self, 
              tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        For architectural anti-patterns, individual file analysis is minimal,
        as the patterns are primarily detected across the entire codebase.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of component information dictionaries
        """
        # Most architectural anti-pattern detection happens at the codebase level
        return []
    
    def analyze_architecture(self, 
                            results: List[Dict],
                            architectural_styles: Dict,
                            codebase_root: Optional[str] = None) -> Dict:
        """Analyze architectural anti-patterns across a codebase.
        
        This method uses the component graph built by architectural style analysis
        to detect problematic patterns.
        
        Args:
            results: List of results from analyzing individual files
            architectural_styles: Dictionary of architectural style results
            codebase_root: The root directory of the codebase
            
        Returns:
            A dictionary containing the detected architectural anti-patterns
        """
        # Store the architectural styles for later use
        self.architectural_styles = architectural_styles
        
        # Use the component graph from architectural style detection if available
        primary_style = architectural_styles.get("primary_style", "unknown")
        
        if primary_style != "unknown" and primary_style in architectural_styles.get("styles", {}):
            style_data = architectural_styles["styles"][primary_style]
            
            # Get the component graph from the primary style pattern if available
            if hasattr(style_data, "get_component_graph"):
                self.component_graph = style_data.get_component_graph()
        
        # If no component graph is available, build our own
        if self.component_graph.number_of_nodes() == 0:
            self._build_component_graph(results)
        
        # Analyze the graph for architectural anti-patterns
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
        """Analyze the component graph for architectural anti-patterns.
        
        Returns:
            A dictionary containing the detected architectural anti-patterns
        """
        # This is a placeholder - subclasses should implement this
        return {
            "type": self.name,
            "severity": 0.0,
            "instances": [],
            "description": "Not implemented"
        }
    
    def get_component_graph(self) -> nx.DiGraph:
        """Get the component graph.
        
        Returns:
            The directed graph of components and relationships
        """
        return self.component_graph