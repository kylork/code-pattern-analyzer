"""
Dependency Cycle anti-pattern detector.

This module provides a pattern detector for identifying cyclic dependencies between components,
which violate good architectural principles and lead to maintainability issues.
"""

from typing import Dict, List, Optional, Set, Tuple
import logging
import os
import networkx as nx
from pathlib import Path
from collections import defaultdict

from .architectural_anti_pattern_base import ArchitecturalAntiPattern

logger = logging.getLogger(__name__)

class DependencyCycleAntiPattern(ArchitecturalAntiPattern):
    """Pattern for detecting the Dependency Cycle anti-pattern.
    
    This anti-pattern occurs when components form circular dependencies, leading to:
    
    1. Tight coupling between components in the cycle
    2. Difficulty understanding the component relationships
    3. Challenges in testing components independently
    4. Potential for infinite recursion or deadlocks
    5. Barrier to modular development and deployment
    """
    
    def __init__(self):
        """Initialize the Dependency Cycle anti-pattern detector."""
        super().__init__(
            name="dependency_cycle",
            description="Identifies circular dependencies between components",
            languages=["python", "javascript", "typescript", "java", "go", "c#"],
        )
        
        # Cycle tracking
        self.cycles = []
        self.components_in_cycles = set()
        
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for dependency cycles.
        
        We detect:
        1. Simple cycles (A -> B -> A)
        2. Complex cycles (A -> B -> C -> A)
        3. Components that participate in multiple cycles
        
        Returns:
            A dictionary containing the dependency cycle analysis
        """
        # Skip analysis if no graph is available
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "severity": 0.0,
                "instances": [],
                "description": "No components to analyze"
            }
        
        # Reset cycle tracking
        self.cycles = []
        self.components_in_cycles = set()
        
        # Find simple cycles
        try:
            # Use NetworkX to find simple cycles
            simple_cycles = list(nx.simple_cycles(self.component_graph))
            
            # Process each cycle
            for cycle in simple_cycles:
                if len(cycle) >= 2:  # Only consider cycles with at least 2 components
                    # Format cycle for reporting
                    cycle_info = {
                        "components": cycle,
                        "length": len(cycle),
                        "severity": min(1.0, 0.5 + (len(cycle) - 2) * 0.1),  # Larger cycles are worse
                        "description": self._format_cycle_description(cycle)
                    }
                    self.cycles.append(cycle_info)
                    
                    # Track components in cycles
                    for component in cycle:
                        self.components_in_cycles.add(component)
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
        
        # Sort cycles by severity
        self.cycles.sort(key=lambda x: x.get("severity", 0), reverse=True)
        
        # Calculate overall severity
        overall_severity = self._calculate_severity()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_severity)
        
        return {
            "type": self.name,
            "severity": overall_severity,
            "instances": self.cycles,
            "metrics": {
                "cycle_count": len(self.cycles),
                "components_in_cycles": len(self.components_in_cycles),
                "total_component_count": len(self.component_graph.nodes),
                "cycle_component_ratio": len(self.components_in_cycles) / len(self.component_graph.nodes) if self.component_graph.nodes else 0,
                "average_cycle_length": sum(c.get("length", 0) for c in self.cycles) / len(self.cycles) if self.cycles else 0,
                "max_cycle_length": max(c.get("length", 0) for c in self.cycles) if self.cycles else 0,
            },
            "description": self._generate_description(overall_severity),
            "recommendations": recommendations,
            "visualization_data": self._generate_visualization_data()
        }
    
    def _format_cycle_description(self, cycle: List[str]) -> str:
        """Format a cycle for human-readable description.
        
        Args:
            cycle: List of component identifiers in the cycle
            
        Returns:
            Human-readable description of the cycle
        """
        # Make cycle components more readable by using basenames
        readable_components = [os.path.basename(c) for c in cycle]
        
        # Add the first component to the end to show the complete cycle
        readable_components.append(readable_components[0])
        
        # Format as arrows
        return " → ".join(readable_components)
    
    def _calculate_severity(self) -> float:
        """Calculate the overall severity of dependency cycles.
        
        Returns:
            Severity score (0.0-1.0)
        """
        if not self.cycles:
            return 0.0
        
        # Consider number and severity of cycles
        cycle_severities = [cycle.get("severity", 0) for cycle in self.cycles]
        max_severity = max(cycle_severities) if cycle_severities else 0
        avg_severity = sum(cycle_severities) / len(cycle_severities) if cycle_severities else 0
        
        # Consider ratio of components in cycles
        cycle_ratio = len(self.components_in_cycles) / len(self.component_graph.nodes) if self.component_graph.nodes else 0
        
        # Calculate weighted severity
        severity = (0.4 * max_severity +     # Highest severity cycle
                   0.3 * avg_severity +      # Average cycle severity  
                   0.3 * min(1.0, cycle_ratio * 2))  # Extent of cycles (doubled to weight appropriately)
        
        return min(1.0, severity)
    
    def _generate_description(self, severity: float) -> str:
        """Generate a description of the dependency cycle anti-pattern.
        
        Args:
            severity: Overall severity score
            
        Returns:
            Human-readable description
        """
        if not self.cycles:
            return "No dependency cycles detected in the codebase."
        
        cycle_count = len(self.cycles)
        cycle_components_ratio = len(self.components_in_cycles) / len(self.component_graph.nodes) if self.component_graph.nodes else 0
        cycle_components_percent = int(cycle_components_ratio * 100)
        
        if severity >= 0.7:
            return (
                f"The codebase contains {cycle_count} dependency cycles affecting {cycle_components_percent}% of components. "
                f"These cyclic dependencies severely impact modularity and create tight coupling that makes "
                f"the system difficult to understand, test, and maintain."
            )
        elif severity >= 0.5:
            return (
                f"The codebase contains {cycle_count} dependency cycles affecting {cycle_components_percent}% of components. "
                f"These cycles create moderate architectural issues that should be addressed to improve "
                f"system modularity and maintainability."
            )
        else:
            return (
                f"The codebase contains {cycle_count} dependency cycles affecting {cycle_components_percent}% of components. "
                f"While limited in scope, these cycles should be addressed to prevent future architectural problems."
            )
    
    def _generate_recommendations(self, severity: float) -> List[str]:
        """Generate recommendations for addressing dependency cycles.
        
        Args:
            severity: Overall severity score
            
        Returns:
            List of recommendations
        """
        if not self.cycles:
            return ["Maintain the current acyclic dependency structure."]
        
        recommendations = []
        
        # Basic recommendations for all cycles
        recommendations.append(
            "Break dependency cycles by applying the Dependency Inversion Principle: "
            "high-level modules should not depend on low-level modules. Both should depend on abstractions."
        )
        
        # Add recommendations based on severity and metrics
        if severity >= 0.7:
            recommendations.insert(0, 
                "Consider a major refactoring to eliminate cyclic dependencies, possibly reorganizing "
                "the codebase into clear layers or modules with unidirectional dependencies."
            )
            
            recommendations.append(
                "Introduce an architectural boundary (like a facade or mediator) to mediate between "
                "components that form cycles."
            )
            
            recommendations.append(
                "Apply the Acyclic Dependencies Principle: the dependency graph of packages or components "
                "should have no cycles."
            )
        elif severity >= 0.5:
            recommendations.append(
                "Extract shared functionality into a separate component that others can depend on without "
                "creating cycles."
            )
            
            recommendations.append(
                "Use events or observer pattern to break tight coupling in cyclic dependencies."
            )
        
        # Add specific recommendations for different cycle types
        has_large_cycles = any(cycle.get("length", 0) > 3 for cycle in self.cycles)
        if has_large_cycles:
            recommendations.append(
                "For large dependency cycles (>3 components), consider breaking down components into smaller, "
                "more focused units with clearer responsibilities."
            )
        
        # Add recommendations for common architectural styles
        primary_style = self.architectural_styles.get("primary_style", "unknown")
        if primary_style == "layered_architecture":
            recommendations.append(
                "Enforce strict layering with dependencies flowing in one direction only, from higher to lower layers."
            )
        elif primary_style == "hexagonal_architecture":
            recommendations.append(
                "Strengthen port and adapter abstractions to ensure that domain components don't depend on external systems."
            )
        
        return recommendations
    
    def _generate_visualization_data(self) -> Dict:
        """Generate data for visualizing dependency cycles.
        
        Returns:
            A dictionary with visualization data
        """
        nodes = []
        edges = []
        
        # Create nodes for each component
        for component in self.component_graph.nodes:
            # Determine if component is in a cycle
            in_cycle = component in self.components_in_cycles
            
            nodes.append({
                "id": component,
                "label": os.path.basename(component),
                "in_cycle": in_cycle
            })
        
        # Create edges for dependencies
        for source, target in self.component_graph.edges:
            # Check if this edge is part of a cycle
            edge_in_cycle = False
            for cycle in self.cycles:
                components = cycle.get("components", [])
                for i in range(len(components)):
                    if components[i] == source and components[(i + 1) % len(components)] == target:
                        edge_in_cycle = True
                        break
                if edge_in_cycle:
                    break
                    
            edges.append({
                "source": source,
                "target": target,
                "in_cycle": edge_in_cycle
            })
        
        # Include cycle data for visualization
        cycles_data = []
        for cycle in self.cycles:
            cycles_data.append({
                "components": [os.path.basename(c) for c in cycle.get("components", [])],
                "severity": cycle.get("severity", 0)
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "cycles": cycles_data
        }