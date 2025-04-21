"""
Separation of Concerns architectural intent detector.

This module provides a pattern detector for identifying the Separation of Concerns
architectural principle in codebases.
"""

from typing import Dict, List, Optional, Set, Tuple, Union, Counter
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from ...pattern_base import QueryBasedPattern
from .architectural_intent_base import ArchitecturalIntentPattern

logger = logging.getLogger(__name__)

class SeparationOfConcernsIntent(ArchitecturalIntentPattern):
    """Pattern for detecting Separation of Concerns architectural principle.
    
    This pattern looks for indications that the codebase has been structured to
    separate different types of concerns, such as:
    
    1. Layer-based separation (presentation, business logic, data access)
    2. Domain-based separation (features organized by domain concepts)
    3. Component-based separation (self-contained components with clear boundaries)
    """
    
    def __init__(self):
        """Initialize the Separation of Concerns intent detector."""
        super().__init__(
            name="separation_of_concerns",
            description="Identifies Separation of Concerns architectural principle",
            languages=["python", "javascript", "typescript", "java"],
        )
        
        # Layers typically found in well-structured applications
        self.known_layers = {
            # Web/application layers
            "controller": ["controller", "route", "endpoint", "api", "resource", "handler", "action"],
            "service": ["service", "manager", "coordinator", "orchestrator", "facade", "application"],
            "repository": ["repository", "dao", "store", "storage", "persistence"],
            "model": ["model", "entity", "domain", "dto", "schema", "record"],
            "view": ["view", "template", "page", "component", "widget", "screen", "ui"],
            # Utility/cross-cutting layers
            "util": ["util", "helper", "common", "shared", "lib", "tool"],
            "config": ["config", "setting", "property", "constant", "environment"],
            "exception": ["exception", "error", "fault", "failure"],
            # Testing layers
            "test": ["test", "spec", "mock", "stub", "fixture"],
        }
        
        # Indicators of domain-driven separation
        self.domain_indicators = ["user", "auth", "account", "payment", "order", "product", 
                                 "customer", "inventory", "billing", "shipping", "notification"]
        
        # Initialize component mappings
        self.component_to_layer = {}
        self.component_to_domain = {}
        self.imports_between_components = defaultdict(list)
        
    def match(self, 
              tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        For the Separation of Concerns detector, we extract information about:
        1. Class/module responsibilities
        2. Import/dependency relationships
        3. Layer indicators in names and paths
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of component information dictionaries
        """
        logger.debug(f"SeparationOfConcernsIntent.match called for {file_path}")
        
        if not file_path:
            logger.warning("No file_path provided, returning empty result")
            return []
            
        components = []
        
        # Extract import statements to track dependencies
        try:
            imports = self._extract_imports(tree, code, language)
            logger.debug(f"Extracted {len(imports)} imports from {file_path}")
        except Exception as e:
            # Handle extraction errors - may happen with mock implementation
            logger.warning(f"Error extracting imports: {e}")
            imports = []
        
        # Determine the responsibilities of this file
        responsibilities = self._determine_responsibilities(tree, code, language, file_path)
        logger.debug(f"Detected responsibilities for {file_path}: {responsibilities}")
        
        # Determine the layer this file belongs to
        layer = self._determine_layer(file_path, code, language)
        logger.debug(f"Detected layer for {file_path}: {layer}")
        
        # Determine the domain this file belongs to
        domain = self._determine_domain(file_path, code, language)
        logger.debug(f"Detected domain for {file_path}: {domain}")
        
        # Create a component entry for this file
        component = {
            'type': 'component',
            'name': file_path,
            'path': file_path,
            'language': language,
            'layer': layer,
            'domain': domain,
            'responsibilities': responsibilities,
            'imports': imports
        }
        
        components.append(component)
        logger.debug(f"Added component for {file_path}: {component}")
        
        return components
    
    def _extract_imports(self, tree, code: str, language: str) -> List[str]:
        """Extract import statements from the code.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            
        Returns:
            List of imported modules/files
        """
        # Handle mock implementation case
        if hasattr(tree, 'content'):
            # For mock implementation, code is in tree.content
            if isinstance(code, str) and not code.strip():
                code = tree.content
        
        imports = []
        
        # Simple regex-based approach for prototype
        if language == "python":
            # Match Python imports
            import_pattern = r'^(?:from\s+([\w.]+)\s+import|import\s+([\w.,\s]+))'
            for match in re.finditer(import_pattern, code, re.MULTILINE):
                from_import = match.group(1)
                regular_import = match.group(2)
                if from_import:
                    imports.append(from_import)
                elif regular_import:
                    # Handle multiple imports in one statement
                    for imp in regular_import.split(','):
                        imports.append(imp.strip())
        
        elif language in ["javascript", "typescript"]:
            # Match JS/TS imports
            import_pattern = r'(?:import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\))'
            for match in re.finditer(import_pattern, code):
                es_import = match.group(1)
                cjs_import = match.group(2)
                imports.append(es_import or cjs_import)
                
        return imports
    
    def _determine_responsibilities(self, tree, code: str, language: str, file_path: str) -> List[str]:
        """Determine the responsibilities of this file based on its contents.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Path to the file
            
        Returns:
            List of identified responsibilities
        """
        # This is a simplified approach for the prototype
        # In a full implementation, we would do more sophisticated analysis
        
        responsibilities = []
        
        # Check for common responsibility indicators in function/method names
        if language == "python":
            patterns = [
                # UI/Controller responsibilities
                r'def (?:render|display|show|handle|get|post|put|delete|route)_(\w+)',
                # Business logic responsibilities
                r'def (?:process|calculate|validate|compute|analyze|transform)_(\w+)',
                # Data access responsibilities
                r'def (?:save|load|find|query|fetch|retrieve|store|update|delete)_(\w+)',
            ]
            
            for pattern in patterns:
                for match in re.finditer(pattern, code, re.IGNORECASE):
                    responsibility = match.group(1).replace('_', ' ')
                    responsibilities.append(responsibility)
        
        # If we didn't find specific responsibilities, infer from filename
        if not responsibilities:
            filename = os.path.basename(file_path)
            name_root = os.path.splitext(filename)[0].lower()
            
            # Check for responsibility indicators in the filename
            for indicator in ["controller", "service", "repository", "model", "view", "util"]:
                if indicator in name_root:
                    responsibilities.append(indicator)
        
        return responsibilities
    
    def _determine_layer(self, file_path: str, code: str, language: str) -> Optional[str]:
        """Determine which layer this file belongs to.
        
        Args:
            file_path: Path to the file
            code: The source code
            language: The language of the code
            
        Returns:
            The identified layer or None
        """
        # Convert path to lowercase for matching
        path_lower = file_path.lower()
        filename = os.path.basename(path_lower)
        name_root = os.path.splitext(filename)[0]
        
        # Check path components for layer indicators
        path_components = path_lower.split(os.sep)
        
        # Try to match directory or file names to known layers
        for layer, indicators in self.known_layers.items():
            # Check directories in path
            for component in path_components:
                if component in indicators:
                    return layer
                    
            # Check filename
            for indicator in indicators:
                if indicator in name_root:
                    return layer
        
        # If no layer found from path, try content-based heuristics
        # This is simplified for the prototype
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1).lower()
            
            for layer, indicators in self.known_layers.items():
                for indicator in indicators:
                    if indicator in class_name:
                        return layer
        
        # Default to unknown layer
        return None
    
    def _determine_domain(self, file_path: str, code: str, language: str) -> Optional[str]:
        """Determine which domain this file belongs to.
        
        Args:
            file_path: Path to the file
            code: The source code
            language: The language of the code
            
        Returns:
            The identified domain or None
        """
        # Convert path to lowercase for matching
        path_lower = file_path.lower()
        
        # Check path components for domain indicators
        path_components = path_lower.split(os.sep)
        
        # Try to match directory names to known domains
        for component in path_components:
            if component in self.domain_indicators:
                return component
        
        # Check filename for domain indicators
        filename = os.path.basename(path_lower)
        name_root = os.path.splitext(filename)[0]
        
        for domain in self.domain_indicators:
            if domain in name_root:
                return domain
        
        # If no domain found from path, try content-based heuristics
        # This is simplified for the prototype
        for domain in self.domain_indicators:
            # Count occurrences of domain name in code
            if re.search(r'\b' + domain + r'\b', code, re.IGNORECASE):
                return domain
        
        # Default to unknown domain
        return None
    
    def _process_pattern_matches(self, 
                                pattern_name: str, 
                                matches: List[Dict],
                                file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Separation of Concerns, we are looking for:
        1. Components and their layers/domains
        2. Dependencies between components
        
        Args:
            pattern_name: The name of the pattern
            matches: List of pattern matches
            file_path: Path to the file
        """
        if pattern_name != self.name:
            return
            
        for match in matches:
            # Each match represents a component
            component_name = match.get('path', file_path)
            
            # Add component node to graph if not already present
            if not self.component_graph.has_node(component_name):
                self.component_graph.add_node(
                    component_name,
                    type='component',
                    layer=match.get('layer'),
                    domain=match.get('domain'),
                    responsibilities=match.get('responsibilities', [])
                )
                
                # Track component mappings
                if match.get('layer'):
                    self.component_to_layer[component_name] = match['layer']
                    
                if match.get('domain'):
                    self.component_to_domain[component_name] = match['domain']
            
            # Process imports to add edges
            imports = match.get('imports', [])
            for imported in imports:
                self.imports_between_components[component_name].append(imported)
    
    def _finalize_component_graph(self) -> None:
        """Finalize the component graph by adding edges for dependencies."""
        # Add edges for imports
        for component, imports in self.imports_between_components.items():
            for imported in imports:
                # Find best matching node for the import
                best_match = None
                highest_score = 0
                
                for node in self.component_graph.nodes:
                    # Simple string matching heuristic
                    # In a real implementation, we would use more sophisticated matching
                    if imported in node:
                        score = len(imported) / len(node)
                        if score > highest_score:
                            highest_score = score
                            best_match = node
                
                if best_match and highest_score > 0.5:  # Threshold for matching
                    # Add edge for dependency
                    self.component_graph.add_edge(
                        component, 
                        best_match,
                        type='imports'
                    )
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Separation of Concerns architectural intent.
        
        We look for:
        1. Layer-based separation (clean layering)
        2. Domain-based separation
        3. Limited cross-cutting dependencies
        
        Returns:
            A dictionary containing the detected architectural intent details
        """
        # Finalize the graph first
        self._finalize_component_graph()
        
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Analyze layering
        layer_analysis = self._analyze_layers()
        
        # Analyze domain separation
        domain_analysis = self._analyze_domains()
        
        # Combine the analyses
        confidence = (layer_analysis['confidence'] + domain_analysis['confidence']) / 2
        
        # Determine separation pattern based on confidence scores
        primary_pattern = "unknown"
        if layer_analysis['confidence'] > domain_analysis['confidence']:
            primary_pattern = "layer-based" if layer_analysis['confidence'] > 0.5 else "unknown"
        else:
            primary_pattern = "domain-based" if domain_analysis['confidence'] > 0.5 else "unknown"
        
        # Generate final analysis
        return {
            "type": self.name,
            "confidence": confidence,
            "primary_pattern": primary_pattern,
            "components_analyzed": len(self.component_graph.nodes),
            "layer_analysis": layer_analysis,
            "domain_analysis": domain_analysis,
            "description": self._generate_description(layer_analysis, domain_analysis, primary_pattern)
        }
    
    def _analyze_layers(self) -> Dict:
        """Analyze layer-based separation of concerns.
        
        Returns:
            Dictionary with layer analysis results
        """
        # Count components by layer
        layer_counts = Counter(self.component_to_layer.values())
        
        # Calculate layer diversity (how many different layers are present)
        layer_diversity = len(layer_counts)
        
        # Calculate layer confidence based on diversity and distribution
        layer_confidence = 0.0
        if layer_diversity > 1:
            # More layers = better separation
            layer_confidence = min(1.0, layer_diversity / 5.0)  # Normalize, max at 5 layers
            
            # Check if layers are balanced (not perfect, but a reasonable heuristic)
            max_count = max(layer_counts.values())
            min_count = min(layer_counts.values()) if layer_counts else 0
            if max_count > 0:
                balance_factor = min_count / max_count if min_count > 0 else 0
                # Adjust confidence based on balance
                layer_confidence *= (0.5 + 0.5 * balance_factor)  # Balance affects 50% of score
        
        # Analyze dependencies between layers
        layer_violations = 0
        clean_layering = False
        layer_dependency_directions = defaultdict(int)
        
        for src, dst in self.component_graph.edges:
            src_layer = self.component_to_layer.get(src)
            dst_layer = self.component_to_layer.get(dst)
            
            if src_layer and dst_layer and src_layer != dst_layer:
                # Count dependencies between layers
                layer_dependency_directions[(src_layer, dst_layer)] += 1
        
        # Determine if there's a clean layering pattern
        # We look for consistent one-way dependencies between layers
        if layer_dependency_directions:
            # Check for violations of clean architecture
            # (e.g., if data layer depends on service layer)
            layer_order = ["view", "controller", "service", "repository", "model"]
            
            for (src_layer, dst_layer), count in layer_dependency_directions.items():
                if src_layer in layer_order and dst_layer in layer_order:
                    src_idx = layer_order.index(src_layer)
                    dst_idx = layer_order.index(dst_layer)
                    
                    # In clean architecture, dependencies should flow inward
                    # (higher layers depend on lower layers)
                    if src_idx > dst_idx:
                        layer_violations += count
            
            # Calculate clean layering score
            total_deps = sum(layer_dependency_directions.values())
            clean_layering = (total_deps - layer_violations) / total_deps if total_deps > 0 else 0
            
            # Adjust confidence based on clean layering
            layer_confidence *= (0.7 + 0.3 * clean_layering)  # Clean layering affects 30% of score
        
        return {
            "confidence": layer_confidence,
            "layer_diversity": layer_diversity,
            "layer_distribution": dict(layer_counts),
            "clean_layering_score": clean_layering,
            "layer_violations": layer_violations,
            "dependencies_between_layers": dict(layer_dependency_directions)
        }
    
    def _analyze_domains(self) -> Dict:
        """Analyze domain-based separation of concerns.
        
        Returns:
            Dictionary with domain analysis results
        """
        # Count components by domain
        domain_counts = Counter(self.component_to_domain.values())
        
        # Calculate domain diversity (how many different domains are present)
        domain_diversity = len(domain_counts)
        
        # Calculate domain confidence based on diversity and distribution
        domain_confidence = 0.0
        if domain_diversity > 1:
            # More domains = better separation
            domain_confidence = min(1.0, domain_diversity / 5.0)  # Normalize, max at 5 domains
            
            # Check if domains are balanced (not perfect, but a reasonable heuristic)
            max_count = max(domain_counts.values())
            min_count = min(domain_counts.values()) if domain_counts else 0
            if max_count > 0:
                balance_factor = min_count / max_count if min_count > 0 else 0
                # Adjust confidence based on balance
                domain_confidence *= (0.5 + 0.5 * balance_factor)  # Balance affects 50% of score
        
        # Analyze dependencies between domains
        cross_domain_dependencies = 0
        internal_dependencies = 0
        domain_coupling = {}
        
        for src, dst in self.component_graph.edges:
            src_domain = self.component_to_domain.get(src)
            dst_domain = self.component_to_domain.get(dst)
            
            if src_domain and dst_domain:
                if src_domain != dst_domain:
                    # Count cross-domain dependencies
                    cross_domain_dependencies += 1
                    
                    # Track coupling between domains
                    domain_pair = tuple(sorted([src_domain, dst_domain]))
                    domain_coupling[domain_pair] = domain_coupling.get(domain_pair, 0) + 1
                else:
                    # Count internal dependencies
                    internal_dependencies += 1
        
        # Calculate domain isolation score
        total_deps = cross_domain_dependencies + internal_dependencies
        domain_isolation = internal_dependencies / total_deps if total_deps > 0 else 0
        
        # Adjust confidence based on domain isolation
        domain_confidence *= (0.6 + 0.4 * domain_isolation)  # Domain isolation affects 40% of score
        
        return {
            "confidence": domain_confidence,
            "domain_diversity": domain_diversity,
            "domain_distribution": dict(domain_counts),
            "domain_isolation_score": domain_isolation,
            "cross_domain_dependencies": cross_domain_dependencies,
            "internal_dependencies": internal_dependencies,
            "domain_coupling": domain_coupling
        }
    
    def _generate_description(self, 
                             layer_analysis: Dict, 
                             domain_analysis: Dict,
                             primary_pattern: str) -> str:
        """Generate a human-readable description of the architectural intent findings.
        
        Args:
            layer_analysis: Results of layer analysis
            domain_analysis: Results of domain analysis
            primary_pattern: The primary separation pattern identified
            
        Returns:
            A description of the architectural intent
        """
        descriptions = []
        
        # Overall assessment
        overall_confidence = (layer_analysis['confidence'] + domain_analysis['confidence']) / 2
        confidence_phrase = "strong" if overall_confidence > 0.8 else \
                           "moderate" if overall_confidence > 0.5 else \
                           "weak" if overall_confidence > 0.2 else "very little"
        
        descriptions.append(f"The codebase shows {confidence_phrase} evidence of Separation of Concerns.")
        
        # Primary pattern
        if primary_pattern == "layer-based":
            layer_div = layer_analysis['layer_diversity']
            layers = list(layer_analysis['layer_distribution'].keys())
            layers_str = ", ".join(str(l) for l in layers if l is not None)
            
            descriptions.append(f"The primary separation pattern is layer-based, with {layer_div} identified layers: {layers_str}.")
            
            # Comment on layering cleanliness
            clean_score = layer_analysis['clean_layering_score']
            if clean_score > 0.8:
                descriptions.append("The codebase exhibits very clean layering with proper dependency direction.")
            elif clean_score > 0.5:
                descriptions.append("The layering is moderately clean with some violations of dependency direction.")
            elif clean_score > 0.2:
                descriptions.append("The layering has significant violations of clean dependency principles.")
            else:
                descriptions.append("Despite having layers, dependencies between them appear arbitrary.")
                
        elif primary_pattern == "domain-based":
            domain_div = domain_analysis['domain_diversity']
            domains = list(domain_analysis['domain_distribution'].keys())
            domains_str = ", ".join(str(d) for d in domains if d is not None)
            
            descriptions.append(f"The primary separation pattern is domain-based, with {domain_div} identified domains: {domains_str}.")
            
            # Comment on domain isolation
            isolation_score = domain_analysis['domain_isolation_score']
            if isolation_score > 0.8:
                descriptions.append("Domains are well-isolated with minimal cross-domain dependencies.")
            elif isolation_score > 0.5:
                descriptions.append("Domains have moderate isolation with some cross-domain coupling.")
            elif isolation_score > 0.2:
                descriptions.append("Domains show significant coupling with many cross-domain dependencies.")
            else:
                descriptions.append("Despite having domain separation, components are highly coupled across domains.")
        else:
            descriptions.append("No clear separation pattern was identified.")
        
        return " ".join(descriptions)