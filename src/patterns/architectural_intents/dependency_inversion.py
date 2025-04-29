"""
Dependency Inversion architectural intent detector.

This module provides a pattern detector for identifying the Dependency Inversion
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

class DependencyInversionIntent(ArchitecturalIntentPattern):
    """Pattern for detecting Dependency Inversion architectural principle.
    
    This pattern looks for indications that the codebase follows the Dependency
    Inversion Principle (DIP), one of the SOLID principles, such as:
    
    1. High-level modules depend on abstractions, not concrete implementations
    2. Use of dependency injection to inject dependencies
    3. Factory patterns for creating implementations
    4. Dependency on interfaces rather than concrete classes
    """
    
    def __init__(self):
        """Initialize the Dependency Inversion intent detector."""
        super().__init__(
            name="dependency_inversion",
            description="Identifies Dependency Inversion architectural principle",
            languages=["python", "javascript", "typescript", "java"],
        )
        
        # Indicators of abstractions in different languages
        self.abstraction_indicators = {
            "python": {
                "interfaces": [
                    r"class\s+[A-Z][a-zA-Z0-9_]*\([^)]*ABC[^)]*\)",  # ABC inheritance
                    r"class\s+[A-Z][a-zA-Z0-9_]*\([^)]*Protocol[^)]*\)",  # Protocol
                    r"@abstractmethod",  # Abstract method decorator
                ],
                "abstract_methods": [
                    r"@abstractmethod",
                    r"raise\s+NotImplementedError",
                    r"pass\s*$",  # Empty method implementations
                ]
            },
            "javascript": {
                "interfaces": [
                    r"interface\s+[A-Z][a-zA-Z0-9_]*",  # TypeScript interface
                    r"abstract\s+class\s+[A-Z][a-zA-Z0-9_]*",  # Abstract class
                ],
                "abstract_methods": [
                    r"abstract\s+[a-zA-Z0-9_]+\([^)]*\)",  # Abstract methods
                    r"throw\s+new\s+Error\(\s*['\"]Not implemented",  # Not implemented error
                ]
            },
            "typescript": {
                "interfaces": [
                    r"interface\s+[A-Z][a-zA-Z0-9_]*",  # TypeScript interface
                    r"abstract\s+class\s+[A-Z][a-zA-Z0-9_]*",  # Abstract class
                ],
                "abstract_methods": [
                    r"abstract\s+[a-zA-Z0-9_]+\([^)]*\)",  # Abstract methods
                    r"throw\s+new\s+Error\(\s*['\"]Not implemented",  # Not implemented error
                ]
            },
            "java": {
                "interfaces": [
                    r"interface\s+[A-Z][a-zA-Z0-9_]*",  # Java interface
                    r"abstract\s+class\s+[A-Z][a-zA-Z0-9_]*",  # Abstract class
                ],
                "abstract_methods": [
                    r"abstract\s+[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\([^)]*\)",  # Abstract methods
                ]
            }
        }
        
        # Indicators of dependency injection in different languages
        self.di_indicators = {
            "python": [
                r"def\s+__init__\s*\([^)]*\):[^;]*\bself\.[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+",  # Constructor injection
                r"@inject",  # Injection decorator
                r"\.inject\(.*\)",  # DI container injection
            ],
            "javascript": [
                r"constructor\s*\([^)]*\)[^{]*{[^}]*this\.[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+",  # Constructor injection
                r"@inject",  # Decoration injection
                r"\.inject\(.*\)",  # DI framework injection
            ],
            "typescript": [
                r"constructor\s*\([^)]*\)[^{]*{[^}]*this\.[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+",  # Constructor injection
                r"@inject",  # Decoration injection
                r"@Inject",  # Alternative decoration
                r"\.inject\(.*\)",  # DI framework injection
            ],
            "java": [
                r"@Inject",  # Java injection annotation
                r"@Autowired",  # Spring injection
                r"@Dependency",  # Generic DI annotation
            ]
        }
        
        # Indicators of factory patterns
        self.factory_indicators = {
            "python": [
                r"def\s+create_[a-zA-Z0-9_]+",  # Factory method
                r"class\s+[a-zA-Z0-9_]*Factory",  # Factory class
                r"def\s+get_instance\s*\(",  # Instance getter
            ],
            "javascript": [
                r"function\s+create[A-Z][a-zA-Z0-9_]*",  # Factory function
                r"class\s+[a-zA-Z0-9_]*Factory",  # Factory class
                r"\.getInstance\(",  # Get instance method
            ],
            "typescript": [
                r"function\s+create[A-Z][a-zA-Z0-9_]*",  # Factory function 
                r"class\s+[a-zA-Z0-9_]*Factory",  # Factory class
                r"\.getInstance\(",  # Get instance method
            ],
            "java": [
                r"public\s+static\s+[a-zA-Z0-9_<>]+\s+create[A-Z][a-zA-Z0-9_]*",  # Factory method
                r"class\s+[a-zA-Z0-9_]*Factory",  # Factory class
                r"\.getInstance\(",  # Get instance method
            ]
        }
        
        # Initialize component mappings
        self.abstraction_scores = {}  # Component to abstraction score
        self.di_scores = {}  # Component to dependency injection score
        self.factory_scores = {}  # Component to factory usage score
        self.interface_to_implementation = defaultdict(list)  # Map interfaces to implementations
        self.implementation_to_interface = {}  # Map implementations to interfaces
        self.high_level_modules = set()  # High-level modules (those depended on by others)
        self.low_level_modules = set()  # Low-level modules (those depending on others)
        
    def match(self, 
              tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match this pattern against an AST.
        
        For Dependency Inversion, we analyze:
        1. Definition and usage of abstractions (interfaces, abstract classes)
        2. Dependency injection practices
        3. Factory pattern usage for implementation creation
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of component information dictionaries
        """
        logger.debug(f"DependencyInversionIntent.match called for {file_path}")
        
        if not file_path:
            logger.warning("No file_path provided, returning empty result")
            return []
            
        components = []
        
        # Handle mock implementation case
        if hasattr(tree, 'content'):
            # For mock implementation, code is in tree.content
            if isinstance(code, str) and not code.strip():
                code = tree.content
        
        # Analyze abstractions
        abstraction_metrics = self._analyze_abstractions(code, language)
        
        # Analyze dependency injection
        di_metrics = self._analyze_dependency_injection(code, language)
        
        # Analyze factory pattern usage
        factory_metrics = self._analyze_factory_patterns(code, language)
        
        # Calculate overall dependency inversion score
        dip_score = self._calculate_dip_score(
            abstraction_metrics, 
            di_metrics, 
            factory_metrics
        )
        
        # Create a component entry for this file
        component = {
            'type': 'component',
            'name': file_path,
            'path': file_path,
            'language': language,
            'dip_score': dip_score,
            'abstractions': abstraction_metrics,
            'dependency_injection': di_metrics,
            'factory_patterns': factory_metrics
        }
        
        components.append(component)
        logger.debug(f"Added dependency inversion component for {file_path}")
        
        return components
    
    def _analyze_abstractions(self, code: str, language: str) -> Dict:
        """Analyze abstraction usage in code.
        
        Args:
            code: The source code
            language: The language of the code
            
        Returns:
            Dictionary with abstraction metrics
        """
        metrics = {
            'defines_interface': False,
            'implements_interface': False,
            'interface_count': 0,
            'abstract_method_count': 0,
            'concrete_method_count': 0,
            'abstraction_ratio': 0.0,
            'depends_on_interfaces': False,
            'interface_dependency_count': 0,
        }
        
        # Skip if language not supported
        if language not in self.abstraction_indicators:
            return metrics
            
        indicators = self.abstraction_indicators[language]
        
        # Detect interface definitions
        for pattern in indicators.get('interfaces', []):
            matches = re.findall(pattern, code)
            if matches:
                metrics['defines_interface'] = True
                metrics['interface_count'] += len(matches)
        
        # Detect abstract methods
        for pattern in indicators.get('abstract_methods', []):
            matches = re.findall(pattern, code)
            metrics['abstract_method_count'] += len(matches)
        
        # Detect concrete method implementations
        if language == 'python':
            concrete_methods = re.findall(r'def\s+[a-zA-Z0-9_]+\s*\((?!.*@abstractmethod)', code)
            metrics['concrete_method_count'] = len(concrete_methods)
        elif language in ['javascript', 'typescript']:
            # Count methods that aren't abstract
            concrete_methods = re.findall(r'(?<!abstract\s+)[a-zA-Z0-9_]+\s*\([^)]*\)\s*{', code)
            metrics['concrete_method_count'] = len(concrete_methods)
        elif language == 'java':
            # Count non-abstract methods
            concrete_methods = re.findall(r'(?<!abstract\s+)[a-zA-Z0-9_<>]+\s+[a-zA-Z0-9_]+\s*\([^)]*\)\s*{', code)
            metrics['concrete_method_count'] = len(concrete_methods)
        
        # Detect interface implementations
        if language == 'python':
            # Check for classes that inherit from interfaces/abstract classes
            class_defs = re.findall(r'class\s+([A-Za-z0-9_]+)\s*\(\s*([A-Za-z0-9_,\s]+)\):', code)
            for class_name, bases in class_defs:
                base_classes = [b.strip() for b in bases.split(',')]
                if any(b.endswith(('Interface', 'Abstract', 'Base', 'ABC')) for b in base_classes):
                    metrics['implements_interface'] = True
                    break
        elif language in ['javascript', 'typescript']:
            # Check for classes that implement interfaces
            implements = re.findall(r'class\s+[A-Za-z0-9_]+\s+implements\s+[A-Za-z0-9_,\s]+', code)
            extends = re.findall(r'class\s+[A-Za-z0-9_]+\s+extends\s+[A-Za-z0-9_]+', code)
            if implements or extends:
                metrics['implements_interface'] = True
        elif language == 'java':
            # Check for classes that implement interfaces
            implements = re.findall(r'class\s+[A-Za-z0-9_]+\s+implements\s+[A-Za-z0-9_,\s<>]+', code)
            extends = re.findall(r'class\s+[A-Za-z0-9_]+\s+extends\s+[A-Za-z0-9_<>]+', code)
            if implements or extends:
                metrics['implements_interface'] = True
        
        # Detect dependencies on interfaces
        if language == 'python':
            # Look for type hints that reference interface-like types
            interface_refs = re.findall(r':\s*([A-Z][A-Za-z0-9_]*)', code)
            dependency_count = sum(1 for ref in interface_refs if any(marker in ref for marker in ['Interface', 'Abstract', 'Base', 'Protocol']))
            metrics['interface_dependency_count'] = dependency_count
            metrics['depends_on_interfaces'] = dependency_count > 0
        elif language in ['javascript', 'typescript']:
            # TypeScript interface references in parameters
            interface_refs = re.findall(r':\s*([A-Z][A-Za-z0-9_]*)', code)
            dependency_count = len(interface_refs)
            metrics['interface_dependency_count'] = dependency_count
            metrics['depends_on_interfaces'] = dependency_count > 0
        elif language == 'java':
            # Java interface references in parameters
            interface_refs = re.findall(r'([A-Z][A-Za-z0-9_]*)\s+[a-z][A-Za-z0-9_]*', code)
            dependency_count = sum(1 for ref in interface_refs if any(marker in ref for marker in ['Interface', 'Abstract', 'Service', 'Repository']))
            metrics['interface_dependency_count'] = dependency_count
            metrics['depends_on_interfaces'] = dependency_count > 0
        
        # Calculate abstraction ratio
        total_methods = metrics['abstract_method_count'] + metrics['concrete_method_count']
        if total_methods > 0:
            metrics['abstraction_ratio'] = metrics['abstract_method_count'] / total_methods
        
        return metrics
    
    def _analyze_dependency_injection(self, code: str, language: str) -> Dict:
        """Analyze dependency injection patterns in code.
        
        Args:
            code: The source code
            language: The language of the code
            
        Returns:
            Dictionary with dependency injection metrics
        """
        metrics = {
            'uses_di': False,
            'di_instance_count': 0,
            'constructor_injection': False,
            'setter_injection': False,
            'di_framework_usage': False,
            'di_annotations_count': 0,
        }
        
        # Skip if language not supported
        if language not in self.di_indicators:
            return metrics
            
        indicators = self.di_indicators[language]
        
        # Check each indicator
        for pattern in indicators:
            matches = re.findall(pattern, code)
            if matches:
                metrics['uses_di'] = True
                metrics['di_instance_count'] += len(matches)
                
                # Identify the injection method
                if 'constructor' in pattern or '__init__' in pattern:
                    metrics['constructor_injection'] = True
                if 'set' in pattern or 'property' in pattern:
                    metrics['setter_injection'] = True
                if '@' in pattern or 'inject(' in pattern:
                    metrics['di_framework_usage'] = True
                    metrics['di_annotations_count'] += len(matches)
        
        return metrics
    
    def _analyze_factory_patterns(self, code: str, language: str) -> Dict:
        """Analyze factory pattern usage in code.
        
        Args:
            code: The source code
            language: The language of the code
            
        Returns:
            Dictionary with factory pattern metrics
        """
        metrics = {
            'uses_factories': False,
            'factory_method_count': 0,
            'factory_class_count': 0,
            'instance_creation_points': 0,
        }
        
        # Skip if language not supported
        if language not in self.factory_indicators:
            return metrics
            
        indicators = self.factory_indicators[language]
        
        # Check each indicator
        for pattern in indicators:
            matches = re.findall(pattern, code)
            if matches:
                metrics['uses_factories'] = True
                
                # Classify the factory type
                if 'class' in pattern and 'Factory' in pattern:
                    metrics['factory_class_count'] += len(matches)
                elif 'create' in pattern or 'get' in pattern:
                    metrics['factory_method_count'] += len(matches)
                
                metrics['instance_creation_points'] += len(matches)
        
        return metrics
    
    def _calculate_dip_score(self, 
                           abstraction_metrics: Dict, 
                           di_metrics: Dict, 
                           factory_metrics: Dict) -> float:
        """Calculate overall dependency inversion principle score.
        
        Args:
            abstraction_metrics: Metrics related to abstractions
            di_metrics: Metrics related to dependency injection
            factory_metrics: Metrics related to factory patterns
            
        Returns:
            Overall DIP score (0.0-1.0)
        """
        # Weight factors
        weights = {
            'abstraction_usage': 0.5,
            'dependency_injection': 0.3,
            'factory_patterns': 0.2,
        }
        
        # Calculate abstraction score (0.0-1.0)
        abstraction_score = 0.0
        if abstraction_metrics.get('defines_interface', False):
            abstraction_score += 0.3
        if abstraction_metrics.get('implements_interface', False):
            abstraction_score += 0.3
        if abstraction_metrics.get('depends_on_interfaces', False):
            abstraction_score += 0.3
        if abstraction_metrics.get('abstraction_ratio', 0.0) > 0:
            abstraction_score += 0.1 * abstraction_metrics['abstraction_ratio']
        abstraction_score = min(1.0, abstraction_score)  # Cap at 1.0
        
        # Calculate dependency injection score (0.0-1.0)
        di_score = 0.0
        if di_metrics.get('uses_di', False):
            di_score += 0.5
        if di_metrics.get('constructor_injection', False):
            di_score += 0.2
        if di_metrics.get('di_framework_usage', False):
            di_score += 0.3
        di_score = min(1.0, di_score)  # Cap at 1.0
        
        # Calculate factory pattern score (0.0-1.0)
        factory_score = 0.0
        if factory_metrics.get('uses_factories', False):
            factory_score += 0.5
        factory_score += 0.5 * min(1.0, factory_metrics.get('instance_creation_points', 0) / 5.0)
        factory_score = min(1.0, factory_score)  # Cap at 1.0
        
        # Calculate weighted average
        overall_score = (
            weights['abstraction_usage'] * abstraction_score +
            weights['dependency_injection'] * di_score +
            weights['factory_patterns'] * factory_score
        )
        
        return overall_score
        
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Dependency Inversion, we are tracking:
        1. Interface definitions and implementations
        2. Dependency injection usage
        3. High-level vs low-level components
        
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
                    dip_score=match.get('dip_score', 0.0),
                    defines_interface=match.get('abstractions', {}).get('defines_interface', False),
                    implements_interface=match.get('abstractions', {}).get('implements_interface', False),
                    uses_di=match.get('dependency_injection', {}).get('uses_di', False),
                    uses_factories=match.get('factory_patterns', {}).get('uses_factories', False),
                )
                
                # Track component scores
                self.abstraction_scores[component_name] = 1.0 if match.get('abstractions', {}).get('defines_interface', False) else 0.0
                self.di_scores[component_name] = 1.0 if match.get('dependency_injection', {}).get('uses_di', False) else 0.0
                self.factory_scores[component_name] = 1.0 if match.get('factory_patterns', {}).get('uses_factories', False) else 0.0
                
                # Track interfaces and implementations
                if match.get('abstractions', {}).get('defines_interface', False):
                    # This is a potential interface
                    self.high_level_modules.add(component_name)
                
                if match.get('abstractions', {}).get('implements_interface', False):
                    # This is a potential implementation
                    self.low_level_modules.add(component_name)
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Dependency Inversion architectural intent.
        
        We analyze:
        1. Overall DIP scores
        2. Interface-implementation relationships
        3. Layer inversion (high-level modules depending on abstractions)
        
        Returns:
            A dictionary containing the dependency inversion intent details
        """
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Calculate average DIP score
        dip_scores = [
            self.component_graph.nodes[node].get('dip_score', 0.0)
            for node in self.component_graph.nodes
        ]
        avg_dip = sum(dip_scores) / len(dip_scores) if dip_scores else 0.0
        
        # Count interface definitions and implementations
        interface_definitions = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('defines_interface', False)
        )
        interface_implementations = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('implements_interface', False)
        )
        
        # Count dependency injection usage
        di_components = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('uses_di', False)
        )
        
        # Count factory pattern usage
        factory_components = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('uses_factories', False)
        )
        
        # Calculate inversion metrics
        # In a perfect DIP system, high-level modules should only depend on abstractions
        inversion_ratio = 0.0
        total_components = len(self.component_graph.nodes)
        if total_components > 0:
            # Proportion of components showing dependency inversion
            inversion_components = len(self.high_level_modules.intersection(self.low_level_modules))
            inversion_ratio = (interface_definitions + interface_implementations + di_components) / (3 * total_components)
        
        # Calculate abstraction metrics
        abstraction_scores = list(self.abstraction_scores.values())
        avg_abstraction = sum(abstraction_scores) / len(abstraction_scores) if abstraction_scores else 0.0
        
        # Calculate DI metrics
        di_scores = list(self.di_scores.values())
        avg_di = sum(di_scores) / len(di_scores) if di_scores else 0.0
        
        # Calculate factory metrics
        factory_scores = list(self.factory_scores.values())
        avg_factory = sum(factory_scores) / len(factory_scores) if factory_scores else 0.0
        
        # Calculate overall confidence score
        # Weighted average of various factors
        confidence = (
            0.4 * avg_dip +  # Overall DIP score
            0.3 * inversion_ratio +  # Components showing dependency inversion
            0.2 * avg_abstraction +  # Abstraction usage
            0.1 * (avg_di + avg_factory) / 2.0  # DI and factory usage
        )
        
        # Create metrics dictionary
        metrics = {
            "avg_dip_score": avg_dip,
            "interface_definitions": interface_definitions,
            "interface_implementations": interface_implementations,
            "inversion_ratio": inversion_ratio,
            "dependency_injection_usage": di_components,
            "factory_pattern_usage": factory_components,
            "avg_abstraction_score": avg_abstraction,
            "avg_di_score": avg_di,
            "avg_factory_score": avg_factory
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
        """Generate a human-readable description of the dependency inversion findings.
        
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
        desc = f"The codebase shows {confidence_desc} evidence of the Dependency Inversion Principle. "
        
        # Add abstraction details
        interface_defs = metrics["interface_definitions"]
        interface_impls = metrics["interface_implementations"]
        if interface_defs > 0 and interface_impls > 0:
            desc += f"There are {interface_defs} interface/abstraction definitions and {interface_impls} implementations, showing good separation of abstractions from details. "
        elif interface_defs > 0:
            desc += f"There are {interface_defs} interface/abstraction definitions but limited implementations, showing partial adoption of the principle. "
        else:
            desc += "There are few formal abstractions defined, limiting the application of dependency inversion. "
        
        # Add dependency injection details
        di_usage = metrics["dependency_injection_usage"]
        if di_usage > 0:
            di_ratio = di_usage / component_count
            if di_ratio > 0.5:
                desc += "Dependency injection is widely used throughout the codebase, facilitating loose coupling. "
            else:
                desc += "Dependency injection is used in some parts of the codebase, but could be more consistently applied. "
        else:
            desc += "Dependency injection is not prominently used, which may lead to tighter coupling between components. "
        
        # Add factory pattern details
        factory_usage = metrics["factory_pattern_usage"]
        if factory_usage > 0:
            desc += "Factory patterns are used to create concrete implementations, further supporting dependency inversion."
        else:
            desc += "Factory patterns are minimally used, which could limit flexibility in implementation selection."
        
        return desc
    
    def _generate_recommendations(self, metrics: Dict, confidence: float) -> List[str]:
        """Generate recommendations for improving dependency inversion.
        
        Args:
            metrics: The calculated metrics
            confidence: Overall confidence score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Only generate recommendations if score is below excellent
        if confidence < 0.8:
            # Abstraction recommendations
            if metrics["interface_definitions"] == 0:
                recommendations.append(
                    "Define interfaces or abstract classes for key components to enable dependency inversion"
                )
            elif metrics["interface_implementations"] < metrics["interface_definitions"]:
                recommendations.append(
                    "Implement existing interfaces throughout the codebase to improve abstraction consistency"
                )
            
            # Dependency injection recommendations
            if metrics["dependency_injection_usage"] == 0:
                recommendations.append(
                    "Introduce dependency injection to reduce direct dependencies on concrete implementations"
                )
            elif metrics["avg_di_score"] < 0.5:
                recommendations.append(
                    "Expand dependency injection usage to more components to improve overall system flexibility"
                )
            
            # Factory pattern recommendations
            if metrics["factory_pattern_usage"] == 0:
                recommendations.append(
                    "Implement factory patterns to centralize and control the creation of concrete implementations"
                )
            
            # General DIP recommendations
            if metrics["inversion_ratio"] < 0.5:
                recommendations.append(
                    "Ensure high-level modules depend on abstractions rather than concrete implementations"
                )
        
        return recommendations