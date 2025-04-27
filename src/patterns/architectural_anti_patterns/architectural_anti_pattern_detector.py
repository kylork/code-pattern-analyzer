"""
Architectural anti-pattern detector composite pattern.

This module provides a composite pattern that aggregates multiple architectural
anti-pattern detectors to identify problematic structures in codebases.
"""

from typing import Dict, List, Optional
import logging

from ...pattern_base import CompositePattern
from .tight_coupling import TightCouplingAntiPattern
from .dependency_cycle import DependencyCycleAntiPattern
from .architectural_erosion import ArchitecturalErosionAntiPattern
from .god_component import GodComponentAntiPattern

logger = logging.getLogger(__name__)

class ArchitecturalAntiPatternDetector(CompositePattern):
    """A composite pattern for detecting architectural anti-patterns.
    
    This pattern combines multiple architectural anti-pattern detectors to
    provide a comprehensive analysis of problematic architectural structures
    and relationships in a codebase.
    """
    
    def __init__(self):
        """Initialize an architectural anti-pattern detector composite pattern."""
        super().__init__(
            name="architectural_anti_pattern",
            description="Identifies problematic architectural patterns across a codebase",
            patterns=[
                TightCouplingAntiPattern(),
                DependencyCycleAntiPattern(),
                ArchitecturalErosionAntiPattern(),
                GodComponentAntiPattern(),
                # Add more anti-pattern detectors here as they are implemented
            ],
        )
    
    def analyze_codebase(self, 
                        results: List[Dict],
                        architectural_styles: Dict,
                        codebase_root: Optional[str] = None) -> Dict:
        """Analyze architectural anti-patterns across a codebase.
        
        This method delegates to the sub-patterns' analyze_architecture methods
        to build a comprehensive understanding of architectural anti-patterns.
        
        Args:
            results: List of results from analyzing individual files
            architectural_styles: Results from architectural style analysis
            codebase_root: The root directory of the codebase
            
        Returns:
            A dictionary containing the detected architectural anti-patterns
        """
        anti_patterns = {}
        
        # Process each sub-pattern
        for pattern in self.patterns:
            # Only process architectural anti-pattern detectors
            if hasattr(pattern, 'analyze_architecture'):
                anti_pattern_name = pattern.name
                anti_pattern_results = pattern.analyze_architecture(
                    results, architectural_styles, codebase_root
                )
                anti_patterns[anti_pattern_name] = anti_pattern_results
        
        # Calculate overall anti-pattern severity
        overall_severity = self._calculate_overall_severity(anti_patterns)
        
        # Generate overall analysis
        return {
            "overall_severity": overall_severity,
            "anti_patterns": anti_patterns,
            "summary": self._generate_summary(anti_patterns, overall_severity),
            "recommendations": self._generate_recommendations(anti_patterns, overall_severity)
        }
    
    def _calculate_overall_severity(self, anti_patterns: Dict) -> float:
        """Calculate overall anti-pattern severity score.
        
        Args:
            anti_patterns: Dictionary of anti-pattern results
            
        Returns:
            Overall severity score (0.0-1.0)
        """
        total_severity = 0.0
        weighted_count = 0
        
        # Define weights for different anti-patterns
        weights = {
            "tight_coupling": 0.5,
            "dependency_cycle": 0.5,
            # Default weight for any other anti-patterns
            "default": 0.1
        }
        
        for name, results in anti_patterns.items():
            severity = results.get("severity", 0.0)
            weight = weights.get(name, weights["default"])
            
            total_severity += severity * weight
            weighted_count += weight
        
        if weighted_count > 0:
            return total_severity / weighted_count
        else:
            return 0.0
    
    def _generate_summary(self, anti_patterns: Dict, overall_severity: float) -> str:
        """Generate a summary of the architectural anti-pattern analysis.
        
        Args:
            anti_patterns: Dictionary of anti-pattern results
            overall_severity: Overall severity score
            
        Returns:
            A human-readable summary of the architectural anti-pattern analysis
        """
        if overall_severity < 0.1:
            return "No significant architectural anti-patterns detected. The codebase demonstrates good architectural design."
        
        # Count the number of anti-patterns with significant severity
        significant_count = sum(1 for results in anti_patterns.values() 
                               if results.get("severity", 0.0) >= 0.3)
        
        if overall_severity >= 0.7:
            severity_desc = "severe"
        elif overall_severity >= 0.4:
            severity_desc = "moderate"
        else:
            severity_desc = "minor"
            
        # Build the summary
        summary = f"The codebase exhibits {severity_desc} architectural anti-patterns. "
        
        # Add details about the most severe anti-patterns
        severe_patterns = sorted(
            [(name, results) for name, results in anti_patterns.items() 
             if results.get("severity", 0.0) >= 0.3],
            key=lambda x: x[1].get("severity", 0.0),
            reverse=True
        )
        
        if severe_patterns:
            summary += "The most concerning issues are: "
            pattern_descs = []
            
            for name, results in severe_patterns[:2]:  # Show top 2
                pattern_descs.append(
                    f"{name.replace('_', ' ').title()} "
                    f"({int(results.get('severity', 0.0) * 100)}% severity)"
                )
                
            summary += ", ".join(pattern_descs)
            
            if len(severe_patterns) > 2:
                summary += f", and {len(severe_patterns) - 2} more."
            else:
                summary += "."
        
        return summary
    
    def _generate_recommendations(self, anti_patterns: Dict, overall_severity: float) -> List[str]:
        """Generate recommendations for addressing architectural anti-patterns.
        
        Args:
            anti_patterns: Dictionary of anti-pattern results
            overall_severity: Overall severity score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Collect recommendations from individual anti-patterns
        for name, results in anti_patterns.items():
            severity = results.get("severity", 0.0)
            pattern_recommendations = results.get("recommendations", [])
            
            # Only include recommendations for significant anti-patterns
            if severity >= 0.3 and pattern_recommendations:
                # Add the top 1-2 recommendations from each significant anti-pattern
                for rec in pattern_recommendations[:2]:
                    recommendations.append(rec)
        
        # Add overall recommendations based on severity
        if overall_severity >= 0.7:
            recommendations.insert(0, 
                "Consider a significant architectural refactoring to address the severe anti-patterns"
            )
        elif overall_severity >= 0.4:
            recommendations.insert(0,
                "Address the most severe anti-patterns first to improve architectural quality"
            )
        elif recommendations:
            recommendations.insert(0,
                "Continue monitoring these anti-patterns to prevent architectural degradation"
            )
            
        return recommendations