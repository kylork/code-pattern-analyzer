"""
Complexity Analyzer module.

This module provides a unified interface for analyzing code complexity
using multiple metrics like cyclomatic complexity, cognitive complexity,
and maintainability index.
"""

from typing import Dict, List, Optional, Any, Union
import logging

import tree_sitter

from .metric_base import ComplexityMetric
from .cyclomatic_complexity import CyclomaticComplexityMetric
from .cognitive_complexity import CognitiveComplexityMetric
from .maintainability_index import MaintainabilityIndexMetric

logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """Unified analyzer for code complexity metrics.
    
    This class provides a single interface for computing multiple complexity
    metrics on code and generating a comprehensive complexity report.
    """
    
    def __init__(self):
        """Initialize the complexity analyzer with all available metrics."""
        self.metrics = [
            CyclomaticComplexityMetric(),
            CognitiveComplexityMetric(),
            MaintainabilityIndexMetric()
        ]
    
    def analyze(self, 
               tree: tree_sitter.Tree, 
               code: str, 
               language: str,
               file_path: Optional[str] = None,
               include_metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze code complexity using all available metrics.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            include_metrics: Optional list of metric names to include (default: all)
            
        Returns:
            A dictionary containing the computed metrics and overall complexity assessment
        """
        # Filter metrics if requested
        metrics_to_use = self.metrics
        if include_metrics:
            metrics_to_use = [m for m in self.metrics if m.name in include_metrics]
        
        # Compute each metric
        results = {}
        for metric in metrics_to_use:
            try:
                if metric.supports_language(language):
                    metric_result = metric.compute(tree, code, language, file_path)
                    results[metric.name] = metric_result
            except Exception as e:
                logger.error(f"Error computing {metric.name}: {e}")
                results[metric.name] = {
                    "metric": metric.name,
                    "error": str(e),
                    "language": language,
                    "file_path": file_path
                }
        
        # Generate overall complexity assessment
        overall_assessment = self._generate_overall_assessment(results, language, file_path)
        
        # Return combined results
        return {
            "metrics": results,
            "overall_assessment": overall_assessment,
            "language": language,
            "file_path": file_path
        }
    
    def _generate_overall_assessment(self, 
                                   metric_results: Dict[str, Any],
                                   language: str,
                                   file_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate an overall assessment of code complexity.
        
        This combines the results of individual metrics to provide a unified view
        of code complexity and maintainability.
        
        Args:
            metric_results: Dictionary of metric results
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            Dictionary containing overall complexity assessment
        """
        # Extract values from individual metrics
        cyclomatic_value = metric_results.get("cyclomatic_complexity", {}).get("value")
        cognitive_value = metric_results.get("cognitive_complexity", {}).get("value")
        maintainability_value = metric_results.get("maintainability_index", {}).get("value")
        
        # Determine overall complexity level
        complexity_level = "unknown"
        if maintainability_value is not None:
            # If maintainability index is available, use it as the primary indicator
            if maintainability_value >= 80:
                complexity_level = "low"
            elif maintainability_value >= 60:
                complexity_level = "moderate"
            elif maintainability_value >= 40:
                complexity_level = "high"
            else:
                complexity_level = "very_high"
        elif cyclomatic_value is not None and cognitive_value is not None:
            # If both cyclomatic and cognitive complexity are available, use a combination
            # This is a simplified approach - a more sophisticated algorithm could be used
            if cyclomatic_value <= 10 and cognitive_value <= 15:
                complexity_level = "low"
            elif cyclomatic_value <= 20 and cognitive_value <= 30:
                complexity_level = "moderate"
            elif cyclomatic_value <= 30 and cognitive_value <= 50:
                complexity_level = "high"
            else:
                complexity_level = "very_high"
        elif cyclomatic_value is not None:
            # If only cyclomatic complexity is available
            if cyclomatic_value <= 10:
                complexity_level = "low"
            elif cyclomatic_value <= 20:
                complexity_level = "moderate"
            elif cyclomatic_value <= 30:
                complexity_level = "high"
            else:
                complexity_level = "very_high"
        elif cognitive_value is not None:
            # If only cognitive complexity is available
            if cognitive_value <= 15:
                complexity_level = "low"
            elif cognitive_value <= 30:
                complexity_level = "moderate"
            elif cognitive_value <= 50:
                complexity_level = "high"
            else:
                complexity_level = "very_high"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_results, complexity_level)
        
        # Generate a description
        description = self._generate_description(metric_results, complexity_level)
        
        return {
            "complexity_level": complexity_level,
            "description": description,
            "recommendations": recommendations,
            "language": language,
            "file_path": file_path
        }
    
    def _generate_recommendations(self, 
                               metric_results: Dict[str, Any],
                               complexity_level: str) -> List[str]:
        """Generate recommendations based on all metrics.
        
        Args:
            metric_results: Dictionary of metric results
            complexity_level: Overall complexity level
            
        Returns:
            List of recommendations
        """
        recommendations = set()
        
        # Collect recommendations from individual metrics
        for metric_name, result in metric_results.items():
            if "recommendations" in result:
                for rec in result["recommendations"]:
                    recommendations.add(rec)
        
        # Add overall recommendations based on complexity level
        if complexity_level == "high" or complexity_level == "very_high":
            recommendations.add("Consider refactoring this code to reduce its complexity")
            recommendations.add("Add comprehensive tests before making significant changes")
        
        # Convert to list and sort by length (shortest first for readability)
        return sorted(list(recommendations), key=len)
    
    def _generate_description(self, 
                            metric_results: Dict[str, Any],
                            complexity_level: str) -> str:
        """Generate a description of the overall code complexity.
        
        Args:
            metric_results: Dictionary of metric results
            complexity_level: Overall complexity level
            
        Returns:
            String description of code complexity
        """
        # Extract values from individual metrics
        cyclomatic_value = metric_results.get("cyclomatic_complexity", {}).get("value")
        cognitive_value = metric_results.get("cognitive_complexity", {}).get("value")
        maintainability_value = metric_results.get("maintainability_index", {}).get("value")
        
        # Generate description
        if complexity_level == "low":
            return (
                f"This code has low complexity and is likely easy to maintain. "
                f"Cyclomatic Complexity: {cyclomatic_value or 'N/A'}, "
                f"Cognitive Complexity: {cognitive_value or 'N/A'}, "
                f"Maintainability Index: {maintainability_value or 'N/A'}."
            )
        elif complexity_level == "moderate":
            return (
                f"This code has moderate complexity. While generally maintainable, "
                f"some areas may benefit from refactoring. "
                f"Cyclomatic Complexity: {cyclomatic_value or 'N/A'}, "
                f"Cognitive Complexity: {cognitive_value or 'N/A'}, "
                f"Maintainability Index: {maintainability_value or 'N/A'}."
            )
        elif complexity_level == "high":
            return (
                f"This code has high complexity, which may indicate potential maintainability issues. "
                f"Consider refactoring complex sections. "
                f"Cyclomatic Complexity: {cyclomatic_value or 'N/A'}, "
                f"Cognitive Complexity: {cognitive_value or 'N/A'}, "
                f"Maintainability Index: {maintainability_value or 'N/A'}."
            )
        elif complexity_level == "very_high":
            return (
                f"This code has very high complexity and is likely difficult to maintain. "
                f"Significant refactoring is recommended. "
                f"Cyclomatic Complexity: {cyclomatic_value or 'N/A'}, "
                f"Cognitive Complexity: {cognitive_value or 'N/A'}, "
                f"Maintainability Index: {maintainability_value or 'N/A'}."
            )
        else:
            return "Unable to determine code complexity."