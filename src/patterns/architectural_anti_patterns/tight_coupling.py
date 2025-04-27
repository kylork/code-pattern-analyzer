"""
Tight Coupling anti-pattern detector.

This module provides a pattern detector for identifying tight coupling between components,
which violates good design principles and leads to maintenance issues.
"""

from typing import Dict, List, Optional, Set, Counter
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from ...pattern_base import Pattern
from .architectural_anti_pattern_base import ArchitecturalAntiPattern

logger = logging.getLogger(__name__)

class TightCouplingAntiPattern(ArchitecturalAntiPattern):
    """Pattern for detecting the Tight Coupling anti-pattern.
    
    This anti-pattern occurs when components are excessively dependent on each other,
    leading to:
    
    1. High change impact (changes in one component affect many others)
    2. Difficulty in testing components in isolation
    3. Reduced reusability of components
    4. Challenges in understanding the system due to complex interactions
    """
    
    def __init__(self):
        """Initialize the Tight Coupling anti-pattern detector."""
        super().__init__(
            name="tight_coupling",
            description="Identifies excessive dependencies between components",
            languages=["python", "javascript", "typescript", "java", "go", "c#"],
        )
        
        # Coupling metrics
        self.coupling_instances = []
        self.afferent_coupling = defaultdict(int)  # Fan-in
        self.efferent_coupling = defaultdict(int)  # Fan-out
        self.coupled_components = set()
        
        # Threshold values
        self.high_coupling_threshold = 5  # More than this number of dependencies indicates tight coupling
        self.excessive_coupling_threshold = 10  # More than this is considered excessive
        
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for tight coupling.
        
        We detect:
        1. Components with high afferent coupling (many incoming dependencies)
        2. Components with high efferent coupling (many outgoing dependencies)
        3. Tightly coupled component pairs or clusters
        
        Returns:
            A dictionary containing the tight coupling analysis
        """
        # Skip analysis if no graph is available
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "severity": 0.0,
                "instances": [],
                "description": "No components to analyze"
            }
        
        # Reset metrics
        self.coupling_instances = []
        self.afferent_coupling = defaultdict(int)
        self.efferent_coupling = defaultdict(int)
        self.coupled_components = set()
        
        # Calculate afferent and efferent coupling for each component
        for component in self.component_graph.nodes:
            # Count incoming edges (afferent coupling)
            self.afferent_coupling[component] = self.component_graph.in_degree(component)
            
            # Count outgoing edges (efferent coupling)
            self.efferent_coupling[component] = self.component_graph.out_degree(component)
            
            # Mark components with high coupling
            if (self.afferent_coupling[component] > self.high_coupling_threshold or
                self.efferent_coupling[component] > self.high_coupling_threshold):
                self.coupled_components.add(component)
        
        # Find tightly coupled component pairs (bidirectional dependencies)
        for source, target in self.component_graph.edges:
            # Check if there's a reciprocal dependency
            if self.component_graph.has_edge(target, source):
                # Both components depend on each other
                coupling_instance = {
                    "type": "bidirectional_dependency",
                    "components": [source, target],
                    "severity": 0.7,  # Bidirectional dependencies are quite severe
                    "description": f"Bidirectional dependency between {os.path.basename(source)} and {os.path.basename(target)}"
                }
                self.coupling_instances.append(coupling_instance)
                self.coupled_components.add(source)
                self.coupled_components.add(target)
        
        # Find components with excessive coupling
        for component in self.component_graph.nodes:
            afferent = self.afferent_coupling[component]
            efferent = self.efferent_coupling[component]
            
            # High afferent coupling (too many incoming dependencies)
            if afferent > self.excessive_coupling_threshold:
                coupling_instance = {
                    "type": "high_afferent_coupling",
                    "component": component,
                    "value": afferent,
                    "severity": min(1.0, (afferent - self.high_coupling_threshold) / 
                                   (self.excessive_coupling_threshold - self.high_coupling_threshold)),
                    "description": f"{os.path.basename(component)} has {afferent} incoming dependencies (excessive fan-in)"
                }
                self.coupling_instances.append(coupling_instance)
                self.coupled_components.add(component)
            
            # High efferent coupling (too many outgoing dependencies)
            if efferent > self.excessive_coupling_threshold:
                coupling_instance = {
                    "type": "high_efferent_coupling",
                    "component": component,
                    "value": efferent,
                    "severity": min(1.0, (efferent - self.high_coupling_threshold) / 
                                   (self.excessive_coupling_threshold - self.high_coupling_threshold)),
                    "description": f"{os.path.basename(component)} depends on {efferent} other components (excessive fan-out)"
                }
                self.coupling_instances.append(coupling_instance)
                self.coupled_components.add(component)
        
        # Calculate instability for each component
        instability_metrics = {}
        for component in self.component_graph.nodes:
            ce = self.efferent_coupling[component]  # Efferent coupling
            ca = self.afferent_coupling[component]  # Afferent coupling
            
            if ce + ca > 0:
                instability = ce / (ce + ca)  # Ranges from 0 to 1
                instability_metrics[component] = instability
                
                # Highly unstable and highly coupled components are problematic
                if instability > 0.7 and ce > self.high_coupling_threshold:
                    coupling_instance = {
                        "type": "high_instability",
                        "component": component,
                        "instability": instability,
                        "efferent": ce,
                        "severity": min(1.0, 0.5 + (ce - self.high_coupling_threshold) / 
                                      (self.excessive_coupling_threshold - self.high_coupling_threshold) * 0.5),
                        "description": f"{os.path.basename(component)} is highly unstable (instability: {instability:.2f}) with {ce} outgoing dependencies"
                    }
                    self.coupling_instances.append(coupling_instance)
        
        # Find highly connected clusters (potential architectural tangles)
        # This is a simplified implementation - a more sophisticated approach would use
        # algorithms like strongly connected components or community detection
        connected_sets = list(nx.connected_components(self.component_graph.to_undirected()))
        for component_set in connected_sets:
            if len(component_set) >= 4:  # Only consider sufficiently large clusters
                # Check the density of connections within the cluster
                subgraph = self.component_graph.subgraph(component_set)
                edge_count = subgraph.number_of_edges()
                node_count = len(component_set)
                max_edges = node_count * (node_count - 1)  # Maximum possible directed edges
                
                if max_edges > 0:
                    density = edge_count / max_edges
                    
                    # High density clusters are problematic
                    if density > 0.3 and node_count >= 5:  # 30% of possible connections in a cluster of 5+ components
                        component_names = [os.path.basename(c) for c in component_set]
                        coupling_instance = {
                            "type": "coupled_cluster",
                            "components": list(component_set),
                            "size": len(component_set),
                            "density": density,
                            "severity": min(1.0, 0.5 + density * 0.5),  # Scale based on density
                            "description": f"Tightly coupled cluster of {len(component_set)} components with connection density of {density:.2f}"
                        }
                        self.coupling_instances.append(coupling_instance)
        
        # Sort instances by severity
        self.coupling_instances.sort(key=lambda x: x.get("severity", 0), reverse=True)
        
        # Calculate overall severity
        overall_severity = self._calculate_severity()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_severity)
        
        return {
            "type": self.name,
            "severity": overall_severity,
            "instances": self.coupling_instances,
            "metrics": {
                "coupled_component_count": len(self.coupled_components),
                "total_component_count": len(self.component_graph.nodes),
                "coupled_component_ratio": len(self.coupled_components) / len(self.component_graph.nodes) if self.component_graph.nodes else 0,
                "average_afferent_coupling": sum(self.afferent_coupling.values()) / len(self.component_graph.nodes) if self.component_graph.nodes else 0,
                "average_efferent_coupling": sum(self.efferent_coupling.values()) / len(self.component_graph.nodes) if self.component_graph.nodes else 0,
                "max_afferent_coupling": max(self.afferent_coupling.values()) if self.afferent_coupling else 0,
                "max_efferent_coupling": max(self.efferent_coupling.values()) if self.efferent_coupling else 0,
            },
            "description": self._generate_description(overall_severity),
            "recommendations": recommendations,
            "visualization_data": self._generate_visualization_data()
        }
    
    def _calculate_severity(self) -> float:
        """Calculate the overall severity of tight coupling.
        
        Returns:
            Severity score (0.0-1.0)
        """
        if not self.coupling_instances:
            return 0.0
        
        # Consider number and severity of instances
        instance_severities = [inst.get("severity", 0) for inst in self.coupling_instances]
        max_severity = max(instance_severities) if instance_severities else 0
        avg_severity = sum(instance_severities) / len(instance_severities) if instance_severities else 0
        
        # Consider ratio of coupled components
        coupled_ratio = len(self.coupled_components) / len(self.component_graph.nodes) if self.component_graph.nodes else 0
        
        # Calculate weighted severity
        severity = (0.4 * max_severity +  # Highest severity issues
                   0.3 * avg_severity +   # Average severity
                   0.3 * coupled_ratio)   # Extent of coupling across codebase
        
        return min(1.0, severity)
    
    def _generate_description(self, severity: float) -> str:
        """Generate a description of the tight coupling anti-pattern.
        
        Args:
            severity: Overall severity score
            
        Returns:
            Human-readable description
        """
        if severity < 0.3:
            return "The codebase shows minimal signs of tight coupling between components."
        
        coupled_ratio = len(self.coupled_components) / len(self.component_graph.nodes) if self.component_graph.nodes else 0
        coupled_percent = int(coupled_ratio * 100)
        
        if severity >= 0.7:
            return (
                f"The codebase exhibits severe tight coupling issues, with {coupled_percent}% of components "
                f"involved in problematic coupling relationships. This significantly impacts maintainability, "
                f"testability, and the ability to evolve the system."
            )
        elif severity >= 0.5:
            return (
                f"The codebase shows moderate tight coupling, with {coupled_percent}% of components "
                f"having excessive dependencies. This coupling reduces the modularity of the system "
                f"and makes it harder to change components independently."
            )
        else:
            return (
                f"The codebase has some instances of tight coupling, affecting {coupled_percent}% of components. "
                f"While not severe, these issues could impact future maintenance and extensibility."
            )
    
    def _generate_recommendations(self, severity: float) -> List[str]:
        """Generate recommendations for addressing tight coupling.
        
        Args:
            severity: Overall severity score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Generate recommendations based on the types of coupling found
        bidirectional_count = sum(1 for inst in self.coupling_instances if inst.get("type") == "bidirectional_dependency")
        high_afferent_count = sum(1 for inst in self.coupling_instances if inst.get("type") == "high_afferent_coupling")
        high_efferent_count = sum(1 for inst in self.coupling_instances if inst.get("type") == "high_efferent_coupling")
        cluster_count = sum(1 for inst in self.coupling_instances if inst.get("type") == "coupled_cluster")
        
        # Recommend based on bidirectional dependencies
        if bidirectional_count > 0:
            recommendations.append(
                f"Eliminate bidirectional dependencies between components by introducing abstractions "
                f"or intermediary components"
            )
        
        # Recommend based on high afferent coupling
        if high_afferent_count > 0:
            recommendations.append(
                f"Reduce high afferent coupling (fan-in) by breaking up highly used components into "
                f"smaller, more focused services or interfaces"
            )
        
        # Recommend based on high efferent coupling
        if high_efferent_count > 0:
            recommendations.append(
                f"Reduce high efferent coupling (fan-out) by applying the Dependency Inversion Principle "
                f"and introducing abstractions that components can depend on"
            )
        
        # Recommend based on coupled clusters
        if cluster_count > 0:
            recommendations.append(
                f"Refactor tightly coupled component clusters by clearly defining boundaries "
                f"and introducing facades or gateway interfaces"
            )
        
        # General recommendations based on severity
        if severity >= 0.7:
            recommendations.insert(0, 
                "Consider a significant architectural refactoring to reduce tight coupling across the codebase"
            )
        elif severity >= 0.5:
            recommendations.insert(0,
                "Apply the Interface Segregation Principle to create smaller, more focused interfaces"
            )
        
        # Add design pattern recommendations
        if severity >= 0.4:
            recommendations.append(
                "Apply the Mediator pattern to centralize and control component interactions"
            )
            
            recommendations.append(
                "Use the Facade pattern to provide simplified interfaces to complex subsystems"
            )
        
        return recommendations
    
    def _generate_visualization_data(self) -> Dict:
        """Generate data for visualizing tight coupling anti-patterns.
        
        Returns:
            A dictionary with visualization data
        """
        nodes = []
        edges = []
        
        # Create nodes for each component
        for component in self.component_graph.nodes:
            afferent = self.afferent_coupling[component]
            efferent = self.efferent_coupling[component]
            
            # Determine coupling level
            if component in self.coupled_components:
                coupling_level = "high"
            elif afferent > self.high_coupling_threshold / 2 or efferent > self.high_coupling_threshold / 2:
                coupling_level = "medium"
            else:
                coupling_level = "low"
                
            nodes.append({
                "id": component,
                "label": os.path.basename(component),
                "afferent": afferent,
                "efferent": efferent,
                "coupling_level": coupling_level
            })
        
        # Create edges for dependencies
        for source, target in self.component_graph.edges:
            # Check if this is a bidirectional dependency
            is_bidirectional = self.component_graph.has_edge(target, source)
            
            edges.append({
                "source": source,
                "target": target,
                "bidirectional": is_bidirectional
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }