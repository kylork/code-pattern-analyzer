"""
Hexagonal Architecture (Ports and Adapters) pattern detector.

This module provides a pattern detector for identifying the Hexagonal Architecture
style in codebases, also known as Ports and Adapters pattern.
"""

from typing import Dict, List, Optional, Set, Counter, Any
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from ...pattern_base import Pattern, CompositePattern
from ..architectural_intents.separation_of_concerns import SeparationOfConcernsIntent
from ..architectural_intents.information_hiding import InformationHidingIntent
from ..architectural_intents.dependency_inversion import DependencyInversionIntent
from .architectural_style_base import ArchitecturalStylePattern

logger = logging.getLogger(__name__)

class HexagonalArchitecturePattern(ArchitecturalStylePattern):
    """Pattern for detecting Hexagonal (Ports and Adapters) Architecture.
    
    This pattern identifies codebases that follow the Hexagonal Architecture style,
    which emphasizes:
    
    1. A domain-centric approach with a clear core domain model
    2. Ports (interfaces) that define how the core interacts with the outside
    3. Adapters that implement the ports to connect to external systems
    4. Dependency rules ensuring the core doesn't depend on external systems
    """
    
    def __init__(self):
        """Initialize the Hexagonal Architecture detector."""
        super().__init__(
            name="hexagonal_architecture",
            description="Identifies Hexagonal (Ports and Adapters) Architecture",
            languages=["python", "javascript", "typescript", "java"],
        )
        
        # Component type classifications
        self.domain_components = set()
        self.port_components = set()
        self.adapter_components = set()
        self.infrastructure_components = set()
        
        # Naming indicators for hexagonal architecture components
        self.domain_indicators = [
            r'domain', r'model', r'entity', r'core',
            r'business', r'service', r'application'
        ]
        
        self.port_indicators = [
            r'port', r'interface', r'boundary', r'contract',
            r'repository', r'service', r'gateway'
        ]
        
        self.adapter_indicators = [
            r'adapter', r'impl', r'implementation', r'infra',
            r'persistence', r'rest', r'api', r'controller',
            r'repository', r'dao'
        ]
        
        self.infrastructure_indicators = [
            r'infra', r'infrastructure', r'config', r'configuration',
            r'security', r'framework', r'persistence', r'database',
            r'messaging', r'notification'
        ]
    
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Hexagonal Architecture, we're looking for:
        1. Domain components (core business logic)
        2. Port interfaces (abstractions)
        3. Adapter implementations (concrete implementations of interfaces)
        
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
            
            # Determine the component type based on path and content
            component_type = self._classify_component(component_name, path_parts, match)
            
            # Add component node to graph
            self.component_graph.add_node(
                component_name,
                type='component',
                component_type=component_type,
                defines_interface=match.get('interfaces', {}).get('defines_interface', 
                                      match.get('abstractions', {}).get('defines_interface', False)),
                implements_interface=match.get('interfaces', {}).get('implements_interface', 
                                        match.get('abstractions', {}).get('implements_interface', False)),
                layer=match.get('layer', None),
                dependencies=match.get('imports', []),
                di_score=match.get('dip_score', 0.0),
                info_hiding_score=match.get('info_hiding_score', 0.0),
            )
            
            # Track component by type
            if component_type == 'domain':
                self.domain_components.add(component_name)
            elif component_type == 'port':
                self.port_components.add(component_name)
            elif component_type == 'adapter':
                self.adapter_components.add(component_name)
            elif component_type == 'infrastructure':
                self.infrastructure_components.add(component_name)
            
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
    
    def _classify_component(self, file_path: str, path_parts: List[str], match: Dict) -> str:
        """Classify the component as domain, port, adapter or infrastructure.
        
        Args:
            file_path: Path to the file
            path_parts: List of path segments
            match: The pattern match data
            
        Returns:
            Component type classification
        """
        # Check for interface definitions first
        defines_interface = match.get('interfaces', {}).get('defines_interface', 
                                 match.get('abstractions', {}).get('defines_interface', False))
        implements_interface = match.get('interfaces', {}).get('implements_interface', 
                                     match.get('abstractions', {}).get('implements_interface', False))
        
        # Convert file path to string for pattern matching
        file_path_str = str(file_path).lower()
        
        # Check for domain components
        for indicator in self.domain_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                # Don't classify as domain if it's clearly an adapter
                if any(re.search(a, file_path_str, re.IGNORECASE) for a in self.adapter_indicators):
                    continue
                return 'domain'
        
        # Check for port components (interfaces)
        is_port = False
        if defines_interface:
            is_port = True
        else:
            for indicator in self.port_indicators:
                if re.search(indicator, file_path_str, re.IGNORECASE):
                    is_port = True
                    break
        
        if is_port and not implements_interface:
            return 'port'
        
        # Check for adapter components
        for indicator in self.adapter_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return 'adapter'
        
        # Check for infrastructure components
        for indicator in self.infrastructure_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return 'infrastructure'
        
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
        """Analyze the component graph for Hexagonal Architecture style.
        
        We detect:
        1. Domain components and their isolation
        2. Port interfaces and their usage
        3. Adapter implementations
        4. Dependency direction (domain should not depend on adapters)
        
        Returns:
            A dictionary containing the hexagonal architecture analysis
        """
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Calculate component type distributions
        total_components = len(self.component_graph.nodes)
        domain_count = len(self.domain_components)
        port_count = len(self.port_components)
        adapter_count = len(self.adapter_components)
        infra_count = len(self.infrastructure_components)
        unknown_count = total_components - domain_count - port_count - adapter_count - infra_count
        
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
            "domain_component_count": domain_count,
            "port_component_count": port_count,
            "adapter_component_count": adapter_count,
            "infrastructure_component_count": infra_count,
            "unknown_component_count": unknown_count,
            "domain_ratio": domain_count / total_components if total_components > 0 else 0,
            "port_ratio": port_count / total_components if total_components > 0 else 0,
            "adapter_ratio": adapter_count / total_components if total_components > 0 else 0,
            "infrastructure_ratio": infra_count / total_components if total_components > 0 else 0,
            "separation_of_concerns_score": soc_score,
            "information_hiding_score": info_hiding_score,
            "dependency_inversion_score": dip_score,
        }
        
        # Calculate dependency directions
        inward_dependencies = 0
        outward_dependencies = 0
        correct_dependencies = 0
        incorrect_dependencies = 0
        
        for source, target in self.component_graph.edges:
            source_type = self.component_graph.nodes[source].get('component_type', 'unknown')
            target_type = self.component_graph.nodes[target].get('component_type', 'unknown')
            
            # Calculate inward/outward dependencies related to domain
            if source_type == 'domain':
                outward_dependencies += 1
            elif target_type == 'domain':
                inward_dependencies += 1
                
            # Check dependency direction correctness
            if source_type == 'adapter' and target_type == 'port':
                correct_dependencies += 1
            elif source_type == 'domain' and target_type == 'port':
                correct_dependencies += 1
            elif source_type == 'adapter' and target_type == 'domain':
                incorrect_dependencies += 1
            
        total_dependencies = self.component_graph.number_of_edges()
        if total_dependencies > 0:
            metrics["correct_dependency_ratio"] = correct_dependencies / total_dependencies
            metrics["incorrect_dependency_ratio"] = incorrect_dependencies / total_dependencies
        else:
            metrics["correct_dependency_ratio"] = 0
            metrics["incorrect_dependency_ratio"] = 0
            
        # Calculate hexagonal architecture confidence score
        confidence = self._calculate_hexagonal_confidence(metrics)
        
        # Generate description
        description = self._generate_description(metrics, confidence)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, confidence)
        
        # Extract component details
        components = []
        for node in self.component_graph.nodes:
            component_type = self.component_graph.nodes[node].get('component_type', 'unknown')
            
            # Only include classified components
            if component_type != 'unknown':
                components.append({
                    "name": node,
                    "type": component_type,
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
    
    def _calculate_hexagonal_confidence(self, metrics: Dict) -> float:
        """Calculate confidence score for hexagonal architecture.
        
        Args:
            metrics: Architecture metrics
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Key indicators for hexagonal architecture
        factors = [
            # Must have ports (interfaces)
            0.25 * min(1.0, metrics["port_ratio"] * 5),
            
            # Must have domain components
            0.25 * min(1.0, metrics["domain_ratio"] * 3),
            
            # Must have adapters
            0.2 * min(1.0, metrics["adapter_ratio"] * 3),
            
            # Correct dependency direction
            0.2 * metrics.get("correct_dependency_ratio", 0),
            
            # Strong information hiding
            0.05 * metrics["information_hiding_score"],
            
            # Strong dependency inversion
            0.05 * metrics["dependency_inversion_score"]
        ]
        
        # Calculate weighted score
        confidence = sum(factors)
        
        # Penalty for incorrect dependencies
        confidence -= 0.2 * metrics.get("incorrect_dependency_ratio", 0)
        
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
        desc = f"The codebase shows {confidence_desc} evidence of Hexagonal Architecture (Ports and Adapters). "
        
        # Add component details
        desc += f"Analysis identified {metrics['domain_component_count']} domain components, "
        desc += f"{metrics['port_component_count']} ports (interfaces), and "
        desc += f"{metrics['adapter_component_count']} adapters. "
        
        # Add dependency direction
        if metrics.get("correct_dependency_ratio", 0) > 0.7:
            desc += "Dependencies flow correctly with adapters depending on ports, showing good adherence to hexagonal principles. "
        elif metrics.get("correct_dependency_ratio", 0) > 0.4:
            desc += "Some dependencies flow correctly, but there are areas where hexagonal principles are not followed. "
        else:
            desc += "Dependency flow does not follow hexagonal architecture principles well. "
        
        # Add overall assessment
        if confidence > 0.7:
            desc += "The codebase demonstrates a deliberate implementation of the Hexagonal Architecture pattern."
        elif confidence > 0.4:
            desc += "The codebase shows partial implementation of Hexagonal Architecture concepts but could be improved."
        else:
            desc += "The codebase shows only superficial resemblance to Hexagonal Architecture."
            
        return desc
    
    def _generate_recommendations(self, metrics: Dict, confidence: float) -> List[str]:
        """Generate recommendations for improving hexagonal architecture.
        
        Args:
            metrics: The metrics dictionary
            confidence: Confidence score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Only generate recommendations if confidence is below excellent
        if confidence < 0.8:
            # Domain recommendations
            if metrics["domain_ratio"] < 0.2:
                recommendations.append(
                    "Create a clear domain model at the core of your application"
                )
                
            # Port recommendations
            if metrics["port_component_count"] < 3 or metrics["port_ratio"] < 0.1:
                recommendations.append(
                    "Define more port interfaces to abstract interactions between domain and external systems"
                )
                
            # Adapter recommendations
            if metrics["adapter_component_count"] < metrics["port_component_count"]:
                recommendations.append(
                    "Implement adapters for each port to connect to external systems"
                )
                
            # Dependency direction recommendations
            if metrics.get("incorrect_dependency_ratio", 0) > 0.2:
                recommendations.append(
                    "Fix dependency direction: domain should depend on ports, and adapters should implement ports"
                )
                
            # Information hiding recommendations
            if metrics["information_hiding_score"] < 0.6:
                recommendations.append(
                    "Improve information hiding with better encapsulation and interface usage"
                )
                
            # Dependency inversion recommendations
            if metrics["dependency_inversion_score"] < 0.6:
                recommendations.append(
                    "Apply dependency inversion to ensure the domain depends only on abstractions"
                )
        
        return recommendations