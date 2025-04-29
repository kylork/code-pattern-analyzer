"""
Layered Architecture pattern detector.

This module provides a pattern detector for identifying the Layered
architectural style in codebases.
"""

from typing import Dict, List, Optional, Set, Counter, Tuple
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from ...pattern_base import Pattern, CompositePattern
from .architectural_style_base import ArchitecturalStylePattern

logger = logging.getLogger(__name__)

class LayeredArchitecturePattern(ArchitecturalStylePattern):
    """Pattern for detecting Layered Architecture.
    
    This pattern identifies codebases that follow the Layered architectural style,
    which emphasizes:
    
    1. Clear separation of components into horizontal layers
    2. Strict dependencies between layers (typically top-down)
    3. Well-defined responsibilities for each layer
    4. Isolation of concerns at each layer level
    5. Standard layers such as presentation, business logic, data access
    """
    
    def __init__(self):
        """Initialize the Layered Architecture detector."""
        super().__init__(
            name="layered_architecture",
            description="Identifies Layered Architecture patterns",
            languages=["python", "javascript", "typescript", "java", "go", "c#"],
        )
        
        # Component tracking
        self.presentation_layer = set()  # UI, controllers, views
        self.business_layer = set()      # Services, business logic
        self.data_access_layer = set()   # Repositories, DAOs
        self.domain_layer = set()        # Domain models, entities
        
        # Layer organization
        self.layers = {}
        self.layer_dependencies = defaultdict(set)
        
        # Track dependency violations for detailed reporting
        self.dependency_violations = []
        
        # Standard layering order (top to bottom)
        self.standard_layer_order = ['presentation', 'business', 'data_access', 'domain']
        
        # Layer indicators - common naming conventions
        self.presentation_indicators = [
            r'controller', r'view', r'ui', r'page', r'screen', r'component',
            r'dialog', r'form', r'template', r'presenter', r'api', r'endpoint',
            r'rest', r'graphql', r'handler', r'servlet', r'action'
        ]
        
        self.business_indicators = [
            r'service', r'manager', r'coordinator', r'workflow', r'usecase',
            r'interactor', r'application', r'orchestrator', r'facade',
            r'processor', r'command', r'handler', r'business'
        ]
        
        self.data_access_indicators = [
            r'repository', r'dao', r'store', r'persistence', r'mapper',
            r'adapter', r'client', r'gateway', r'provider', r'datasource'
        ]
        
        self.domain_indicators = [
            r'model', r'entity', r'domain', r'dto', r'bean', r'pojo',
            r'record', r'struct', r'type', r'vo', r'value'
        ]
        
        # Layer directory names
        self.layer_directories = {
            'presentation': [
                'controllers', 'views', 'ui', 'pages', 'screens', 'components',
                'presenters', 'api', 'rest', 'graphql', 'web'
            ],
            'business': [
                'services', 'managers', 'usecases', 'interactors', 'application',
                'business', 'workflows', 'orchestrators', 'facades'
            ],
            'data_access': [
                'repositories', 'daos', 'persistence', 'data', 'mappers',
                'adapters', 'clients', 'gateways', 'providers'
            ],
            'domain': [
                'models', 'entities', 'domain', 'dtos', 'beans', 'pojos',
                'records', 'types', 'vo', 'valueobjects'
            ]
        }
    
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Layered Architecture, we're looking for:
        1. Components that fit into one of the standard layers
        2. Dependencies between components in different layers
        3. Directory structure that reflects layer organization
        
        Args:
            pattern_name: The name of the pattern
            matches: List of pattern matches
            file_path: Path to the file
        """
        # Skip non-relevant patterns
        if not matches:
            return
            
        # Process based on pattern type
        if pattern_name in ['class_definition', 'function_definition']:
            for match in matches:
                component_name = match.get('name', '')
                
                # Skip generic/common names
                if not component_name or component_name.lower() in ['main', 'test', 'utils', 'helper']:
                    continue
                
                # Categorize the component by name indicators
                layer = self._categorize_component_by_name(component_name)
                
                # If we couldn't categorize by name, try by file path
                if not layer:
                    layer = self._categorize_component_by_path(file_path)
                
                # If we have a layer, add to the graph
                if layer:
                    node_id = f"{file_path}::{component_name}"
                    node_attrs = {
                        'file': file_path,
                        'name': component_name,
                        'layer': layer,
                        'type': pattern_name
                    }
                    
                    # Add to component graph
                    if not self.component_graph.has_node(node_id):
                        self.component_graph.add_node(node_id, **node_attrs)
                    
                    # Add to appropriate layer set
                    if layer == 'presentation':
                        self.presentation_layer.add(node_id)
                    elif layer == 'business':
                        self.business_layer.add(node_id)
                    elif layer == 'data_access':
                        self.data_access_layer.add(node_id)
                    elif layer == 'domain':
                        self.domain_layer.add(node_id)
        
        # Process import/dependency patterns
        elif pattern_name in ['import', 'import_from', 'require']:
            for match in matches:
                source_file = file_path
                target = match.get('module', match.get('name', ''))
                
                # Try to resolve the target to a file path (simplified approach)
                target_file = self._resolve_import_target(source_file, target)
                
                if target_file and os.path.exists(target_file):
                    # Get the layers
                    source_layer = self._categorize_component_by_path(source_file)
                    target_layer = self._categorize_component_by_path(target_file)
                    
                    if source_layer and target_layer:
                        # Add to layer dependencies
                        self.layer_dependencies[source_layer].add(target_layer)
                        
                        # Check for layer dependency violations
                        violation = self._check_layer_dependency_violation(
                            source_layer, target_layer, source_file, target_file,
                            match.get('line', 0)
                        )
                        
                        if violation:
                            self.dependency_violations.append(violation)
                        
                        # Add edge to component graph
                        source_id = f"{source_file}::module"
                        target_id = f"{target_file}::module"
                        
                        if not self.component_graph.has_node(source_id):
                            self.component_graph.add_node(source_id, 
                                                          file=source_file, 
                                                          layer=source_layer,
                                                          type='module')
                        
                        if not self.component_graph.has_node(target_id):
                            self.component_graph.add_node(target_id, 
                                                          file=target_file, 
                                                          layer=target_layer,
                                                          type='module')
                        
                        # Add edge with violation flag
                        is_violation = True if violation else False
                        self.component_graph.add_edge(
                            source_id, target_id, 
                            type='import', 
                            violation=is_violation
                        )
    
    def _check_layer_dependency_violation(self, 
                                         source_layer: str, 
                                         target_layer: str,
                                         source_file: str,
                                         target_file: str,
                                         line_number: int = 0) -> Optional[Dict]:
        """Check if this dependency violates layered architecture principles.
        
        In a strict layered architecture, dependencies should only flow downward:
        presentation → business → data_access → domain
        
        Args:
            source_layer: The layer of the source component
            target_layer: The layer of the target component
            source_file: Path to the source file
            target_file: Path to the target file
            line_number: Line number of the import statement
            
        Returns:
            A dictionary describing the violation, or None if no violation
        """
        # Get indices in the standard layer order
        try:
            source_idx = self.standard_layer_order.index(source_layer)
            target_idx = self.standard_layer_order.index(target_layer)
        except ValueError:
            # If we can't find the layer in our standard order, skip this check
            return None
        
        # Check if dependency flows upward (violation)
        if target_idx <= source_idx and source_layer != target_layer:
            # This is a violation - dependency flows upward
            return {
                'source_layer': source_layer,
                'target_layer': target_layer,
                'source_file': source_file,
                'target_file': target_file,
                'line': line_number,
                'message': f"Upward dependency from {source_layer} to {target_layer}"
            }
            
        return None
    
    def _categorize_component_by_name(self, component_name: str) -> Optional[str]:
        """Categorize a component into a layer based on its name.
        
        Args:
            component_name: The name of the component
            
        Returns:
            The layer name, or None if not categorized
        """
        normalized_name = component_name.lower()
        
        # Check for presentation layer indicators
        for indicator in self.presentation_indicators:
            if re.search(indicator, normalized_name, re.IGNORECASE):
                return 'presentation'
        
        # Check for business layer indicators
        for indicator in self.business_indicators:
            if re.search(indicator, normalized_name, re.IGNORECASE):
                return 'business'
        
        # Check for data access layer indicators
        for indicator in self.data_access_indicators:
            if re.search(indicator, normalized_name, re.IGNORECASE):
                return 'data_access'
        
        # Check for domain layer indicators
        for indicator in self.domain_indicators:
            if re.search(indicator, normalized_name, re.IGNORECASE):
                return 'domain'
        
        return None
    
    def _categorize_component_by_path(self, file_path: str) -> Optional[str]:
        """Categorize a component into a layer based on its file path.
        
        Args:
            file_path: The path to the component file
            
        Returns:
            The layer name, or None if not categorized
        """
        path_parts = Path(file_path).parts
        
        # Check each directory name against layer directory patterns
        for part in path_parts:
            part_lower = part.lower()
            
            # Check each layer
            for layer, directories in self.layer_directories.items():
                if part_lower in directories:
                    return layer
                
                # Also check for singular forms
                if part_lower.rstrip('s') in [d.rstrip('s') for d in directories]:
                    return layer
        
        return None
    
    def _resolve_import_target(self, source_file: str, target: str) -> Optional[str]:
        """Resolve an import target to a file path.
        
        This is a simplified approach that works for relative imports.
        For a production system, you'd need a more sophisticated resolver
        that understands the language's import resolution rules.
        
        Args:
            source_file: The source file containing the import
            target: The import target
            
        Returns:
            The resolved file path, or None if not resolved
        """
        source_dir = os.path.dirname(source_file)
        
        # Handle relative imports like 'from ..models import User'
        if target.startswith('.'):
            # Count the number of dots to determine how many directories to go up
            up_levels = target.count('.') - (1 if target.startswith('..') else 0)
            
            # Go up that many directories
            current_dir = source_dir
            for _ in range(up_levels):
                current_dir = os.path.dirname(current_dir)
            
            # Remove the dots and convert to path
            clean_target = target.lstrip('.')
            if clean_target:
                target_path = os.path.join(current_dir, *clean_target.split('.'))
                
                # Try with common extensions
                for ext in ['.py', '.js', '.ts', '.java', '.go', '.cs']:
                    if os.path.exists(target_path + ext):
                        return target_path + ext
                
                # Try as a directory with __init__.py
                init_path = os.path.join(target_path, '__init__.py')
                if os.path.exists(init_path):
                    return init_path
        
        return None
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Layered Architecture style.
        
        Returns:
            A dictionary containing the detected architectural style
        """
        # Count components in each layer
        layer_counts = {
            'presentation': len(self.presentation_layer),
            'business': len(self.business_layer),
            'data_access': len(self.data_access_layer),
            'domain': len(self.domain_layer)
        }
        
        total_components = sum(layer_counts.values())
        if total_components == 0:
            logger.info("No components found for layered architecture analysis")
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No evidence of Layered Architecture detected",
                "layer_counts": layer_counts,
                "layer_dependencies": dict(self.layer_dependencies),
                "recommendations": []
            }
        
        # Calculate layer distribution score - ideally balanced or following common patterns
        layer_scores = []
        if total_components >= 4:  # Need a minimum number of components
            # Check if we have at least some components in each layer
            layers_with_components = sum(1 for count in layer_counts.values() if count > 0)
            layer_distribution_score = min(1.0, layers_with_components / 4.0)
            layer_scores.append(layer_distribution_score)
            
            # Bonus for having a typical layer ratio (more UI, fewer data access)
            if (layer_counts['presentation'] >= layer_counts['business'] >= 
                layer_counts['data_access']):
                layer_scores.append(0.1)
        
        # Analyze dependencies between layers
        dependency_scores = []
        
        # Check top-down dependencies
        correct_dependencies = {
            'presentation': {'business', 'domain'},
            'business': {'data_access', 'domain'},
            'data_access': {'domain'},
            'domain': set()  # Domain layer should not depend on other layers
        }
        
        total_dependencies = 0
        correct_dependency_count = 0
        
        for source_layer, target_layers in self.layer_dependencies.items():
            valid_targets = correct_dependencies.get(source_layer, set())
            for target_layer in target_layers:
                total_dependencies += 1
                if target_layer in valid_targets:
                    correct_dependency_count += 1
        
        # Calculate dependency score
        if total_dependencies > 0:
            dependency_score = correct_dependency_count / total_dependencies
            dependency_scores.append(dependency_score)
            
            # Apply a penalty for violations
            violation_count = len(self.dependency_violations)
            if violation_count > 0:
                violation_ratio = min(1.0, violation_count / total_dependencies)
                # Higher penalty for more violations
                dependency_scores.append(-0.5 * violation_ratio)
        
        # Check directory structure
        directory_scores = []
        node_layers = [data.get('layer') for _, data in self.component_graph.nodes(data=True) 
                      if 'layer' in data]
        
        if node_layers:
            # Count how many components are in a directory matching their layer
            layer_counter = Counter(node_layers)
            directory_score = min(1.0, len(layer_counter) / 4.0)
            directory_scores.append(directory_score)
        
        # Calculate overall confidence
        confidence_scores = layer_scores + dependency_scores + directory_scores
        confidence = sum(confidence_scores) / max(1, len(confidence_scores))
        confidence = max(0.0, min(1.0, confidence))  # Ensure confidence is between 0 and 1
        
        # Calculate statistics for violations
        violation_stats = self._calculate_violation_statistics()
        
        # Get top components for each layer
        top_components = {
            'presentation': self._get_top_components(self.presentation_layer, 3),
            'business': self._get_top_components(self.business_layer, 3),
            'data_access': self._get_top_components(self.data_access_layer, 3),
            'domain': self._get_top_components(self.domain_layer, 3)
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            layer_counts, 
            self.layer_dependencies, 
            violation_stats
        )
        
        # Convert sets to lists for JSON serialization
        layer_deps = {}
        for source, targets in self.layer_dependencies.items():
            layer_deps[source] = list(targets)
        
        # Create the result dictionary
        return {
            "type": self.name,
            "confidence": confidence,
            "layer_counts": layer_counts,
            "components": top_components,
            "layer_dependencies": layer_deps,
            "violation_statistics": violation_stats,
            "dependency_violations": self.dependency_violations[:10],  # Limit to top 10
            "description": self._generate_description(confidence, layer_counts, violation_stats),
            "recommendations": recommendations,
            "layered_architecture_graph": self._generate_layer_graph_data()
        }
    
    def _calculate_violation_statistics(self) -> Dict:
        """Calculate statistics about layer dependency violations.
        
        Returns:
            Dictionary of violation statistics
        """
        if not self.dependency_violations:
            return {
                'count': 0,
                'by_source_layer': {},
                'by_target_layer': {},
                'most_common_violation': None
            }
        
        # Count violations by source and target layer
        violations_by_source = defaultdict(int)
        violations_by_target = defaultdict(int)
        violation_pairs = defaultdict(int)
        
        for violation in self.dependency_violations:
            source = violation['source_layer']
            target = violation['target_layer']
            violations_by_source[source] += 1
            violations_by_target[target] += 1
            violation_pairs[(source, target)] += 1
        
        # Find most common violation pair
        most_common = max(violation_pairs.items(), key=lambda x: x[1])
        source, target = most_common[0]
        
        return {
            'count': len(self.dependency_violations),
            'by_source_layer': dict(violations_by_source),
            'by_target_layer': dict(violations_by_target),
            'most_common_violation': {
                'source': source,
                'target': target,
                'count': most_common[1]
            }
        }
    
    def _generate_layer_graph_data(self) -> Dict:
        """Generate data for visualizing the layered architecture.
        
        Returns:
            A dictionary with layer graph data
        """
        # Create nodes for each layer
        nodes = []
        for layer in self.standard_layer_order:
            count = 0
            if layer == 'presentation':
                count = len(self.presentation_layer)
            elif layer == 'business':
                count = len(self.business_layer)
            elif layer == 'data_access':
                count = len(self.data_access_layer)
            elif layer == 'domain':
                count = len(self.domain_layer)
                
            nodes.append({
                'id': layer,
                'label': layer.replace('_', ' ').title(),
                'count': count
            })
        
        # Create edges for dependencies between layers
        edges = []
        for source_layer, target_layers in self.layer_dependencies.items():
            for target_layer in target_layers:
                # Skip self-dependencies
                if source_layer == target_layer:
                    continue
                    
                # Check if this is a violation
                is_violation = False
                try:
                    source_idx = self.standard_layer_order.index(source_layer)
                    target_idx = self.standard_layer_order.index(target_layer)
                    is_violation = target_idx <= source_idx
                except ValueError:
                    pass
                
                edges.append({
                    'source': source_layer,
                    'target': target_layer,
                    'violation': is_violation
                })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _get_top_components(self, component_set: Set[str], limit: int = 3) -> List[Dict]:
        """Get the top components from a layer.
        
        Args:
            component_set: Set of component IDs
            limit: Maximum number of components to return
            
        Returns:
            List of component dictionaries
        """
        result = []
        for node_id in list(component_set)[:limit]:
            if self.component_graph.has_node(node_id):
                node_data = self.component_graph.nodes[node_id]
                result.append({
                    'name': node_data.get('name', os.path.basename(node_id)),
                    'file': node_data.get('file', ''),
                    'type': node_data.get('type', '')
                })
        return result
    
    def _generate_description(self, 
                            confidence: float, 
                            layer_counts: Dict[str, int],
                            violation_stats: Dict) -> str:
        """Generate a description of the Layered Architecture analysis.
        
        Args:
            confidence: The confidence score
            layer_counts: Dictionary of component counts by layer
            violation_stats: Statistics about layer dependency violations
            
        Returns:
            A human-readable description
        """
        if confidence < 0.3:
            return "The codebase shows minimal evidence of a Layered Architecture pattern."
        
        # Format layer distribution
        layer_desc = []
        for layer, count in layer_counts.items():
            if count > 0:
                layer_desc.append(f"{count} {layer.replace('_', ' ')} components")
        
        violation_count = violation_stats.get('count', 0)
        
        if confidence < 0.6:
            violation_text = ""
            if violation_count > 0:
                violation_text = f" There are {violation_count} dependency violations that go against layered architecture principles."
            
            return (
                f"The codebase shows some evidence of a Layered Architecture pattern, "
                f"with partial separation between {', '.join(layer.replace('_', ' ') for layer, count in layer_counts.items() if count > 0)} layers. "
                f"However, the layer boundaries are not consistently maintained.{violation_text}"
            )
        
        if confidence >= 0.8:
            violation_text = ""
            if violation_count > 0:
                violation_text = f" However, there are still {violation_count} dependency violations that should be addressed."
            
            return (
                f"The codebase strongly follows a Layered Architecture pattern with clear separation "
                f"between layers: {', '.join(layer_desc)}. Dependencies consistently flow from "
                f"higher to lower layers, following good layered architecture principles.{violation_text}"
            )
        
        violation_text = ""
        if violation_count > 0:
            violation_text = f" There are {violation_count} dependencies that violate the layered architecture principles."
        
        return (
            f"The codebase follows a Layered Architecture pattern with {', '.join(layer_desc)}. "
            f"Most dependencies follow the expected top-down flow between layers, "
            f"though there are some exceptions to strict layering.{violation_text}"
        )
    
    def _generate_recommendations(self, 
                                layer_counts: Dict[str, int],
                                layer_dependencies: Dict[str, Set[str]],
                                violation_stats: Dict) -> List[str]:
        """Generate recommendations for improving the Layered Architecture.
        
        Args:
            layer_counts: Dictionary of component counts by layer
            layer_dependencies: Dictionary of layer dependencies
            violation_stats: Statistics about layer violations
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for missing layers
        missing_layers = [layer for layer, count in layer_counts.items() if count == 0]
        if missing_layers:
            missing_layer_names = [layer.replace('_', ' ') for layer in missing_layers]
            recommendations.append(
                f"Consider adding {', '.join(missing_layer_names)} layers to complete the layered architecture"
            )
        
        # Check for violations and recommend fixes
        violation_count = violation_stats.get('count', 0)
        if violation_count > 0:
            # General recommendation for violations
            recommendations.append(
                f"Address the {violation_count} dependency violations to improve adherence to layered architecture principles"
            )
            
            # Most common violation
            most_common = violation_stats.get('most_common_violation')
            if most_common:
                source = most_common['source'].replace('_', ' ')
                target = most_common['target'].replace('_', ' ')
                count = most_common['count']
                
                recommendations.append(
                    f"Focus on eliminating the {count} dependencies from {source} to {target} layer "
                    f"by introducing appropriate abstractions or refactoring the code"
                )
        
        # Check for incorrect dependencies
        incorrect_dependencies = False
        standard_order = self.standard_layer_order
        
        for source_idx, source_layer in enumerate(standard_order):
            if source_layer in layer_dependencies:
                for target_layer in layer_dependencies[source_layer]:
                    target_idx = standard_order.index(target_layer) if target_layer in standard_order else -1
                    if target_idx >= 0 and target_idx <= source_idx:
                        incorrect_dependencies = True
                        break
        
        if incorrect_dependencies:
            recommendations.append(
                "Enforce stricter top-down dependencies between layers (presentation → business → data access → domain)"
            )
        
        # Check for layer balance
        if layer_counts['presentation'] == 0 and layer_counts['business'] > 0:
            recommendations.append(
                "Add a clear presentation layer to separate UI concerns from business logic"
            )
        
        if layer_counts['domain'] == 0 and (layer_counts['business'] > 0 or layer_counts['data_access'] > 0):
            recommendations.append(
                "Define a domain model layer to encapsulate core business entities and logic"
            )
        
        # Recommend directory structure improvements
        if sum(layer_counts.values()) > 0:
            has_directory_structure = False
            for node, data in self.component_graph.nodes(data=True):
                file_path = data.get('file', '')
                if file_path and data.get('layer') in self._categorize_component_by_path(file_path):
                    has_directory_structure = True
                    break
            
            if not has_directory_structure:
                recommendations.append(
                    "Reorganize code into directories that reflect the layered architecture "
                    "(controllers/, services/, repositories/, models/)"
                )
        
        # Recommend dependency inversion for clean boundaries
        if sum(layer_counts.values()) >= 8:  # Only for larger codebases
            recommendations.append(
                "Consider using interfaces at layer boundaries to further reduce coupling between layers"
            )
            
        # If significant violations exist, suggest the Dependency Inversion Principle
        if violation_count > 3:
            recommendations.append(
                "Apply the Dependency Inversion Principle to fix upward dependencies: "
                "higher-level modules should depend on abstractions, not concretions"
            )
        
        # Suggest visualizing the architecture
        if sum(layer_counts.values()) > 10:  # Only for more complex codebases
            recommendations.append(
                "Consider creating an architecture diagram to visualize your layered architecture "
                "and maintain awareness of proper layer dependencies"
            )
            
        # Add a fallback recommendation if we have none
        if not recommendations:
            recommendations.append(
                "Continue maintaining clear layer boundaries and respecting the dependency flow"
            )
            
        return recommendations