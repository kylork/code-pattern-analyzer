"""
God Component anti-pattern detector.

This module provides a pattern detector for identifying God Components (also known as
God Classes or Blob Classes), which violate good design principles through excessive size
and responsibility concentration.
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

class GodComponentAntiPattern(ArchitecturalAntiPattern):
    """Pattern for detecting the God Component anti-pattern.
    
    This anti-pattern occurs when a component takes on too many responsibilities,
    becoming bloated and violating the single responsibility principle, leading to:
    
    1. Excessive size and complexity 
    2. High coupling with many other components
    3. Many incoming and outgoing dependencies
    4. Difficulty understanding, testing, and modifying the component
    5. Inhibited code reuse due to heavy interdependence
    """
    
    def __init__(self):
        """Initialize the God Component anti-pattern detector."""
        super().__init__(
            name="god_component",
            description="Identifies oversized components with too many responsibilities",
            languages=["python", "javascript", "typescript", "java", "go", "c#"],
        )
        
        # Component metrics
        self.component_metrics = {}
        self.god_components = []
        
        # Thresholds for identifying god components
        self.dependency_threshold = 10  # Incoming + outgoing dependencies
        self.methods_threshold = 15     # Number of methods/functions
        self.loc_threshold = 500        # Lines of code
        self.responsibility_threshold = 5  # Estimated number of responsibilities
        
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for god components.
        
        We detect:
        1. Components with excessive dependencies
        2. Components with many methods/functions
        3. Large components (by lines of code)
        4. Components that seem to have multiple responsibilities
        
        Returns:
            A dictionary containing the god component analysis
        """
        # Skip analysis if no graph is available
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "severity": 0.0,
                "instances": [],
                "description": "No components to analyze"
            }
        
        # Reset metrics tracking
        self.component_metrics = {}
        self.god_components = []
        
        # Calculate metrics for each component
        for node_id, node_data in self.component_graph.nodes(data=True):
            # Get base metrics from graph
            incoming = self.component_graph.in_degree(node_id)
            outgoing = self.component_graph.out_degree(node_id)
            total_dependencies = incoming + outgoing
            
            # Get method count and size (if available)
            methods_count = node_data.get("methods_count", 0)
            loc = node_data.get("loc", 0)
            
            # Estimate responsibilities (very simplistic approach)
            # In a real implementation, this would be more sophisticated
            # using natural language processing, semantic analysis, etc.
            component_name = os.path.basename(node_id)
            responsibility_count = self._estimate_responsibilities(node_id, node_data, component_name)
            
            # Store metrics
            self.component_metrics[node_id] = {
                "incoming_dependencies": incoming,
                "outgoing_dependencies": outgoing,
                "total_dependencies": total_dependencies,
                "methods_count": methods_count,
                "loc": loc,
                "responsibility_count": responsibility_count,
                "name": component_name,
                "file": node_id
            }
            
            # Check if this is a god component
            god_component_score = self._calculate_god_component_score(
                total_dependencies, methods_count, loc, responsibility_count
            )
            
            if god_component_score > 0.5:  # Threshold for being considered a god component
                self.component_metrics[node_id]["god_component_score"] = god_component_score
                
                self.god_components.append({
                    "component": node_id,
                    "name": component_name,
                    "file": node_id,
                    "metrics": self.component_metrics[node_id],
                    "severity": god_component_score,
                    "type": "god_component",
                    "description": self._generate_god_component_description(
                        component_name, total_dependencies, methods_count, loc, responsibility_count
                    )
                })
        
        # Sort god components by severity
        self.god_components.sort(key=lambda x: x.get("severity", 0), reverse=True)
        
        # Calculate overall severity
        overall_severity = self._calculate_severity()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_severity)
        
        return {
            "type": self.name,
            "severity": overall_severity,
            "instances": self.god_components,
            "metrics": {
                "god_component_count": len(self.god_components),
                "total_component_count": len(self.component_graph.nodes),
                "god_component_ratio": len(self.god_components) / len(self.component_graph.nodes) if self.component_graph.nodes else 0,
                "average_dependency_count": sum(m.get("total_dependencies", 0) for m in self.component_metrics.values()) / len(self.component_metrics) if self.component_metrics else 0,
                "average_methods_count": sum(m.get("methods_count", 0) for m in self.component_metrics.values()) / len(self.component_metrics) if self.component_metrics else 0,
                "average_loc": sum(m.get("loc", 0) for m in self.component_metrics.values()) / len(self.component_metrics) if self.component_metrics else 0,
            },
            "description": self._generate_description(overall_severity),
            "recommendations": recommendations,
            "visualization_data": self._generate_visualization_data()
        }
    
    def _estimate_responsibilities(self, node_id: str, node_data: Dict, component_name: str) -> int:
        """Estimate the number of responsibilities for a component.
        
        In a real implementation, this would use semantic analysis and NLP.
        This is a simplified version that uses heuristics.
        
        Args:
            node_id: The node ID in the graph
            node_data: Node attributes
            component_name: The name of the component
            
        Returns:
            Estimated number of responsibilities
        """
        # Start with base estimate based on name
        responsibility_count = 1
        
        # Check for "and" in the name - might indicate multiple responsibilities
        if "and" in component_name.lower():
            responsibility_count += 1
        
        # Check for multiple verbs in the name like "ProcessAndValidate"
        verb_patterns = [
            "process", "validate", "handle", "manage", "control", "create", "build", 
            "generate", "transform", "calculate", "compute", "render", "display", 
            "parse", "format", "convert", "store", "load", "save", "export", "import",
            "send", "receive", "filter", "sort", "update", "delete", "authenticate",
            "authorize", "log", "cache", "sync", "coordinate"
        ]
        
        verb_count = 0
        for verb in verb_patterns:
            # Look for pattern where verb is at word boundary
            if re.search(r'\b' + verb + r'\b', component_name.lower()):
                verb_count += 1
                
        responsibility_count += min(3, verb_count)  # Cap at 3 additional from verbs
        
        # If we have dependencies data, use it
        incoming = self.component_graph.in_degree(node_id)
        outgoing = self.component_graph.out_degree(node_id)
        
        # If component has many incoming and outgoing dependencies, it might
        # have multiple responsibilities
        if incoming > 5 and outgoing > 5:
            responsibility_count += 1
            
        # If it connects very different types of components, it might
        # have multiple responsibilities
        if incoming > 3 and outgoing > 3:
            # Get all neighbors
            predecessors = list(self.component_graph.predecessors(node_id))
            successors = list(self.component_graph.successors(node_id))
            
            # Get types of neighbors if available
            pred_types = set()
            succ_types = set()
            
            for p in predecessors:
                p_type = self.component_graph.nodes[p].get('component_type', 
                                                         self.component_graph.nodes[p].get('layer', None))
                if p_type:
                    pred_types.add(p_type)
                    
            for s in successors:
                s_type = self.component_graph.nodes[s].get('component_type', 
                                                         self.component_graph.nodes[s].get('layer', None))
                if s_type:
                    succ_types.add(s_type)
            
            # If connecting many different types, add to responsibility count
            responsibility_count += min(2, len(pred_types), len(succ_types))
        
        return responsibility_count
    
    def _calculate_god_component_score(self, 
                                     total_dependencies: int, 
                                     methods_count: int, 
                                     loc: int, 
                                     responsibility_count: int) -> float:
        """Calculate a score indicating how much this component exhibits god component traits.
        
        Args:
            total_dependencies: Number of incoming and outgoing dependencies
            methods_count: Number of methods/functions in the component
            loc: Lines of code
            responsibility_count: Estimated number of responsibilities
            
        Returns:
            God component score (0.0-1.0)
        """
        # Calculate normalized scores for each metric
        dependency_score = min(1.0, total_dependencies / self.dependency_threshold)
        methods_score = min(1.0, methods_count / self.methods_threshold)
        loc_score = min(1.0, loc / self.loc_threshold)
        responsibility_score = min(1.0, responsibility_count / self.responsibility_threshold)
        
        # Weighted average of scores
        weights = [0.3, 0.2, 0.2, 0.3]  # Dependencies, methods, LOC, responsibilities
        total_score = (
            weights[0] * dependency_score +
            weights[1] * methods_score +
            weights[2] * loc_score +
            weights[3] * responsibility_score
        )
        
        return total_score
    
    def _generate_god_component_description(self, 
                                          component_name: str, 
                                          total_dependencies: int, 
                                          methods_count: int, 
                                          loc: int, 
                                          responsibility_count: int) -> str:
        """Generate a description of why this component is considered a god component.
        
        Args:
            component_name: Name of the component
            total_dependencies: Number of incoming and outgoing dependencies
            methods_count: Number of methods/functions
            loc: Lines of code
            responsibility_count: Estimated number of responsibilities
            
        Returns:
            Human-readable description
        """
        reasons = []
        
        if total_dependencies >= self.dependency_threshold:
            reasons.append(f"has {total_dependencies} dependencies")
            
        if methods_count >= self.methods_threshold:
            reasons.append(f"contains {methods_count} methods")
            
        if loc >= self.loc_threshold:
            reasons.append(f"contains {loc} lines of code")
            
        if responsibility_count >= self.responsibility_threshold:
            reasons.append(f"appears to have {responsibility_count} different responsibilities")
        
        # If we have reasons, generate description
        if reasons:
            return f"Component {component_name} is a god component that {', '.join(reasons)}"
        else:
            return f"Component {component_name} exhibits god component characteristics"
    
    def _calculate_severity(self) -> float:
        """Calculate the overall severity of god components in the codebase.
        
        Returns:
            Severity score (0.0-1.0)
        """
        if not self.god_components:
            return 0.0
        
        # Consider the number and severity of god components
        god_component_severities = [comp.get("severity", 0.0) for comp in self.god_components]
        max_severity = max(god_component_severities) if god_component_severities else 0.0
        avg_severity = sum(god_component_severities) / len(god_component_severities) if god_component_severities else 0.0
        
        # Consider ratio of god components to total components
        god_ratio = len(self.god_components) / len(self.component_graph.nodes) if self.component_graph.nodes else 0.0
        
        # Calculate weighted severity
        severity = (0.4 * max_severity +  # Worst god component
                   0.4 * avg_severity +   # Average god component severity
                   0.2 * min(1.0, god_ratio * 5))  # Ratio of god components (scaled)
        
        return min(1.0, severity)
    
    def _generate_description(self, severity: float) -> str:
        """Generate a description of the god component anti-pattern.
        
        Args:
            severity: Overall severity score
            
        Returns:
            Human-readable description
        """
        if severity < 0.3:
            return "The codebase shows minimal evidence of god components. Most components follow good design principles."
        
        num_god_components = len(self.god_components)
        component_ratio = len(self.god_components) / len(self.component_graph.nodes) if self.component_graph.nodes else 0
        component_ratio_pct = int(component_ratio * 100)
        
        if severity >= 0.7:
            return (
                f"The codebase has {num_god_components} god components ({component_ratio_pct}% of all components). "
                f"These components have excessive responsibilities, size, and dependencies, making the "
                f"system harder to understand, test, and maintain. This indicates a significant violation "
                f"of the Single Responsibility Principle."
            )
        elif severity >= 0.5:
            return (
                f"The codebase has {num_god_components} god components ({component_ratio_pct}% of all components). "
                f"These components have more responsibilities and dependencies than ideal, which may "
                f"lead to maintainability issues and hinder code reuse."
            )
        else:
            return (
                f"The codebase has {num_god_components} god components ({component_ratio_pct}% of all components). "
                f"While limited in scope, these components have more responsibilities than recommended "
                f"and would benefit from refactoring to improve maintainability."
            )
    
    def _generate_recommendations(self, severity: float) -> List[str]:
        """Generate recommendations for addressing god components.
        
        Args:
            severity: Overall severity score
            
        Returns:
            List of recommendations
        """
        if not self.god_components:
            return ["Continue following the Single Responsibility Principle in your design."]
        
        recommendations = []
        
        # Basic recommendation for all god components
        recommendations.append(
            "Apply the Single Responsibility Principle to break down god components into smaller, more focused components"
        )
        
        # Add recommendations based on severity
        if severity >= 0.7:
            recommendations.insert(0, 
                "Prioritize refactoring the god components as a major architectural improvement"
            )
            
            recommendations.append(
                "Consider a complete redesign of the most severe god components, splitting them into multiple smaller components"
            )
            
            recommendations.append(
                "Implement regular code reviews and static analysis to prevent new god components from forming"
            )
        elif severity >= 0.5:
            recommendations.append(
                "Apply the Extract Class refactoring pattern to split responsibilities into separate components"
            )
            
            recommendations.append(
                "Review component dependencies to identify opportunities to reduce coupling"
            )
            
        # Add specific recommendations based on the god components
        high_dependency_components = [c for c in self.god_components if c["metrics"].get("total_dependencies", 0) >= self.dependency_threshold]
        if high_dependency_components:
            recommendations.append(
                "Reduce coupling by introducing interfaces or applying the Dependency Inversion Principle"
            )
            
        high_method_components = [c for c in self.god_components if c["metrics"].get("methods_count", 0) >= self.methods_threshold]
        if high_method_components:
            recommendations.append(
                "Apply the Extract Method and Extract Class refactoring patterns to break down large components"
            )
            
        high_responsibility_components = [c for c in self.god_components if c["metrics"].get("responsibility_count", 0) >= self.responsibility_threshold]
        if high_responsibility_components:
            recommendations.append(
                "Identify distinct responsibilities within god components and separate them into focused components"
            )
            
        # Add general design principles
        recommendations.append(
            "Apply design patterns like Strategy, Observer, or Decorator to distribute responsibilities appropriately"
        )
        
        return recommendations
    
    def _generate_visualization_data(self) -> Dict:
        """Generate data for visualizing god components.
        
        Returns:
            A dictionary with visualization data
        """
        nodes = []
        edges = []
        
        # Set of god component IDs for quick lookup
        god_component_ids = {c["component"] for c in self.god_components}
        
        # Create nodes for each component
        for node_id, node_data in self.component_graph.nodes(data=True):
            # Determine if this is a god component
            is_god = node_id in god_component_ids
            
            # Get metrics if available
            metrics = self.component_metrics.get(node_id, {})
            
            nodes.append({
                "id": node_id,
                "label": os.path.basename(node_id),
                "is_god_component": is_god,
                "metrics": metrics,
                "severity": next((c["severity"] for c in self.god_components if c["component"] == node_id), 0.0)
            })
        
        # Create edges for dependencies
        for source, target in self.component_graph.edges:
            # Check if either end is a god component
            involves_god = source in god_component_ids or target in god_component_ids
            
            edges.append({
                "source": source,
                "target": target,
                "involves_god_component": involves_god
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "god_components": self.god_components
        }