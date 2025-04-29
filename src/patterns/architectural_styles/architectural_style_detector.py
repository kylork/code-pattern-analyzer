"""
Architectural style detector composite pattern.

This module provides a composite pattern that aggregates multiple architectural
style detectors to identify higher-level architectural approaches in codebases.
"""

from typing import Dict, List, Optional
import logging

from ...pattern_base import CompositePattern
from .hexagonal import HexagonalArchitecturePattern
from .clean_architecture import CleanArchitecturePattern
from .microservices import MicroservicesPattern
from .event_driven import EventDrivenPattern
from .layered import LayeredArchitecturePattern

logger = logging.getLogger(__name__)

class ArchitecturalStyleDetector(CompositePattern):
    """A composite pattern for detecting architectural styles.
    
    This pattern combines multiple architectural style patterns to
    provide a comprehensive analysis of the architectural approach
    used in a codebase.
    """
    
    def __init__(self):
        """Initialize an architectural style detector composite pattern."""
        super().__init__(
            name="architectural_style",
            description="Identifies higher-level architectural styles across a codebase",
            patterns=[
                HexagonalArchitecturePattern(),
                CleanArchitecturePattern(),
                MicroservicesPattern(),
                EventDrivenPattern(),
                LayeredArchitecturePattern(),
                # Add more architectural style patterns here as they are implemented
            ],
        )
    
    def analyze_codebase(self, 
                        results: List[Dict],
                        architectural_intents: Dict,
                        codebase_root: Optional[str] = None) -> Dict:
        """Analyze architectural styles across a codebase.
        
        This method delegates to the sub-patterns' analyze_architecture methods
        to build a comprehensive understanding of the architectural styles.
        
        Args:
            results: List of results from analyzing individual files
            architectural_intents: Results from architectural intent analysis
            codebase_root: The root directory of the codebase
            
        Returns:
            A dictionary containing the detected architectural styles
        """
        architectural_styles = {}
        
        # Process each sub-pattern
        for pattern in self.patterns:
            # Only process architectural style patterns
            if hasattr(pattern, 'analyze_architecture'):
                style_name = pattern.name
                style_results = pattern.analyze_architecture(results, architectural_intents, codebase_root)
                architectural_styles[style_name] = style_results
        
        # Calculate primary architectural style
        primary_style = self._determine_primary_style(architectural_styles)
        
        # Generate overall analysis
        return {
            "primary_style": primary_style,
            "styles": architectural_styles,
            "summary": self._generate_summary(architectural_styles, primary_style)
        }
    
    def _determine_primary_style(self, architectural_styles: Dict) -> str:
        """Determine the primary architectural style based on confidence scores.
        
        Args:
            architectural_styles: Dictionary of architectural style results
            
        Returns:
            The name of the primary architectural style, or "unknown"
        """
        primary_style = "unknown"
        highest_confidence = 0.0
        
        for style_name, results in architectural_styles.items():
            confidence = results.get('confidence', 0.0)
            if confidence > highest_confidence and confidence >= 0.4:  # Minimum threshold
                highest_confidence = confidence
                primary_style = style_name
                
        return primary_style
    
    def _generate_summary(self, 
                         architectural_styles: Dict,
                         primary_style: str) -> str:
        """Generate a summary of the architectural style analysis.
        
        Args:
            architectural_styles: Dictionary of architectural style results
            primary_style: The name of the primary architectural style
            
        Returns:
            A human-readable summary of the architectural style analysis
        """
        if primary_style == "unknown":
            return "No clear architectural style detected. The codebase may use a custom or hybrid architecture."
            
        # Get the primary style description
        primary_desc = architectural_styles[primary_style].get('description', '')
        
        # Generate a summary of all detected styles
        style_summaries = []
        for style_name, results in architectural_styles.items():
            confidence = results.get('confidence', 0.0)
            if confidence >= 0.3 and style_name != primary_style:  # Secondary styles
                confidence_percent = int(confidence * 100)
                style_summaries.append(f"{style_name.replace('_', ' ').title()} ({confidence_percent}% confidence)")
                
        # Combine into final summary
        summary = primary_desc
        
        if style_summaries:
            summary += f" Additionally, the codebase shows elements of: {', '.join(style_summaries)}."
            
        # Add recommendations from primary style
        primary_recommendations = architectural_styles[primary_style].get('recommendations', [])
        if primary_recommendations:
            summary += " Key recommendations: "
            summary += "; ".join(primary_recommendations[:2])  # Just show top 2
            if len(primary_recommendations) > 2:
                summary += "."
                
        return summary