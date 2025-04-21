"""
Information Hiding architectural intent detector.

This module provides a pattern detector for identifying the Information Hiding
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

class InformationHidingIntent(ArchitecturalIntentPattern):
    """Pattern for detecting Information Hiding architectural principle.
    
    This pattern looks for indications that the codebase has been structured to
    hide implementation details and internal state, such as:
    
    1. Encapsulation of state with private/protected variables
    2. Use of interfaces/abstract classes to hide implementation details
    3. Well-defined public APIs with clear access boundaries
    4. Use of modules/packages to control visibility
    """
    
    def __init__(self):
        """Initialize the Information Hiding intent detector."""
        super().__init__(
            name="information_hiding",
            description="Identifies Information Hiding architectural principle",
            languages=["python", "javascript", "typescript", "java"],
        )
        
        # Indicators of encapsulation in different languages
        self.encapsulation_indicators = {
            "python": {
                "private_vars": r"self\._[a-zA-Z0-9_]+",  # Private instance variables
                "property_methods": r"@property",         # Property decorators
                "getter_methods": r"def get_[a-zA-Z0-9_]+",  # Getter methods
                "setter_methods": r"def set_[a-zA-Z0-9_]+",  # Setter methods
            },
            "javascript": {
                "private_vars": r"#[a-zA-Z0-9_]+|this\._[a-zA-Z0-9_]+",  # Private fields or underscore convention
                "getter_methods": r"get [a-zA-Z0-9_]+\(",  # ES6 getter methods
                "setter_methods": r"set [a-zA-Z0-9_]+\(",  # ES6 setter methods
            },
            "typescript": {
                "private_vars": r"private [a-zA-Z0-9_]+|#[a-zA-Z0-9_]+|this\._[a-zA-Z0-9_]+",  # TypeScript private modifiers
                "protected_vars": r"protected [a-zA-Z0-9_]+",  # Protected modifiers
                "interfaces": r"interface [a-zA-Z0-9_]+",  # Interfaces
                "abstract_classes": r"abstract class",  # Abstract classes
            },
            "java": {
                "private_vars": r"private [a-zA-Z0-9_<>]+",  # Private fields
                "protected_vars": r"protected [a-zA-Z0-9_<>]+",  # Protected fields
                "interfaces": r"interface [a-zA-Z0-9_]+",  # Interfaces
                "abstract_classes": r"abstract class",  # Abstract classes
            }
        }
        
        # Interface-related indicators
        self.interface_indicators = {
            "python": [
                r"class [A-Z][a-zA-Z0-9_]*\([A-Z][a-zA-Z0-9_]*\)",  # Class inheritance
                r"@abstractmethod",  # Abstract method decorator
                r"raise NotImplementedError",  # Common in interface methods
                r"ABC",  # Abstract Base Class
                r"Protocol"  # Python typing Protocol
            ],
            "javascript": [
                r"class \w+ extends",  # Class inheritance
                r"interface \w+",  # TypeScript interface
                r"implements",  # Interface implementation
            ],
            "java": [
                r"interface \w+",  # Java interface
                r"implements \w+",  # Interface implementation
                r"abstract class",  # Abstract class
                r"@Override",  # Method override annotation
            ]
        }
        
        # Module/package boundary indicators
        self.module_boundary_indicators = {
            "python": [
                r"^__all__\s*=",  # Explicit export list
                r"from\s+\.\s+import",  # Relative import (package internal)
                r"import\s+[a-zA-Z0-9_.]+\s+as\s+_",  # Private import
            ],
            "javascript": [
                r"export\s+{",  # ES6 named exports
                r"export\s+default",  # ES6 default export
                r"module\.exports",  # CommonJS exports
            ],
            "java": [
                r"public\s+class",  # Public class (exposed)
                r"package-private",  # Package private modifier
                r"class\s+[a-zA-Z0-9_]+\s*{",  # Default visibility (package)
            ]
        }
        
        # Initialize component mappings
        self.encapsulation_scores = {}  # Component to encapsulation score
        self.interface_usage_scores = {}  # Component to interface usage score
        self.module_boundary_scores = {}  # Component to module boundary score
        self.component_to_public_api = {}  # Component to public API size
        self.component_to_private_impl = {}  # Component to private implementation size
        
    def match(self, 
              tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        For Information Hiding, we analyze:
        1. Encapsulation practices (private/protected variables, getters/setters)
        2. Interface/abstract class usage
        3. Module/package visibility boundaries
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of component information dictionaries
        """
        logger.debug(f"InformationHidingIntent.match called for {file_path}")
        
        if not file_path:
            logger.warning("No file_path provided, returning empty result")
            return []
            
        components = []
        
        # Handle mock implementation case
        if hasattr(tree, 'content'):
            # For mock implementation, code is in tree.content
            if isinstance(code, str) and not code.strip():
                code = tree.content
        
        # Analyze encapsulation patterns
        encapsulation_metrics = self._analyze_encapsulation(code, language)
        
        # Analyze interface usage
        interface_metrics = self._analyze_interface_usage(code, language)
        
        # Analyze module boundaries
        module_metrics = self._analyze_module_boundaries(code, language, file_path)
        
        # Calculate overall information hiding score
        info_hiding_score = self._calculate_info_hiding_score(
            encapsulation_metrics, 
            interface_metrics, 
            module_metrics
        )
        
        # Create a component entry for this file
        component = {
            'type': 'component',
            'name': file_path,
            'path': file_path,
            'language': language,
            'info_hiding_score': info_hiding_score,
            'encapsulation': encapsulation_metrics,
            'interfaces': interface_metrics,
            'module_boundaries': module_metrics
        }
        
        components.append(component)
        logger.debug(f"Added information hiding component for {file_path}")
        
        return components
    
    def _analyze_encapsulation(self, code: str, language: str) -> Dict:
        """Analyze encapsulation patterns in the code.
        
        Args:
            code: The source code
            language: The language of the code
            
        Returns:
            Dictionary with encapsulation metrics
        """
        metrics = {
            'private_vars_count': 0,
            'protected_vars_count': 0,
            'getter_setter_count': 0,
            'property_count': 0,
            'public_method_count': 0,
            'private_method_count': 0,
            'encapsulation_ratio': 0.0,
            'public_api_size': 0,
            'private_impl_size': 0,
        }
        
        # Skip if language not supported
        if language not in self.encapsulation_indicators:
            return metrics
            
        indicators = self.encapsulation_indicators[language]
        
        # Count private variables
        if 'private_vars' in indicators:
            private_vars = re.findall(indicators['private_vars'], code)
            metrics['private_vars_count'] = len(private_vars)
        
        # Count protected variables
        if 'protected_vars' in indicators:
            protected_vars = re.findall(indicators['protected_vars'], code)
            metrics['protected_vars_count'] = len(protected_vars)
        
        # Count getter methods
        if 'getter_methods' in indicators:
            getters = re.findall(indicators['getter_methods'], code)
            metrics['getter_setter_count'] += len(getters)
        
        # Count setter methods
        if 'setter_methods' in indicators:
            setters = re.findall(indicators['setter_methods'], code)
            metrics['getter_setter_count'] += len(setters)
        
        # Count property decorators (Python)
        if 'property_methods' in indicators:
            properties = re.findall(indicators['property_methods'], code)
            metrics['property_count'] = len(properties)
        
        # Count public and private methods (language-specific)
        if language == "python":
            # Python methods starting with underscore are considered private
            private_methods = re.findall(r"def _[a-zA-Z0-9_]+\(", code)
            public_methods = re.findall(r"def (?!_)[a-zA-Z0-9_]+\(", code)
            metrics['private_method_count'] = len(private_methods)
            metrics['public_method_count'] = len(public_methods)
        elif language in ["javascript", "typescript"]:
            # JS/TS private methods with # or _ prefix
            private_methods = re.findall(r"(?:_|\#)[a-zA-Z0-9_]+\s*\(|private\s+[a-zA-Z0-9_]+\s*\(", code)
            # Public methods without private modifiers
            public_methods = re.findall(r"(?<!private\s+)(?<!protected\s+)(?<!_)(?<!\#)[a-zA-Z0-9_]+\s*\(", code)
            metrics['private_method_count'] = len(private_methods)
            metrics['public_method_count'] = len(public_methods)
        elif language == "java":
            # Java methods with private/protected keywords
            private_methods = re.findall(r"private\s+[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\s*\(", code)
            protected_methods = re.findall(r"protected\s+[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\s*\(", code)
            public_methods = re.findall(r"public\s+[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\s*\(", code)
            metrics['private_method_count'] = len(private_methods) + len(protected_methods)
            metrics['public_method_count'] = len(public_methods)
        
        # Calculate public API size and private implementation size
        metrics['public_api_size'] = metrics['public_method_count']
        metrics['private_impl_size'] = (
            metrics['private_vars_count'] + 
            metrics['protected_vars_count'] + 
            metrics['private_method_count']
        )
        
        # Calculate encapsulation ratio (private to public)
        total_members = metrics['public_api_size'] + metrics['private_impl_size']
        if total_members > 0:
            metrics['encapsulation_ratio'] = metrics['private_impl_size'] / total_members
        
        return metrics
    
    def _analyze_interface_usage(self, code: str, language: str) -> Dict:
        """Analyze interface and abstract class usage.
        
        Args:
            code: The source code
            language: The language of the code
            
        Returns:
            Dictionary with interface usage metrics
        """
        metrics = {
            'defines_interface': False,
            'implements_interface': False,
            'abstract_class_count': 0,
            'interface_count': 0,
            'interface_method_count': 0,
            'implementation_method_count': 0,
            'abstraction_ratio': 0.0,
        }
        
        # Skip if language not supported
        if language not in self.interface_indicators:
            return metrics
            
        indicators = self.interface_indicators[language]
        
        # Check each indicator
        for indicator in indicators:
            matches = re.findall(indicator, code)
            
            # Detect interface definitions
            if "interface" in indicator or "ABC" in indicator or "Protocol" in indicator:
                metrics['interface_count'] += len(matches)
                if len(matches) > 0:
                    metrics['defines_interface'] = True
            
            # Detect abstract classes
            if "abstract class" in indicator:
                metrics['abstract_class_count'] += len(matches)
            
            # Detect interface implementations
            if "implements" in indicator or "extends" in indicator:
                if len(matches) > 0:
                    metrics['implements_interface'] = True
            
            # Detect abstract methods
            if "@abstractmethod" in indicator or "raise NotImplementedError" in indicator:
                metrics['interface_method_count'] += len(matches)
            
            # Detect method overrides
            if "@Override" in indicator:
                metrics['implementation_method_count'] += len(matches)
        
        # Calculate abstraction ratio
        total_methods = metrics['interface_method_count'] + metrics['implementation_method_count']
        if total_methods > 0:
            metrics['abstraction_ratio'] = metrics['interface_method_count'] / total_methods
        
        return metrics
    
    def _analyze_module_boundaries(self, code: str, language: str, file_path: str) -> Dict:
        """Analyze module/package boundary definitions.
        
        Args:
            code: The source code
            language: The language of the code
            file_path: Path to the file
            
        Returns:
            Dictionary with module boundary metrics
        """
        metrics = {
            'explicit_exports': False,
            'internal_imports_count': 0,
            'external_imports_count': 0,
            'import_locality': 0.0,
            'package_private_count': 0,
            'public_count': 0,
            'boundary_clarity': 0.0,
        }
        
        # Skip if language not supported
        if language not in self.module_boundary_indicators:
            return metrics
            
        indicators = self.module_boundary_indicators[language]
        
        # Check for explicit exports
        for indicator in indicators:
            if "__all__" in indicator or "export" in indicator or "module.exports" in indicator:
                if re.search(indicator, code):
                    metrics['explicit_exports'] = True
                    break
        
        # Analyze imports (Python)
        if language == "python":
            # Count internal imports (relative imports)
            internal_imports = re.findall(r"from\s+\.\s+import|from\s+\.[a-zA-Z0-9_]+\s+import", code)
            metrics['internal_imports_count'] = len(internal_imports)
            
            # Count external imports (absolute imports)
            external_imports = re.findall(r"import\s+[a-zA-Z0-9_.]+|from\s+(?!\.)(?!self)[a-zA-Z0-9_.]+\s+import", code)
            metrics['external_imports_count'] = len(external_imports)
        
        # Analyze exports/imports (JavaScript/TypeScript)
        elif language in ["javascript", "typescript"]:
            # Count internal imports (relative imports)
            internal_imports = re.findall(r"import\s+.*\s+from\s+['\"]\..*['\"]", code)
            metrics['internal_imports_count'] = len(internal_imports)
            
            # Count external imports (node_modules or absolute)
            external_imports = re.findall(r"import\s+.*\s+from\s+['\"](?!\.).*['\"]", code)
            metrics['external_imports_count'] = len(external_imports)
            
        # Analyze package visibility (Java)
        elif language == "java":
            # Count public members
            public_members = re.findall(r"public\s+(?:class|interface|enum|[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\s*\()", code)
            metrics['public_count'] = len(public_members)
            
            # Count package-private members (no visibility modifier)
            package_private = re.findall(r"(?<!public\s+)(?<!private\s+)(?<!protected\s+)(class|interface|enum|[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\s*\()", code)
            metrics['package_private_count'] = len(package_private)
        
        # Calculate import locality ratio (internal vs total)
        total_imports = metrics['internal_imports_count'] + metrics['external_imports_count']
        if total_imports > 0:
            metrics['import_locality'] = metrics['internal_imports_count'] / total_imports
        
        # Calculate boundary clarity (existence of explicit export mechanisms)
        metrics['boundary_clarity'] = 1.0 if metrics['explicit_exports'] else 0.0
        
        return metrics
    
    def _calculate_info_hiding_score(self, 
                                    encapsulation_metrics: Dict, 
                                    interface_metrics: Dict, 
                                    module_metrics: Dict) -> float:
        """Calculate overall information hiding score.
        
        Args:
            encapsulation_metrics: Metrics related to encapsulation
            interface_metrics: Metrics related to interface usage
            module_metrics: Metrics related to module boundaries
            
        Returns:
            Overall information hiding score (0.0-1.0)
        """
        # Weight factors (can be adjusted)
        weights = {
            'encapsulation': 0.4,
            'interface_usage': 0.4,
            'module_boundaries': 0.2,
        }
        
        # Calculate encapsulation score (0.0-1.0)
        encapsulation_score = encapsulation_metrics.get('encapsulation_ratio', 0.0)
        
        # Calculate interface usage score (0.0-1.0)
        interface_score = 0.0
        if interface_metrics.get('defines_interface', False):
            interface_score += 0.5
        if interface_metrics.get('implements_interface', False):
            interface_score += 0.3
        if interface_metrics.get('abstraction_ratio', 0.0) > 0:
            interface_score += 0.2 * interface_metrics['abstraction_ratio']
        interface_score = min(1.0, interface_score)  # Cap at 1.0
        
        # Calculate module boundary score (0.0-1.0)
        boundary_score = 0.0
        if module_metrics.get('explicit_exports', False):
            boundary_score += 0.5
        boundary_score += 0.5 * module_metrics.get('import_locality', 0.0)
        
        # Calculate weighted average
        overall_score = (
            weights['encapsulation'] * encapsulation_score +
            weights['interface_usage'] * interface_score +
            weights['module_boundaries'] * boundary_score
        )
        
        return overall_score
        
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Information Hiding, we are tracking:
        1. Components and their information hiding scores
        2. Interface definitions and implementations
        3. Module boundaries and visibilities
        
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
                    info_hiding_score=match.get('info_hiding_score', 0.0),
                    defines_interface=match.get('interfaces', {}).get('defines_interface', False),
                    implements_interface=match.get('interfaces', {}).get('implements_interface', False),
                    encapsulation_ratio=match.get('encapsulation', {}).get('encapsulation_ratio', 0.0),
                    public_api_size=match.get('encapsulation', {}).get('public_api_size', 0),
                    private_impl_size=match.get('encapsulation', {}).get('private_impl_size', 0),
                )
                
                # Track component scores
                self.encapsulation_scores[component_name] = match.get('encapsulation', {}).get('encapsulation_ratio', 0.0)
                self.interface_usage_scores[component_name] = 1.0 if match.get('interfaces', {}).get('defines_interface', False) else 0.0
                self.module_boundary_scores[component_name] = match.get('module_boundaries', {}).get('boundary_clarity', 0.0)
                self.component_to_public_api[component_name] = match.get('encapsulation', {}).get('public_api_size', 0)
                self.component_to_private_impl[component_name] = match.get('encapsulation', {}).get('private_impl_size', 0)
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Information Hiding architectural intent.
        
        We analyze:
        1. Overall information hiding scores
        2. Interface definitions and usage
        3. Encapsulation practices
        4. Module boundary definitions
        
        Returns:
            A dictionary containing the information hiding intent details
        """
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Calculate average information hiding score
        info_hiding_scores = [
            self.component_graph.nodes[node].get('info_hiding_score', 0.0)
            for node in self.component_graph.nodes
        ]
        avg_info_hiding = sum(info_hiding_scores) / len(info_hiding_scores) if info_hiding_scores else 0.0
        
        # Count interface definitions and implementations
        interface_definitions = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('defines_interface', False)
        )
        interface_implementations = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('implements_interface', False)
        )
        
        # Calculate encapsulation metrics
        encapsulation_scores = list(self.encapsulation_scores.values())
        avg_encapsulation = sum(encapsulation_scores) / len(encapsulation_scores) if encapsulation_scores else 0.0
        
        # Calculate public/private ratio
        total_public_api = sum(self.component_to_public_api.values())
        total_private_impl = sum(self.component_to_private_impl.values())
        public_private_ratio = total_private_impl / total_public_api if total_public_api > 0 else 0.0
        
        # Calculate interface usage metrics
        interface_scores = list(self.interface_usage_scores.values())
        avg_interface_usage = sum(interface_scores) / len(interface_scores) if interface_scores else 0.0
        
        # Calculate module boundary metrics
        boundary_scores = list(self.module_boundary_scores.values())
        avg_boundary_clarity = sum(boundary_scores) / len(boundary_scores) if boundary_scores else 0.0
        
        # Calculate overall confidence score
        # Weighted average of various factors
        confidence = (
            0.4 * avg_info_hiding +  # Overall information hiding score
            0.2 * avg_encapsulation +  # Encapsulation practices
            0.2 * avg_interface_usage +  # Interface usage
            0.1 * (interface_implementations / len(self.component_graph.nodes) if len(self.component_graph.nodes) > 0 else 0.0) +  # Interface implementation ratio
            0.1 * avg_boundary_clarity  # Module boundary clarity
        )
        
        # Create metrics dictionary
        metrics = {
            "avg_information_hiding_score": avg_info_hiding,
            "interface_definitions": interface_definitions,
            "interface_implementations": interface_implementations,
            "avg_encapsulation_ratio": avg_encapsulation,
            "public_private_ratio": public_private_ratio,
            "total_public_api_size": total_public_api,
            "total_private_impl_size": total_private_impl,
            "avg_boundary_clarity": avg_boundary_clarity
        }
        
        # Generate description
        description = self._generate_description(
            metrics,
            confidence,
            len(self.component_graph.nodes)
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, confidence)
        
        # Generate final analysis
        return {
            "type": self.name,
            "confidence": confidence,
            "components_analyzed": len(self.component_graph.nodes),
            "metrics": metrics,
            "recommendations": recommendations,
            "description": description
        }
    
    def _generate_description(self, 
                             metrics: Dict, 
                             confidence: float,
                             component_count: int) -> str:
        """Generate a human-readable description of the information hiding findings.
        
        Args:
            metrics: The calculated metrics
            confidence: Overall confidence score
            component_count: Number of components analyzed
            
        Returns:
            A description of the architectural intent
        """
        # Confidence level description
        if confidence > 0.8:
            confidence_desc = "strong"
        elif confidence > 0.6:
            confidence_desc = "good"
        elif confidence > 0.4:
            confidence_desc = "moderate"
        elif confidence > 0.2:
            confidence_desc = "weak"
        else:
            confidence_desc = "very little"
            
        # Main description
        desc = f"The codebase shows {confidence_desc} evidence of Information Hiding principles. "
        
        # Add encapsulation details
        enc_ratio = metrics["avg_encapsulation_ratio"]
        if enc_ratio > 0.7:
            desc += "Components generally have good encapsulation with strong separation of public API and private implementation details. "
        elif enc_ratio > 0.4:
            desc += "Components show moderate encapsulation with some separation of public API and private implementation. "
        else:
            desc += "Components generally lack strong encapsulation, with limited separation between public and private members. "
        
        # Add interface usage details
        interface_defs = metrics["interface_definitions"]
        interface_impls = metrics["interface_implementations"]
        if interface_defs > 0 and interface_impls > 0:
            desc += f"The codebase uses interfaces/abstract classes ({interface_defs} definitions with {interface_impls} implementations) to separate interface from implementation. "
        elif interface_defs > 0:
            desc += f"The codebase defines interfaces/abstract classes ({interface_defs} found) but has limited implementation separation. "
        else:
            desc += "The codebase makes minimal use of interfaces or abstract classes to separate interface from implementation. "
        
        # Add module boundary details
        boundary_clarity = metrics["avg_boundary_clarity"]
        if boundary_clarity > 0.7:
            desc += "Module/package boundaries are clearly defined with explicit exports and strong visibility control."
        elif boundary_clarity > 0.3:
            desc += "Module/package boundaries are partially defined with some explicit visibility control."
        else:
            desc += "Module/package boundaries lack clear definition, with limited explicit visibility control."
        
        return desc
    
    def _generate_recommendations(self, metrics: Dict, confidence: float) -> List[str]:
        """Generate recommendations for improving information hiding.
        
        Args:
            metrics: The calculated metrics
            confidence: Overall confidence score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Only generate recommendations if score is below excellent
        if confidence < 0.8:
            # Encapsulation recommendations
            if metrics["avg_encapsulation_ratio"] < 0.6:
                recommendations.append(
                    "Improve encapsulation by making implementation details private and exposing a clear public API"
                )
            
            # Interface recommendations
            if metrics["interface_definitions"] == 0:
                recommendations.append(
                    "Consider using interfaces or abstract classes to separate interface from implementation"
                )
            elif metrics["interface_implementations"] < metrics["interface_definitions"]:
                recommendations.append(
                    "Increase the use of existing interfaces throughout the codebase for more consistent abstraction"
                )
            
            # Module boundary recommendations
            if metrics["avg_boundary_clarity"] < 0.5:
                recommendations.append(
                    "Define clearer module boundaries with explicit exports and stronger visibility control"
                )
            
            # Public API size recommendations
            if metrics["public_private_ratio"] < 1.0:
                recommendations.append(
                    "Reduce the size of public APIs relative to private implementation to improve information hiding"
                )
        
        return recommendations