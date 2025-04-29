"""
Cognitive Complexity metric implementation.

This module provides the implementation of SonarSource's Cognitive Complexity metric,
which measures the difficulty of understanding code by considering factors like
nesting, control flow complexity, and structural complexity.
"""

from typing import Dict, List, Optional, Any, Union, Set
import logging
import re

import tree_sitter

from .metric_base import ComplexityMetric

logger = logging.getLogger(__name__)

class CognitiveComplexityMetric(ComplexityMetric):
    """Cognitive Complexity metric implementation.
    
    Calculates SonarSource's Cognitive Complexity, which measures the difficulty in
    understanding code by accounting for:
    1. Nesting - incrementing with each level of nesting
    2. Structural complexity - counted once per structure
    3. Cognitive cost of sequences, interrupts, and continuations
    
    Unlike Cyclomatic Complexity, Cognitive Complexity penalizes deeply nested structures
    more heavily, reflecting the increased mental effort needed to understand them.
    """
    
    def __init__(self):
        """Initialize the Cognitive Complexity metric."""
        super().__init__(
            name="cognitive_complexity",
            description="SonarSource's Cognitive Complexity - measures the difficulty of understanding code"
        )
        
        # Language-specific configuration for control flow statements
        self.language_config = {
            "python": {
                "queries": {
                    "functions": """
                        (function_definition
                            name: (identifier) @function_name
                            body: (block) @function_body) @function
                        
                        (class_definition
                            name: (identifier) @class_name
                            body: (block
                                (function_definition
                                    name: (identifier) @method_name
                                    body: (block) @method_body) @method)) @class
                    """,
                    # We need to capture nesting as well for cognitive complexity
                    "structures": """
                        (if_statement) @if
                        (elif_clause) @elif
                        (else_clause) @else
                        (for_statement) @for
                        (while_statement) @while
                        (try_statement) @try
                        (except_clause) @except
                        (boolean_operator) @boolean_op
                        (conditional_expression) @conditional
                        (lambda) @lambda
                        (comprehension) @comprehension
                    """
                }
            },
            "javascript": {
                "queries": {
                    "functions": """
                        (function_declaration
                            name: (identifier) @function_name
                            body: (statement_block) @function_body) @function
                        
                        (method_definition
                            name: (property_identifier) @method_name
                            body: (statement_block) @method_body) @method
                        
                        (arrow_function
                            body: [(statement_block) @arrow_body, (expression) @arrow_expr]) @arrow
                    """,
                    "structures": """
                        (if_statement) @if
                        (else_clause) @else
                        (for_statement) @for
                        (for_in_statement) @for_in
                        (while_statement) @while
                        (do_statement) @do
                        (switch_statement) @switch
                        (case_statement) @case
                        (try_statement) @try
                        (catch_clause) @catch
                        (binary_expression
                            operator: ["&&", "||"]) @boolean_expr
                        (ternary_expression) @ternary
                    """
                }
            },
            # Add more languages as needed
        }
        
        # Default rules for languages not specifically configured
        self.default_structure_patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b', r'\bcase\b', 
            r'\bcatch\b', r'\btry\b', r'\band\b', r'\bor\b', r'\b\?\b', r'\?.*:',
            r'\blambda\b'
        ]
        
        # Complexity level thresholds - cognitive complexity has different thresholds than cyclomatic
        self.complexity_thresholds = {
            "low": 15,        # 1-15 is considered low complexity
            "moderate": 30,   # 16-30 is considered moderate complexity
            "high": 50,       # 31-50 is considered high complexity
            # > 50 is considered very high complexity
        }
    
    def compute(self, 
               tree: tree_sitter.Tree, 
               code: str, 
               language: str,
               file_path: Optional[str] = None) -> Dict[str, Any]:
        """Compute the Cognitive Complexity for a given AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary containing the computed metric values
        """
        if not self.supports_language(language):
            logger.warning(f"Cognitive Complexity metric does not support language: {language}")
            return {
                "metric": self.name,
                "value": None,
                "language": language,
                "file_path": file_path,
                "functions": [],
                "overall_complexity_level": "unknown",
                "description": f"Language {language} not supported"
            }
        
        # Use tree-sitter queries if available for this language
        if language in self.language_config:
            return self._compute_with_queries(tree, code, language, file_path)
        else:
            # Fallback to simplified calculation using regex
            return self._compute_with_regex(code, language, file_path)
    
    def _compute_with_queries(self, 
                            tree: tree_sitter.Tree, 
                            code: str, 
                            language: str,
                            file_path: Optional[str] = None) -> Dict[str, Any]:
        """Compute complexity using tree-sitter queries.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary containing the computed metric values
        """
        # Get the queries for this language
        lang_config = self.language_config[language]
        functions_query = lang_config["queries"]["functions"]
        structures_query = lang_config["queries"]["structures"]
        
        # Run the queries
        try:
            from tree_sitter import Query, Language, Parser
            
            # Get the language module
            from src.tree_sitter_manager import LanguageManager
            manager = LanguageManager()
            lang_module = manager.get_language(language)
            
            # Query for functions/methods
            function_query = Query(lang_module, functions_query)
            function_matches = function_query.captures(tree.root_node)
            
            # Extract functions and methods
            functions = []
            function_nodes = {}
            
            for match, tag in function_matches:
                if tag in ['function', 'method', 'arrow']:
                    function_nodes[match.id] = match
            
            for node_id, node in function_nodes.items():
                # Get function name
                name = "anonymous"
                for match, tag in function_matches:
                    if tag in ['function_name', 'method_name'] and match.parent.id == node_id:
                        name = code[match.start_byte:match.end_byte]
                        break
                
                # Get function body
                body = None
                for match, tag in function_matches:
                    if tag in ['function_body', 'method_body', 'arrow_body', 'arrow_expr'] and match.parent.id == node_id:
                        body = match
                        break
                
                if body:
                    # Compute cognitive complexity for this function
                    complexity, details = self._compute_node_complexity(body, lang_module, structures_query, code)
                    
                    # Function info
                    function_info = {
                        "name": name,
                        "complexity": complexity,
                        "complexity_level": self.get_complexity_level(complexity),
                        "line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "nesting_increment": details.get("nesting_increment", 0),
                        "structural_increment": details.get("structural_increment", 0),
                        "boolean_increment": details.get("boolean_increment", 0),
                        "recommendations": self.get_recommendations(complexity)
                    }
                    
                    functions.append(function_info)
            
            # Sort functions by complexity (highest first)
            functions.sort(key=lambda f: f["complexity"], reverse=True)
            
            # Calculate overall complexity (max of all functions)
            overall_complexity = max([f["complexity"] for f in functions]) if functions else 0
            overall_level = self.get_complexity_level(overall_complexity)
            
            return {
                "metric": self.name,
                "value": overall_complexity,
                "language": language,
                "file_path": file_path,
                "functions": functions,
                "overall_complexity_level": overall_level,
                "recommendations": self.get_recommendations(overall_complexity)
            }
        
        except Exception as e:
            logger.error(f"Error computing cognitive complexity with queries: {e}")
            # Fallback to regex-based calculation
            return self._compute_with_regex(code, language, file_path)
    
    def _compute_node_complexity(self, 
                               node: tree_sitter.Node,
                               lang_module,
                               structures_query: str,
                               code: str) -> tuple:
        """Compute cognitive complexity for a single node (function body).
        
        Args:
            node: The node to compute complexity for
            lang_module: The tree-sitter language module
            structures_query: Query for control flow structures
            code: The source code
            
        Returns:
            Tuple of (complexity value, details dictionary)
        """
        # Run the structures query
        query = Query(lang_module, structures_query)
        matches = query.captures(node)
        
        complexity = 0
        nesting_level = 0
        nesting_increment = 0
        structural_increment = 0
        boolean_increment = 0
        
        # Process each control flow structure
        for match, tag in matches:
            # Increment for the structure itself (except for else/elif which are part of if)
            if tag not in ['else', 'elif', 'else_clause']:
                complexity += 1
                structural_increment += 1
            
            # Additional increment for nesting level
            if tag in ['if', 'for', 'while', 'try', 'switch', 'do']:
                # Increase nesting level for nested structures
                # This is simplified - in a real implementation we'd track the exact nesting
                # by examining the AST hierarchy more carefully
                nesting_level += 1
                complexity += nesting_level
                nesting_increment += nesting_level
                
                # Decrease nesting level after processing children
                nesting_level -= 1
            
            # Boolean operators add complexity
            if tag in ['boolean_op', 'boolean_expr']:
                complexity += 1
                boolean_increment += 1
        
        details = {
            "nesting_increment": nesting_increment,
            "structural_increment": structural_increment,
            "boolean_increment": boolean_increment
        }
        
        return complexity, details
    
    def _compute_with_regex(self, 
                          code: str, 
                          language: str,
                          file_path: Optional[str] = None) -> Dict[str, Any]:
        """Compute complexity using regex pattern matching.
        
        This is a fallback method when tree-sitter queries are not available.
        
        Args:
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary containing the computed metric values
        """
        # Split code into lines
        lines = code.split('\n')
        
        # Count control flow structures using regex
        structure_count = 0
        for line in lines:
            for pattern in self.default_structure_patterns:
                if re.search(pattern, line):
                    structure_count += 1
                    break
        
        # This is a very simplified calculation that doesn't account for nesting
        # but provides a baseline estimate
        complexity = structure_count
        complexity_level = self.get_complexity_level(complexity)
        
        return {
            "metric": self.name,
            "value": complexity,
            "language": language,
            "file_path": file_path,
            "overall_complexity_level": complexity_level,
            "description": "Calculated using regex pattern matching (highly simplified)",
            "recommendations": self.get_recommendations(complexity)
        }
    
    def get_complexity_level(self, value: Union[int, float]) -> str:
        """Get the complexity level for a given Cognitive Complexity value.
        
        Args:
            value: The computed Cognitive Complexity value
            
        Returns:
            A string indicating the complexity level ('low', 'moderate', 'high', 'very_high')
        """
        if value <= self.complexity_thresholds["low"]:
            return "low"
        elif value <= self.complexity_thresholds["moderate"]:
            return "moderate"
        elif value <= self.complexity_thresholds["high"]:
            return "high"
        else:
            return "very_high"
    
    def get_recommendations(self, value: Union[int, float]) -> List[str]:
        """Get recommendations for improving code with this complexity level.
        
        Args:
            value: The computed Cognitive Complexity value
            
        Returns:
            A list of recommendations for improving the code
        """
        if value <= self.complexity_thresholds["low"]:
            # Low complexity - no specific recommendations needed
            return []
        
        recommendations = []
        
        if value <= self.complexity_thresholds["moderate"]:
            # Moderate complexity
            recommendations = [
                "Reduce nesting by extracting nested blocks into named methods",
                "Use guard clauses to return early and reduce nesting",
                "Simplify boolean expressions by extracting them to named variables"
            ]
        elif value <= self.complexity_thresholds["high"]:
            # High complexity
            recommendations = [
                "Break down the function into smaller, focused methods with clear names",
                "Reduce nesting levels by using early returns and guard clauses",
                "Replace nested conditionals with a lookup table or strategy pattern",
                "Move repeated or complex logic to helper methods",
                "Simplify complicated boolean expressions"
            ]
        else:
            # Very high complexity
            recommendations = [
                "This function is extremely difficult to understand and maintain - refactor urgently",
                "Split into multiple smaller functions with single responsibilities",
                "Consider redesigning this logic using the State or Strategy patterns",
                "Replace conditional logic with polymorphism where appropriate",
                "Use descriptive variable names to clarify complex conditions",
                "Add comprehensive tests before refactoring to ensure behavior is preserved"
            ]
        
        return recommendations
    
    def supports_language(self, language: str) -> bool:
        """Check if this metric supports a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            True if the metric supports the language, False otherwise
        """
        # Languages specifically supported with queries
        if language in self.language_config:
            return True
        
        # For other languages, we can use the simplified regex approach
        return True