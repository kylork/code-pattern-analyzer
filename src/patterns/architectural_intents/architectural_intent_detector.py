"""
Architectural intent detector composite pattern.

This module provides a composite pattern that aggregates multiple
architectural intent detectors.
"""

from typing import Dict, List, Optional
import logging

from ...pattern_base import CompositePattern
from .separation_of_concerns import SeparationOfConcernsIntent
from .information_hiding import InformationHidingIntent
from .dependency_inversion import DependencyInversionIntent

logger = logging.getLogger(__name__)

class ArchitecturalIntentDetector(CompositePattern):
    """A composite pattern for detecting architectural intents.
    
    This pattern combines multiple architectural intent patterns to
    provide a comprehensive analysis of the architectural design
    decisions in a codebase.
    """
    
    def __init__(self):
        """Initialize an architectural intent detector composite pattern."""
        super().__init__(
            name="architectural_intent",
            description="Identifies architectural intents and design decisions across a codebase",
            patterns=[
                SeparationOfConcernsIntent(),
                InformationHidingIntent(),
                DependencyInversionIntent(),
                # Add more architectural intent patterns here as they are implemented
                # etc.
            ],
        )
    
    def analyze_codebase(self, 
                        results: List[Dict],
                        codebase_root: Optional[str] = None) -> Dict:
        """Analyze architectural intents across a codebase.
        
        This method delegates to the sub-patterns' analyze_architecture methods
        to build a comprehensive understanding of the architectural intents.
        
        Args:
            results: List of results from analyzing individual files
            codebase_root: The root directory of the codebase
            
        Returns:
            A dictionary containing the detected architectural intents
        """
        architectural_intents = {}
        
        # Process each sub-pattern
        for pattern in self.patterns:
            # Only process architectural intent patterns
            if hasattr(pattern, 'analyze_architecture'):
                intent_name = pattern.name
                intent_results = pattern.analyze_architecture(results, codebase_root)
                architectural_intents[intent_name] = intent_results
        
        # Calculate overall architectural health score
        # This is a simple weighted average of the confidence scores
        # In a full implementation, this would be more sophisticated
        intent_weights = {
            'separation_of_concerns': 0.4,  # High importance
            'information_hiding': 0.3,      # High importance
            'dependency_inversion': 0.3,    # High importance
            # Add weights for other intents as they are implemented
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for intent_name, results in architectural_intents.items():
            if intent_name in intent_weights and 'confidence' in results:
                weight = intent_weights.get(intent_name, 1.0)
                weighted_sum += results['confidence'] * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Create the overall analysis
        return {
            "architectural_score": overall_score,
            "intents": architectural_intents,
            "summary": self._generate_summary(architectural_intents, overall_score)
        }
    
    def _generate_summary(self, 
                         architectural_intents: Dict,
                         overall_score: float) -> str:
        """Generate a summary of the architectural analysis.
        
        Args:
            architectural_intents: Dictionary of architectural intent results
            overall_score: Overall architectural health score
            
        Returns:
            A human-readable summary of the architectural analysis
        """
        # Format the overall score as a percentage
        score_percent = int(overall_score * 100)
        
        # Determine the health description
        health_description = "excellent" if overall_score > 0.8 else \
                             "good" if overall_score > 0.6 else \
                             "moderate" if overall_score > 0.4 else \
                             "poor" if overall_score > 0.2 else "concerning"
        
        # Start with the overall assessment
        summary = f"The codebase demonstrates {health_description} architectural health ({score_percent}%)."
        
        # Add intent-specific summaries
        for intent_name, results in architectural_intents.items():
            if 'description' in results:
                summary += f" {results['description']}"
        
        # Add architectural recommendations
        if overall_score < 0.8:
            summary += " Consider the following architectural improvements:"
            
            # Add specific recommendations based on the results
            if 'separation_of_concerns' in architectural_intents:
                soc_results = architectural_intents['separation_of_concerns']
                
                # Layer-based recommendations
                if soc_results.get('primary_pattern') == 'layer-based':
                    layer_score = soc_results.get('layer_analysis', {}).get('clean_layering_score', 0)
                    if layer_score < 0.7:
                        summary += " Improve layer separation by enforcing proper dependency direction between layers."
                
                # Domain-based recommendations
                elif soc_results.get('primary_pattern') == 'domain-based':
                    isolation_score = soc_results.get('domain_analysis', {}).get('domain_isolation_score', 0)
                    if isolation_score < 0.7:
                        summary += " Reduce cross-domain coupling by introducing domain boundaries and limiting direct dependencies."
                
                # No clear pattern recommendations
                elif soc_results.get('primary_pattern') == 'unknown':
                    summary += " Consider adopting a more explicit architectural pattern like layered architecture or domain-driven design."
                    
            # Add information hiding recommendations
            if 'information_hiding' in architectural_intents:
                info_hiding_results = architectural_intents['information_hiding']
                
                # Add recommendations from the information hiding analysis
                if 'recommendations' in info_hiding_results and info_hiding_results['recommendations']:
                    for recommendation in info_hiding_results['recommendations']:
                        summary += f" {recommendation}."
            
            # Add dependency inversion recommendations
            if 'dependency_inversion' in architectural_intents:
                dip_results = architectural_intents['dependency_inversion']
                
                # Add recommendations from the dependency inversion analysis
                if 'recommendations' in dip_results and dip_results['recommendations']:
                    for recommendation in dip_results['recommendations']:
                        summary += f" {recommendation}."
        
        return summary