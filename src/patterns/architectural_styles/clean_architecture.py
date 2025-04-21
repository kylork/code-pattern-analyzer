"""
Clean Architecture pattern detector.

This module provides a pattern detector for identifying the Clean Architecture
style in codebases, as described by Robert C. Martin.
"""

from typing import Dict, List, Optional, Set, Counter
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from ...pattern_base import Pattern, CompositePattern
from .architectural_style_base import ArchitecturalStylePattern

logger = logging.getLogger(__name__)

class CleanArchitecturePattern(ArchitecturalStylePattern):
    """Pattern for detecting Clean Architecture.
    
    This pattern identifies codebases that follow the Clean Architecture style,
    which emphasizes:
    
    1. Independence of frameworks and external details
    2. Dependency rule: dependencies only point inward
    3. Clear layers: entities, use cases, interface adapters, frameworks
    """
    
    def __init__(self):
        """Initialize the Clean Architecture detector."""
        super().__init__(
            name="clean_architecture",
            description="Identifies Clean Architecture patterns",
            languages=["python", "javascript", "typescript", "java"],
        )
        
        # Component layer classifications
        self.entity_components = set()
        self.usecase_components = set()
        self.interface_adapter_components = set()
        self.framework_components = set()
        
        # Naming indicators for clean architecture layers
        self.entity_indicators = [
            r'entity', r'model', r'domain/model', r'core/entity',
            r'business/entity', r'domain/entity', r'enterprise'
        ]
        
        self.usecase_indicators = [
            r'usecase', r'use_case', r'interactor', r'application',
            r'service', r'domain/service', r'core/service'
        ]
        
        self.interface_adapter_indicators = [
            r'controller', r'presenter', r'gateway', r'adapter',
            r'repository', r'persistence/repository', r'api'
        ]
        
        self.framework_indicators = [
            r'framework', r'infra', r'infrastructure', r'platform',
            r'driver', r'external', r'persistence/driver', r'ui/web',
            r'web', r'rest', r'database', r'config'
        ]
    
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Clean Architecture, we're looking for:
        1. Entity components (core business rules)
        2. Use case components (application-specific business rules)
        3. Interface adapter components (convert data between layers)
        4. Framework components (external details)
        
        Args:
            pattern_name: The name of the pattern
            matches: List of pattern matches
            file_path: Path to the file
        """
        # Skip patterns that aren't relevant for architectural style detection
        if pattern_name not in ["separation_of_concerns", "information_hiding", 
                               "dependency_inversion", "architectural_intent"]:
            return
            
        for match in matches:
            # Each match represents a component
            component_name = match.get('path', file_path)
            
            # Skip if already processed
            if self.component_graph.has_node(component_name):
                continue
                
            # Extract info from the file path
            path_parts = self._get_path_parts(component_name)
            
            # Determine the component layer based on path and content
            layer = self._classify_layer(component_name, path_parts, match)
            
            # Add component node to graph
            self.component_graph.add_node(
                component_name,
                type='component',
                architecture_layer=layer,
                defines_interface=match.get('interfaces', {}).get('defines_interface', 
                                      match.get('abstractions', {}).get('defines_interface', False)),
                implements_interface=match.get('interfaces', {}).get('implements_interface', 
                                        match.get('abstractions', {}).get('implements_interface', False)),
                original_layer=match.get('layer', None),
                dependencies=match.get('imports', []),
                di_score=match.get('dip_score', 0.0),
                info_hiding_score=match.get('info_hiding_score', 0.0),
            )
            
            # Track component by layer
            if layer == 'entity':
                self.entity_components.add(component_name)
            elif layer == 'usecase':
                self.usecase_components.add(component_name)
            elif layer == 'interface_adapter':
                self.interface_adapter_components.add(component_name)
            elif layer == 'framework':
                self.framework_components.add(component_name)
            
            # Add dependencies if available
            if 'imports' in match:
                for dependency in match['imports']:
                    # Try to resolve relative paths or package references
                    dependency_path = self._resolve_dependency(component_name, dependency)
                    if dependency_path:
                        if not self.component_graph.has_node(dependency_path):
                            # Add placeholder node for now
                            self.component_graph.add_node(dependency_path, type='component')
                        
                        # Add dependency edge
                        self.component_graph.add_edge(component_name, dependency_path)
    
    def _get_path_parts(self, file_path: str) -> List[str]:
        """Extract meaningful parts from the file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of path segments
        """
        # Convert to Path object for easier manipulation
        path = Path(file_path)
        
        # Get path parts excluding the filename itself
        parts = list(path.parts)
        
        # Filter out common non-meaningful parts
        filtered_parts = [p.lower() for p in parts if p not in [
            '/', '.', 'src', 'source', 'app', 'main'
        ]]
        
        return filtered_parts
    
    def _classify_layer(self, file_path: str, path_parts: List[str], match: Dict) -> str:
        """Classify the component into a Clean Architecture layer.
        
        Args:
            file_path: Path to the file
            path_parts: List of path segments
            match: The pattern match data
            
        Returns:
            Clean Architecture layer
        """
        # Convert file path to string for pattern matching
        file_path_str = str(file_path).lower()
        
        # Check for entity layer
        for indicator in self.entity_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return 'entity'
        
        # Check for use case layer
        for indicator in self.usecase_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return 'usecase'
        
        # Check for interface adapter layer
        for indicator in self.interface_adapter_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return 'interface_adapter'
        
        # Check for framework layer
        for indicator in self.framework_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return 'framework'
        
        # Default to "unknown" if we can't classify
        return 'unknown'
    
    def _resolve_dependency(self, source_path: str, dependency: str) -> Optional[str]:
        """Resolve a dependency string to a file path.
        
        Args:
            source_path: Path to the source file
            dependency: Dependency string (import or package)
            
        Returns:
            Resolved file path or None if can't resolve
        """
        # This is a simplified implementation
        # In a real system, this would have more complex import resolution
        
        # For now, just check if the dependency is a node in our graph
        for node in self.component_graph.nodes:
            if dependency in node:
                return node
        
        # Try to construct a path based on the source path
        try:
            source_dir = os.path.dirname(source_path)
            possible_path = os.path.join(source_dir, dependency)
            if possible_path in self.component_graph.nodes:
                return possible_path
            
            # Add common extensions
            for ext in ['.py', '.js', '.ts', '.java']:
                if (possible_path + ext) in self.component_graph.nodes:
                    return possible_path + ext
        except:
            pass
            
        return None
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Clean Architecture style.
        
        We detect:
        1. Presence of the four layers
        2. Dependency direction (dependencies should point inward)
        3. Isolation of enterprise business rules (entities)
        
        Returns:
            A dictionary containing the clean architecture analysis
        """
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Calculate layer distributions
        total_components = len(self.component_graph.nodes)
        entity_count = len(self.entity_components)
        usecase_count = len(self.usecase_components)
        adapter_count = len(self.interface_adapter_components)
        framework_count = len(self.framework_components)
        unknown_count = total_components - entity_count - usecase_count - adapter_count - framework_count
        
        # Calculate architectural intent scores from previously analyzed results
        soc_score = 0.0
        if 'separation_of_concerns' in self.architectural_intents:
            soc_score = self.architectural_intents['separation_of_concerns'].get('confidence', 0.0)
            
        info_hiding_score = 0.0
        if 'information_hiding' in self.architectural_intents:
            info_hiding_score = self.architectural_intents['information_hiding'].get('confidence', 0.0)
            
        dip_score = 0.0
        if 'dependency_inversion' in self.architectural_intents:
            dip_score = self.architectural_intents['dependency_inversion'].get('confidence', 0.0)
        
        # Calculate metrics
        metrics = {
            "total_components": total_components,
            "entity_component_count": entity_count,
            "usecase_component_count": usecase_count,
            "adapter_component_count": adapter_count,
            "framework_component_count": framework_count,
            "unknown_component_count": unknown_count,
            "entity_ratio": entity_count / total_components if total_components > 0 else 0,
            "usecase_ratio": usecase_count / total_components if total_components > 0 else 0,
            "adapter_ratio": adapter_count / total_components if total_components > 0 else 0,
            "framework_ratio": framework_count / total_components if total_components > 0 else 0,
            "separation_of_concerns_score": soc_score,
            "information_hiding_score": info_hiding_score,
            "dependency_inversion_score": dip_score,
        }
        
        # Calculate dependency directions - dependencies should point inward
        # Framework -> Adapter -> Use case -> Entity
        correct_edges = 0
        incorrect_edges = 0
        layer_values = {
            'entity': 1,
            'usecase': 2,
            'interface_adapter': 3,
            'framework': 4,
            'unknown': 0
        }
        
        for source, target in self.component_graph.edges:
            source_layer = self.component_graph.nodes[source].get('architecture_layer', 'unknown')
            target_layer = self.component_graph.nodes[target].get('architecture_layer', 'unknown')
            
            source_value = layer_values.get(source_layer, 0)
            target_value = layer_values.get(target_layer, 0)
            
            # Skip if either layer is unknown
            if source_value == 0 or target_value == 0:
                continue
                
            # In Clean Architecture, dependencies should point inward (higher to lower value)
            if source_value > target_value:
                correct_edges += 1
            else:
                incorrect_edges += 1
                
        total_edges = correct_edges + incorrect_edges
        if total_edges > 0:
            metrics["dependency_direction_compliance"] = correct_edges / total_edges
        else:
            metrics["dependency_direction_compliance"] = 0
            
        # Calculate clean architecture confidence score
        confidence = self._calculate_clean_architecture_confidence(metrics)
        
        # Generate description
        description = self._generate_description(metrics, confidence)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, confidence)
        
        # Extract component details
        components = []
        for node in self.component_graph.nodes:
            layer = self.component_graph.nodes[node].get('architecture_layer', 'unknown')
            
            # Only include classified components
            if layer != 'unknown':
                components.append({
                    "name": node,
                    "layer": layer,
                    "defines_interface": self.component_graph.nodes[node].get('defines_interface', False),
                    "implements_interface": self.component_graph.nodes[node].get('implements_interface', False),
                })
        
        return {
            "type": self.name,
            "confidence": confidence,
            "components": components,
            "metrics": metrics,
            "recommendations": recommendations,
            "description": description
        }
    
    def _calculate_clean_architecture_confidence(self, metrics: Dict) -> float:
        """Calculate confidence score for clean architecture.
        
        Args:
            metrics: Architecture metrics
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Key indicators for clean architecture
        factors = [
            # Must have all four layers
            0.1 * min(1.0, metrics["entity_ratio"] * 5),
            0.1 * min(1.0, metrics["usecase_ratio"] * 5),
            0.1 * min(1.0, metrics["adapter_ratio"] * 5),
            0.1 * min(1.0, metrics["framework_ratio"] * 5),
            
            # Dependency direction is crucial
            0.3 * metrics.get("dependency_direction_compliance", 0),
            
            # Strong separation of concerns
            0.1 * metrics["separation_of_concerns_score"],
            
            # Strong information hiding
            0.1 * metrics["information_hiding_score"],
            
            # Strong dependency inversion
            0.1 * metrics["dependency_inversion_score"]
        ]
        
        # Calculate weighted score
        confidence = sum(factors)
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _generate_description(self, metrics: Dict, confidence: float) -> str:
        """Generate a description of the architectural style.
        
        Args:
            metrics: The metrics dictionary
            confidence: Confidence score
            
        Returns:
            Human-readable description
        """
        # Determine confidence level
        if confidence > 0.8:
            confidence_desc = "strong"
        elif confidence > 0.6:
            confidence_desc = "good"
        elif confidence > 0.4:
            confidence_desc = "moderate"
        elif confidence > 0.2:
            confidence_desc = "weak"
        else:
            confidence_desc = "minimal"
            
        # Build description
        desc = f"The codebase shows {confidence_desc} evidence of Clean Architecture. "
        
        # Add layer details
        desc += f"Analysis identified {metrics['entity_component_count']} entity components, "
        desc += f"{metrics['usecase_component_count']} use case components, "
        desc += f"{metrics['adapter_component_count']} interface adapter components, and "
        desc += f"{metrics['framework_component_count']} framework components. "
        
        # Add dependency direction
        compliance = metrics.get("dependency_direction_compliance", 0)
        if compliance > 0.8:
            desc += "Dependencies flow correctly inward (from outer to inner layers), showing excellent adherence to the dependency rule. "
        elif compliance > 0.6:
            desc += "Dependencies mostly flow inward, with some violations of the dependency rule. "
        else:
            desc += "Many dependencies violate the dependency rule, which is a core principle of Clean Architecture. "
        
        # Add overall assessment
        if confidence > 0.7:
            desc += "The codebase demonstrates a deliberate implementation of Clean Architecture."
        elif confidence > 0.4:
            desc += "The codebase shows partial implementation of Clean Architecture concepts but could be improved."
        else:
            desc += "The codebase shows only superficial resemblance to Clean Architecture."
            
        return desc
    
    def _generate_recommendations(self, metrics: Dict, confidence: float) -> List[str]:
        """Generate recommendations for improving clean architecture.
        
        Args:
            metrics: The metrics dictionary
            confidence: Confidence score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Only generate recommendations if confidence is below excellent
        if confidence < 0.8:
            # Layer recommendations
            if metrics["entity_ratio"] < 0.1:
                recommendations.append(
                    "Create a clear entity layer for core business rules"
                )
                
            if metrics["usecase_ratio"] < 0.1:
                recommendations.append(
                    "Define use cases that encapsulate application-specific business rules"
                )
                
            if metrics["adapter_ratio"] < 0.1:
                recommendations.append(
                    "Implement interface adapters to convert data between use cases and external systems"
                )
                
            if metrics["framework_ratio"] < 0.1:
                recommendations.append(
                    "Separate framework code into an outer layer to isolate external dependencies"
                )
                
            # Dependency direction recommendations
            compliance = metrics.get("dependency_direction_compliance", 0)
            if compliance < 0.7:
                recommendations.append(
                    "Fix dependency direction: dependencies should point inward toward the entity layer"
                )
                
            # Dependency inversion recommendation
            if metrics["dependency_inversion_score"] < 0.6:
                recommendations.append(
                    "Apply dependency inversion to ensure inner layers don't depend on outer layers"
                )
        
        return recommendations