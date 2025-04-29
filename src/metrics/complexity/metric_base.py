"""
Base class for complexity metrics.

This module provides the base class for all complexity metrics,
ensuring consistent interfaces and behavior.
"""

from typing import Dict, List, Optional, Any, Union
import logging

import tree_sitter

logger = logging.getLogger(__name__)

class ComplexityMetric:
    """Base class for complexity metrics.
    
    All complexity metrics should extend this class and implement the compute method.
    """
    
    def __init__(self, name: str, description: str):
        """Initialize the complexity metric.
        
        Args:
            name: Unique identifier for the metric
            description: Human-readable description of the metric
        """
        self.name = name
        self.description = description
    
    def compute(self, 
               tree: tree_sitter.Tree, 
               code: str, 
               language: str,
               file_path: Optional[str] = None) -> Dict[str, Any]:
        """Compute the complexity metric for a given AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary containing the computed metric values
        """
        raise NotImplementedError("Subclasses must implement compute()")
    
    def get_complexity_level(self, value: Union[int, float]) -> str:
        """Get the complexity level for a given metric value.
        
        Args:
            value: The computed metric value
            
        Returns:
            A string indicating the complexity level ('low', 'moderate', 'high', 'very_high')
        """
        raise NotImplementedError("Subclasses must implement get_complexity_level()")
    
    def get_recommendations(self, value: Union[int, float]) -> List[str]:
        """Get recommendations for improving code with this complexity level.
        
        Args:
            value: The computed metric value
            
        Returns:
            A list of recommendations for improving the code
        """
        raise NotImplementedError("Subclasses must implement get_recommendations()")
    
    def supports_language(self, language: str) -> bool:
        """Check if this metric supports a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            True if the metric supports the language, False otherwise
        """
        # By default, assume all languages are supported
        # Subclasses can override this if needed
        return True