"""
Architectural Erosion anti-pattern detector.

This module provides a pattern detector for identifying architectural erosion,
where the actual implementation diverges from the intended architecture.
"""

from typing import Dict, List, Optional, Set, Counter
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from .architectural_anti_pattern_base import ArchitecturalAntiPattern

logger = logging.getLogger(__name__)

class ArchitecturalErosionAntiPattern(ArchitecturalAntiPattern):
    """Pattern for detecting the Architectural Erosion anti-pattern.
    
    This anti-pattern occurs when the implemented architecture diverges from the
    intended design, leading to:
    
    1. Violation of architectural boundaries
    2. Deterioration of the intended structure over time
    3. Increasing difficulty in maintaining the system
    4. Cross-cutting dependencies that bypass architectural layers/boundaries
    """
    
    def __init__(self):
        """Initialize the Architectural Erosion anti-pattern detector."""
        super().__init__(
            name="architectural_erosion",
            description="Identifies divergence between intended and actual architecture",
            languages=["python", "javascript", "typescript", "java", "go", "c#"],
        )
        
        # Erosion tracking
        self.boundary_violations = []
        self.cross_cutting_dependencies = []
        self.layer_bypass_dependencies = []
        
        # Metrics
        self.total_dependencies = 0
        self.architectural_violation_count = 0
        
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for architectural erosion.
        
        We detect:
        1. Violations of architectural boundaries
        2. Cross-cutting dependencies that bypass the intended structure
        3. Inconsistent dependencies that go against the primary architectural style
        
        Returns:
            A dictionary containing the architectural erosion analysis
        """
        # Skip analysis if no graph is available
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "severity": 0.0,
                "instances": [],
                "description": "No components to analyze"
            }
        
        # Reset erosion tracking
        self.boundary_violations = []
        self.cross_cutting_dependencies = []
        self.layer_bypass_dependencies = []
        self.total_dependencies = self.component_graph.number_of_edges()
        self.architectural_violation_count = 0
        
        # Extract the primary architectural style information
        primary_style = self.architectural_styles.get("primary_style", "unknown")
        primary_style_confidence = 0.0
        if primary_style != "unknown":
            style_info = self.architectural_styles.get("styles", {}).get(primary_style, {})
            primary_style_confidence = style_info.get("confidence", 0.0)
        
        # Analyze based on the primary architectural style
        if primary_style == "layered_architecture":
            self._analyze_layered_architecture_erosion()
        elif primary_style == "hexagonal_architecture":
            self._analyze_hexagonal_architecture_erosion()
        elif primary_style == "clean_architecture":
            self._analyze_clean_architecture_erosion()
        elif primary_style == "microservices":
            self._analyze_microservices_erosion()
        elif primary_style == "event_driven":
            self._analyze_event_driven_erosion()
        else:
            # Generic analysis for unknown architectural style
            self._analyze_generic_architectural_erosion()
        
        # Calculate overall severity
        erosion_instances = self.boundary_violations + self.cross_cutting_dependencies + self.layer_bypass_dependencies
        overall_severity = self._calculate_severity(erosion_instances, primary_style_confidence)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_severity, primary_style)
        
        return {
            "type": self.name,
            "severity": overall_severity,
            "instances": erosion_instances,
            "metrics": {
                "total_dependencies": self.total_dependencies,
                "architectural_violations": self.architectural_violation_count,
                "violation_ratio": self.architectural_violation_count / max(1, self.total_dependencies),
                "boundary_violations": len(self.boundary_violations),
                "cross_cutting_dependencies": len(self.cross_cutting_dependencies),
                "layer_bypass_dependencies": len(self.layer_bypass_dependencies),
                "primary_architectural_style": primary_style,
                "primary_style_confidence": primary_style_confidence
            },
            "description": self._generate_description(overall_severity, primary_style),
            "recommendations": recommendations,
            "visualization_data": self._generate_visualization_data()
        }
    
    def _analyze_layered_architecture_erosion(self):
        """Analyze erosion in a layered architecture.
        
        In a layered architecture, erosion typically means:
        1. Dependencies that go upward (from lower to higher layers)
        2. Dependencies that skip layers
        3. Dependencies that cross-cut across multiple layers
        """
        # Get layer information for each component
        component_layers = {}
        layer_order = ['presentation', 'business', 'data_access', 'domain']
        
        for node_id, node_data in self.component_graph.nodes(data=True):
            layer = node_data.get('layer', None)
            if layer in layer_order:
                component_layers[node_id] = layer
        
        # Check for layer violations in dependencies
        for source, target in self.component_graph.edges:
            source_layer = component_layers.get(source)
            target_layer = component_layers.get(target)
            
            if source_layer and target_layer:
                source_idx = layer_order.index(source_layer) if source_layer in layer_order else -1
                target_idx = layer_order.index(target_layer) if target_layer in layer_order else -1
                
                if source_idx >= 0 and target_idx >= 0:
                    # Check for upward dependencies (erosion)
                    if target_idx < source_idx:
                        self.boundary_violations.append({
                            "type": "upward_dependency",
                            "source": source,
                            "source_layer": source_layer,
                            "target": target,
                            "target_layer": target_layer,
                            "severity": 0.8,
                            "description": f"Upward dependency from {os.path.basename(source)} ({source_layer}) to {os.path.basename(target)} ({target_layer})"
                        })
                        self.architectural_violation_count += 1
                    
                    # Check for layer-skipping dependencies
                    elif target_idx > source_idx + 1:
                        self.layer_bypass_dependencies.append({
                            "type": "layer_skip",
                            "source": source,
                            "source_layer": source_layer,
                            "target": target,
                            "target_layer": target_layer,
                            "severity": 0.5,
                            "description": f"Layer-skipping dependency from {os.path.basename(source)} ({source_layer}) to {os.path.basename(target)} ({target_layer})"
                        })
                        self.architectural_violation_count += 1
    
    def _analyze_hexagonal_architecture_erosion(self):
        """Analyze erosion in a hexagonal architecture.
        
        In a hexagonal architecture, erosion typically means:
        1. Domain components depending on adapters
        2. Adapters bypassing ports (interfaces)
        3. Direct dependencies between adapters
        """
        # Get component types for each node
        component_types = {}
        
        for node_id, node_data in self.component_graph.nodes(data=True):
            component_type = node_data.get('component_type', None)
            if component_type:
                component_types[node_id] = component_type
        
        # Check for hexagonal architecture violations
        for source, target in self.component_graph.edges:
            source_type = component_types.get(source)
            target_type = component_types.get(target)
            
            if source_type and target_type:
                # Domain should not depend on adapters
                if source_type == 'domain' and target_type == 'adapter':
                    self.boundary_violations.append({
                        "type": "domain_to_adapter",
                        "source": source,
                        "source_type": source_type,
                        "target": target,
                        "target_type": target_type,
                        "severity": 0.9,
                        "description": f"Domain component {os.path.basename(source)} directly depends on adapter {os.path.basename(target)}"
                    })
                    self.architectural_violation_count += 1
                
                # Domain should depend on ports, not other domains
                elif source_type == 'domain' and target_type == 'domain':
                    # This might be acceptable in some cases, but worth flagging as a potential issue
                    self.cross_cutting_dependencies.append({
                        "type": "domain_to_domain",
                        "source": source,
                        "source_type": source_type,
                        "target": target,
                        "target_type": target_type,
                        "severity": 0.3,
                        "description": f"Domain component {os.path.basename(source)} directly depends on domain component {os.path.basename(target)}"
                    })
                    self.architectural_violation_count += 1
                
                # Adapters should not depend directly on other adapters
                elif source_type == 'adapter' and target_type == 'adapter':
                    self.cross_cutting_dependencies.append({
                        "type": "adapter_to_adapter",
                        "source": source,
                        "source_type": source_type,
                        "target": target,
                        "target_type": target_type,
                        "severity": 0.6,
                        "description": f"Adapter {os.path.basename(source)} directly depends on adapter {os.path.basename(target)}"
                    })
                    self.architectural_violation_count += 1
    
    def _analyze_clean_architecture_erosion(self):
        """Analyze erosion in a clean architecture.
        
        In clean architecture, erosion typically means:
        1. Inner circles depending on outer circles
        2. Dependencies that bypass the dependency rule
        3. Use cases depending directly on frameworks or infrastructure
        """
        # For now, simplify by reusing the hexagonal architecture analysis
        # since clean architecture follows similar principles
        self._analyze_hexagonal_architecture_erosion()
    
    def _analyze_microservices_erosion(self):
        """Analyze erosion in a microservices architecture.
        
        In microservices, erosion typically means:
        1. Direct dependencies between services (bypassing APIs)
        2. Shared database accesses
        3. Tight coupling between services
        """
        # This would require more context about service boundaries
        # For now, implement a generic version focused on excessive dependencies
        self._analyze_generic_architectural_erosion()
    
    def _analyze_event_driven_erosion(self):
        """Analyze erosion in an event-driven architecture.
        
        In event-driven architecture, erosion typically means:
        1. Direct dependencies between components (bypassing events)
        2. Synchronous calls where events should be used
        3. Components being aware of event handling implementation details
        """
        # This would require more context about event boundaries
        # For now, implement a generic version focused on excessive dependencies
        self._analyze_generic_architectural_erosion()
    
    def _analyze_generic_architectural_erosion(self):
        """Generic analysis for architectural erosion without a specific style.
        
        This looks for:
        1. High coupling between components
        2. Circular dependencies
        3. Highly coupled components with many outgoing dependencies
        """
        # Build a component dependency count
        outgoing_deps = defaultdict(int)
        incoming_deps = defaultdict(int)
        
        for source, target in self.component_graph.edges:
            outgoing_deps[source] += 1
            incoming_deps[target] += 1
        
        # Flag components with excessive outgoing dependencies
        threshold = 5  # Arbitrary threshold for demonstration
        for component, count in outgoing_deps.items():
            if count > threshold:
                self.boundary_violations.append({
                    "type": "excessive_dependencies",
                    "component": component,
                    "dependency_count": count,
                    "severity": min(0.9, 0.4 + (count - threshold) * 0.05),
                    "description": f"Component {os.path.basename(component)} has {count} outgoing dependencies"
                })
                self.architectural_violation_count += 1
        
        # Find circular dependencies
        try:
            # Use NetworkX to find simple cycles
            cycles = list(nx.simple_cycles(self.component_graph))
            
            for cycle in cycles:
                if len(cycle) >= 2:
                    cycle_desc = " → ".join([os.path.basename(c) for c in cycle] + [os.path.basename(cycle[0])])
                    self.cross_cutting_dependencies.append({
                        "type": "circular_dependency",
                        "components": cycle,
                        "severity": min(0.9, 0.5 + len(cycle) * 0.1),
                        "description": f"Circular dependency found: {cycle_desc}"
                    })
                    self.architectural_violation_count += 1
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
    
    def _calculate_severity(self, erosion_instances: List[Dict], primary_style_confidence: float) -> float:
        """Calculate the overall severity of architectural erosion.
        
        Args:
            erosion_instances: List of erosion instances found
            primary_style_confidence: Confidence score of the primary architectural style
            
        Returns:
            Severity score (0.0-1.0)
        """
        if not erosion_instances:
            return 0.0
        
        # Calculate average severity of detected instances
        total_severity = sum(instance.get("severity", 0.0) for instance in erosion_instances)
        avg_severity = total_severity / len(erosion_instances) if erosion_instances else 0.0
        
        # Consider the ratio of violations to total dependencies
        violation_ratio = min(1.0, self.architectural_violation_count / max(1, self.total_dependencies))
        
        # Consider the strength of the primary architectural style
        # If the primary style is very confident, violations are more severe
        style_factor = 0.5 + (primary_style_confidence * 0.5)
        
        # Calculate weighted severity
        severity = (0.5 * avg_severity + 0.3 * violation_ratio) * style_factor
        
        return min(1.0, severity)
    
    def _generate_description(self, severity: float, primary_style: str) -> str:
        """Generate a description of the architectural erosion anti-pattern.
        
        Args:
            severity: Overall severity score
            primary_style: Primary architectural style
            
        Returns:
            Human-readable description
        """
        if severity < 0.3:
            return f"The codebase shows minimal signs of architectural erosion. The {primary_style.replace('_', ' ')} architecture is well-maintained."
        
        violation_count = self.architectural_violation_count
        violation_ratio = self.architectural_violation_count / max(1, self.total_dependencies)
        violation_percent = int(violation_ratio * 100)
        
        style_name = primary_style.replace('_', ' ').title() if primary_style != "unknown" else "intended"
        
        if severity >= 0.7:
            return (
                f"The codebase exhibits significant architectural erosion, with {violation_count} violations "
                f"({violation_percent}% of dependencies) that contradict the {style_name} architecture. "
                f"These violations have substantially degraded the architectural integrity, "
                f"making the system harder to maintain and evolve."
            )
        elif severity >= 0.5:
            return (
                f"The codebase shows moderate architectural erosion, with {violation_count} violations "
                f"({violation_percent}% of dependencies) that contradict the {style_name} architecture. "
                f"These violations are degrading the architectural integrity and may lead to maintainability issues."
            )
        else:
            return (
                f"The codebase has some signs of architectural erosion, with {violation_count} violations "
                f"({violation_percent}% of dependencies) that contradict the {style_name} architecture. "
                f"While limited in scope, these violations should be addressed to maintain architectural integrity."
            )
    
    def _generate_recommendations(self, severity: float, primary_style: str) -> List[str]:
        """Generate recommendations for addressing architectural erosion.
        
        Args:
            severity: Overall severity score
            primary_style: Primary architectural style
            
        Returns:
            List of recommendations
        """
        if severity < 0.3:
            return ["Continue to maintain the architectural integrity of the codebase."]
        
        recommendations = []
        
        # Basic recommendations for all architectural styles
        recommendations.append(
            "Create and document clear architectural boundaries, rules, and constraints"
        )
        
        # Add recommendations based on severity
        if severity >= 0.7:
            recommendations.insert(0, 
                "Consider a major architectural refactoring to restore the intended structure"
            )
            
            recommendations.append(
                "Implement regular architecture compliance checks in your CI/CD pipeline"
            )
            
            recommendations.append(
                "Hold architecture review sessions for significant changes to prevent further erosion"
            )
        elif severity >= 0.5:
            recommendations.append(
                "Create a prioritized plan to address the most severe architectural violations first"
            )
            
            recommendations.append(
                "Increase awareness of the intended architecture and its rules among the development team"
            )
        
        # Add style-specific recommendations
        if primary_style == "layered_architecture":
            # Check for layer violations
            if self.layer_bypass_dependencies:
                recommendations.append(
                    "Fix layer-skipping dependencies by introducing proper intermediate abstractions"
                )
            
            # Check for upward dependencies
            if self.boundary_violations:
                recommendations.append(
                    "Fix upward dependencies that violate the layered architecture's top-down structure"
                )
                
        elif primary_style == "hexagonal_architecture" or primary_style == "clean_architecture":
            # Check for domain-to-adapter dependencies
            domain_to_adapter_violations = [v for v in self.boundary_violations if v.get("type") == "domain_to_adapter"]
            if domain_to_adapter_violations:
                recommendations.append(
                    "Fix domain components that depend directly on adapters by introducing ports/interfaces"
                )
            
            # Check for adapter-to-adapter dependencies
            adapter_to_adapter_violations = [v for v in self.cross_cutting_dependencies if v.get("type") == "adapter_to_adapter"]
            if adapter_to_adapter_violations:
                recommendations.append(
                    "Eliminate direct dependencies between adapters by communicating through the domain"
                )
        
        # Add general architectural recommendations
        recommendations.append(
            "Introduce architectural fitness functions to detect architectural erosion automatically"
        )
        
        return recommendations
    
    def _generate_visualization_data(self) -> Dict:
        """Generate data for visualizing architectural erosion.
        
        Returns:
            A dictionary with visualization data
        """
        nodes = []
        edges = []
        
        # Set of components involved in violations
        violation_components = set()
        for violation in self.boundary_violations + self.cross_cutting_dependencies + self.layer_bypass_dependencies:
            if "source" in violation:
                violation_components.add(violation["source"])
            if "target" in violation:
                violation_components.add(violation["target"])
            if "components" in violation:
                violation_components.update(violation["components"])
        
        # Create nodes for each component
        for node_id, node_data in self.component_graph.nodes(data=True):
            # Determine if node is involved in a violation
            in_violation = node_id in violation_components
            
            # Get layer or component type
            component_category = node_data.get('layer', node_data.get('component_type', 'unknown'))
            
            nodes.append({
                "id": node_id,
                "label": os.path.basename(node_id),
                "in_violation": in_violation,
                "category": component_category
            })
        
        # Create edges for dependencies
        for source, target, edge_data in self.component_graph.edges(data=True):
            # Check if this edge is a violation
            is_violation = False
            violation_type = "none"
            
            # Check different types of violations
            for violation in self.boundary_violations:
                if violation.get("source") == source and violation.get("target") == target:
                    is_violation = True
                    violation_type = violation.get("type", "boundary_violation")
                    break
                    
            if not is_violation:
                for violation in self.cross_cutting_dependencies:
                    if violation.get("source") == source and violation.get("target") == target:
                        is_violation = True
                        violation_type = violation.get("type", "cross_cutting")
                        break
            
            if not is_violation:
                for violation in self.layer_bypass_dependencies:
                    if violation.get("source") == source and violation.get("target") == target:
                        is_violation = True
                        violation_type = violation.get("type", "layer_bypass")
                        break
                        
            edges.append({
                "source": source,
                "target": target,
                "is_violation": is_violation,
                "violation_type": violation_type
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "violations": self.boundary_violations + self.cross_cutting_dependencies + self.layer_bypass_dependencies
        }