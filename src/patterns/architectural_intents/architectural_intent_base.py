"""
Base class for architectural intent patterns.

This module provides the base class for all architectural intent 
pattern detectors, extending beyond traditional design patterns to
identify higher-level architectural decisions.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
import logging
import networkx as nx
from pathlib import Path

from ...pattern_base import Pattern, CompositePattern

logger = logging.getLogger(__name__)

class ArchitecturalIntentPattern(Pattern):
    """Base class for architectural intent patterns.
    
    This class extends the basic Pattern class to provide capabilities
    for detecting higher-level architectural intentions across multiple
    files and components.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 languages: Optional[List[str]] = None):
        """Initialize an architectural intent pattern.
        
        Args:
            name: Unique identifier for the pattern
            description: Human-readable description of the pattern
            languages: List of supported languages. If None, supports all languages.
        """
        super().__init__(name, description, languages)
        self.component_graph = nx.DiGraph()
        
    def match(self, 
              tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        For architectural intent patterns, this is just the first step.
        The full architectural intent detection requires analyzing relationships
        between multiple files, which is done by the analyze_architecture method.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of component information dictionaries
        """
        raise NotImplementedError("Subclasses must implement match()")
    
    def analyze_architecture(self, 
                            results: List[Dict],
                            codebase_root: Optional[str] = None) -> Dict:
        """Analyze architectural patterns across multiple files.
        
        This method looks for higher-level architectural intents by analyzing
        the relationships between components identified in individual files.
        
        Args:
            results: List of results from analyzing individual files
            codebase_root: The root directory of the codebase
            
        Returns:
            A dictionary containing the detected architectural intents
        """
        # Reset the component graph
        self.component_graph = nx.DiGraph()
        
        # Build the component graph
        self._build_component_graph(results)
        
        # Analyze the graph for architectural intents
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
            
            logger.debug(f"Analyzing file: {file_path} with patterns: {list(patterns.keys())}")
            
            # Process each pattern type
            for pattern_name, matches in patterns.items():
                logger.debug(f"Processing {len(matches)} matches for pattern {pattern_name}")
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
        """Analyze the component graph for architectural intents.
        
        Returns:
            A dictionary containing the detected architectural intents
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