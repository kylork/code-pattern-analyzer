"""
Maintainability Index metric implementation.

This module provides the implementation of the Maintainability Index,
which combines various metrics to assess the maintainability of code.
"""

from typing import Dict, List, Optional, Any, Union, Set
import logging
import re
import math

import tree_sitter

from .metric_base import ComplexityMetric
from .cyclomatic_complexity import CyclomaticComplexityMetric

logger = logging.getLogger(__name__)

class MaintainabilityIndexMetric(ComplexityMetric):
    """Maintainability Index metric implementation.
    
    The Maintainability Index is a composite metric that combines:
    1. Halstead Volume (HV) - measuring the size and complexity of operations
    2. Cyclomatic Complexity (CC) - measuring the number of independent paths
    3. Lines of Code (LOC) - measuring the physical size of the code
    
    The formula is typically:
    MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
    
    For simplicity, this implementation uses a modified version that weighs
    Cyclomatic Complexity more heavily and estimates Halstead Volume.
    """
    
    def __init__(self):
        """Initialize the Maintainability Index metric."""
        super().__init__(
            name="maintainability_index",
            description="Maintainability Index - composite metric for assessing code maintainability"
        )
        
        # Create a Cyclomatic Complexity metric to use in the calculation
        self.cc_metric = CyclomaticComplexityMetric()
        
        # Maintainability level thresholds
        self.maintainability_thresholds = {
            "high": 80,    # 80-100 is high maintainability
            "moderate": 60,  # 60-79 is moderate maintainability
            "low": 40      # 40-59 is low maintainability
                           # < 40 is very low maintainability
        }
    
    def compute(self, 
               tree: tree_sitter.Tree, 
               code: str, 
               language: str,
               file_path: Optional[str] = None) -> Dict[str, Any]:
        """Compute the Maintainability Index for a given AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary containing the computed metric values
        """
        # Calculate component metrics
        
        # 1. Lines of Code (LOC)
        loc = len(code.split('\n'))
        
        # 2. Cyclomatic Complexity (CC)
        cc_results = self.cc_metric.compute(tree, code, language, file_path)
        cc = cc_results.get("value", 1)  # Default to 1 if not available
        
        # 3. Estimate Halstead Volume (HV)
        # This is a simplified estimation, as proper Halstead calculation is complex
        operators, operands = self._estimate_halstead_components(code, language)
        halstead_volume = self._calculate_halstead_volume(operators, operands)
        
        # Calculate Maintainability Index
        mi = self._calculate_maintainability_index(halstead_volume, cc, loc)
        
        # Ensure value is between 0 and 100
        mi = max(0, min(100, mi))
        
        # Get maintainability level
        maintainability_level = self.get_complexity_level(mi)
        
        # Return the results
        return {
            "metric": self.name,
            "value": mi,
            "language": language,
            "file_path": file_path,
            "maintainability_level": maintainability_level,
            "component_metrics": {
                "lines_of_code": loc,
                "cyclomatic_complexity": cc,
                "halstead_volume": halstead_volume
            },
            "recommendations": self.get_recommendations(mi)
        }
    
    def _estimate_halstead_components(self, code: str, language: str) -> tuple:
        """Estimate Halstead components (operators and operands).
        
        This is a simplified estimation that counts various symbols as operators
        and identifiers as operands.
        
        Args:
            code: The source code
            language: The language of the source code
            
        Returns:
            Tuple of (operators count, operands count)
        """
        # Define patterns to match operators and operands
        operator_patterns = {
            "python": [
                r'[\+\-\*/=<>!%&|\^~]', r'\band\b', r'\bor\b', r'\bnot\b', 
                r'\bin\b', r'\bis\b', r'\bif\b', r'\belse\b', r'\bfor\b', 
                r'\bwhile\b', r'\bdef\b', r'\bclass\b'
            ],
            "javascript": [
                r'[\+\-\*/=<>!%&|\^~]', r'&&', r'\|\|', r'!', r'===', r'!==',
                r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bfunction\b',
                r'\bclass\b', r'\bconst\b', r'\blet\b', r'\bvar\b'
            ],
            # Default patterns for other languages
            "default": [
                r'[\+\-\*/=<>!%&|\^~]', r'\bif\b', r'\belse\b', r'\bfor\b', 
                r'\bwhile\b', r'\bfunction\b', r'\bclass\b'
            ]
        }
        
        operand_patterns = {
            "python": [
                r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',  # identifiers
                r'\b\d+\b',  # numbers
                r'"([^"\\]|\\.)*"',  # double-quoted strings
                r"'([^'\\]|\\.)*'"   # single-quoted strings
            ],
            "javascript": [
                r'\b[a-zA-Z_$][a-zA-Z0-9_$]*\b',  # identifiers
                r'\b\d+\b',  # numbers
                r'"([^"\\]|\\.)*"',  # double-quoted strings
                r"'([^'\\]|\\.)*'",  # single-quoted strings
                r"`([^`\\]|\\.)*`"   # template strings
            ],
            # Default patterns for other languages
            "default": [
                r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',  # identifiers
                r'\b\d+\b',  # numbers
                r'"([^"\\]|\\.)*"',  # double-quoted strings
                r"'([^'\\]|\\.)*'"   # single-quoted strings
            ]
        }
        
        # Get patterns for the specified language or use default
        op_patterns = operator_patterns.get(language, operator_patterns["default"])
        operand_patterns = operand_patterns.get(language, operand_patterns["default"])
        
        # Count operators and operands
        operators = 0
        for pattern in op_patterns:
            operators += len(re.findall(pattern, code))
        
        operands = 0
        for pattern in operand_patterns:
            operands += len(re.findall(pattern, code))
        
        return operators, operands
    
    def _calculate_halstead_volume(self, operators: int, operands: int) -> float:
        """Calculate Halstead Volume.
        
        The formula is: V = N * log2(n)
        where:
        - N is the total number of operators and operands (N1 + N2)
        - n is the number of distinct operators and operands (n1 + n2)
        
        Since we don't track distinct operators/operands, we estimate n as a fraction of N.
        
        Args:
            operators: Count of operators
            operands: Count of operands
            
        Returns:
            Halstead Volume value
        """
        # Total operators and operands
        N = operators + operands
        
        # Estimate distinct operators and operands as a fraction of the total
        # This is a simplification - a proper implementation would count unique operators/operands
        n = max(1, int(N * 0.3))  # Assume about 30% are unique
        
        # Calculate Halstead Volume
        if N == 0 or n <= 1:
            return 0
        
        volume = N * math.log2(n)
        return volume
    
    def _calculate_maintainability_index(self, 
                                       halstead_volume: float, 
                                       cyclomatic_complexity: int, 
                                       lines_of_code: int) -> float:
        """Calculate the Maintainability Index.
        
        The standard formula is:
        MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
        
        We normalize the result to a 0-100 scale.
        
        Args:
            halstead_volume: Halstead Volume
            cyclomatic_complexity: Cyclomatic Complexity
            lines_of_code: Lines of Code
            
        Returns:
            Maintainability Index value (0-100)
        """
        # Handle edge cases
        if lines_of_code <= 0:
            return 100  # Empty files are perfectly maintainable
        
        if halstead_volume <= 0:
            halstead_volume = 1  # Avoid taking log of zero or negative
        
        # Calculate raw MI
        raw_mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic_complexity - 16.2 * math.log(lines_of_code)
        
        # Normalize to 0-100 scale
        normalized_mi = max(0, min(100, raw_mi * 100 / 171))
        
        return normalized_mi
    
    def get_complexity_level(self, value: Union[int, float]) -> str:
        """Get the maintainability level for a given Maintainability Index value.
        
        Args:
            value: The computed Maintainability Index value
            
        Returns:
            A string indicating the maintainability level ('high', 'moderate', 'low', 'very_low')
        """
        if value >= self.maintainability_thresholds["high"]:
            return "high"
        elif value >= self.maintainability_thresholds["moderate"]:
            return "moderate"
        elif value >= self.maintainability_thresholds["low"]:
            return "low"
        else:
            return "very_low"
    
    def get_recommendations(self, value: Union[int, float]) -> List[str]:
        """Get recommendations for improving code with this maintainability level.
        
        Args:
            value: The computed Maintainability Index value
            
        Returns:
            A list of recommendations for improving the code
        """
        if value >= self.maintainability_thresholds["high"]:
            # High maintainability - no specific recommendations needed
            return ["The code is highly maintainable - continue the good practices"]
        
        recommendations = []
        
        if value >= self.maintainability_thresholds["moderate"]:
            # Moderate maintainability
            recommendations = [
                "Consider refactoring the most complex methods",
                "Look for opportunities to simplify complex expressions",
                "Ensure code is well-documented with meaningful comments"
            ]
        elif value >= self.maintainability_thresholds["low"]:
            # Low maintainability
            recommendations = [
                "Refactor complex methods into smaller, focused functions",
                "Reduce cyclomatic complexity by simplifying conditional logic",
                "Break down large functions and classes into smaller units",
                "Improve naming to make code more self-explanatory",
                "Add comprehensive unit tests before making major changes"
            ]
        else:
            # Very low maintainability
            recommendations = [
                "This code requires significant refactoring to improve maintainability",
                "Break down large methods into smaller, single-responsibility functions",
                "Simplify complex conditional logic and reduce nesting levels",
                "Consider rewriting particularly problematic sections",
                "Ensure comprehensive test coverage before making major changes",
                "Look for and eliminate code duplication through abstraction",
                "Implement design patterns to improve structure and clarity"
            ]
        
        return recommendations
    
    def supports_language(self, language: str) -> bool:
        """Check if this metric supports a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            True if the metric supports the language, False otherwise
        """
        # The maintainability index can be calculated for any language
        # as long as we can calculate or estimate its component metrics
        return self.cc_metric.supports_language(language)