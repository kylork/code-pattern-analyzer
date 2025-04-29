"""
Cyclomatic Complexity metric implementation.

This module provides the implementation of McCabe's Cyclomatic Complexity metric,
which measures the number of linearly independent paths through a program's source code.
"""

from typing import Dict, List, Optional, Any, Union, Set
import logging
import re

import tree_sitter

from .metric_base import ComplexityMetric

logger = logging.getLogger(__name__)

class CyclomaticComplexityMetric(ComplexityMetric):
    """Cyclomatic Complexity metric implementation.
    
    Calculates McCabe's Cyclomatic Complexity, which is defined as:
    CC = E - N + 2P
    where:
    - E is the number of edges in the control flow graph
    - N is the number of nodes in the control flow graph
    - P is the number of connected components (usually 1 for a function)
    
    In practice, this is computed by counting the number of decision points (branches)
    in the code and adding 1 for the entry point.
    """
    
    def __init__(self):
        """Initialize the Cyclomatic Complexity metric."""
        super().__init__(
            name="cyclomatic_complexity",
            description="McCabe's Cyclomatic Complexity - measures the number of linearly independent paths through code"
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
                    "branches": """
                        (if_statement) @if
                        (elif_clause) @elif
                        (else_clause) @else
                        (for_statement) @for
                        (while_statement) @while
                        (try_statement) @try
                        (except_clause) @except
                        (boolean_operator) @boolean_op
                        (conditional_expression) @conditional
                    """
                },
                "boolean_operators": ["and", "or"]
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
                    "branches": """
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
                },
                "boolean_operators": ["&&", "||"]
            },
            # Add more languages as needed
        }
        
        # Default rules for languages not specifically configured
        self.default_branch_patterns = [
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b', r'\bcase\b', 
            r'\bcatch\b', r'\btry\b', r'\band\b', r'\bor\b', r'\b\?\b', r'\?.*:',
        ]
        
        # Complexity level thresholds
        self.complexity_thresholds = {
            "low": 10,        # 1-10 is considered low complexity
            "moderate": 20,   # 11-20 is considered moderate complexity
            "high": 30,       # 21-30 is considered high complexity
            # > 30 is considered very high complexity
        }
    
    def compute(self, 
               tree: tree_sitter.Tree, 
               code: str, 
               language: str,
               file_path: Optional[str] = None) -> Dict[str, Any]:
        """Compute the Cyclomatic Complexity for a given AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A dictionary containing the computed metric values
        """
        if not self.supports_language(language):
            logger.warning(f"Cyclomatic Complexity metric does not support language: {language}")
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
        branches_query = lang_config["queries"]["branches"]
        
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
                    # Run the branches query on the function body
                    branch_query = Query(lang_module, branches_query)
                    branch_matches = branch_query.captures(body)
                    
                    # Count branches
                    branches = set()
                    boolean_op_count = 0
                    
                    for match, tag in branch_matches:
                        if tag in ['if', 'for', 'while', 'try', 'switch', 'do']:
                            branches.add(match.id)
                        elif tag in ['elif', 'else', 'except', 'catch', 'case']:
                            branches.add(match.id)
                        elif tag in ['boolean_op', 'boolean_expr']:
                            # Count boolean operators (and, or, &&, ||)
                            boolean_op_count += 1
                        elif tag in ['conditional', 'ternary']:
                            branches.add(match.id)
                    
                    # Calculate cyclomatic complexity
                    complexity = 1 + len(branches) + boolean_op_count
                    
                    # Function info
                    function_info = {
                        "name": name,
                        "complexity": complexity,
                        "complexity_level": self.get_complexity_level(complexity),
                        "line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                        "branches": len(branches),
                        "boolean_operators": boolean_op_count,
                        "recommendations": self.get_recommendations(complexity)
                    }
                    
                    functions.append(function_info)
            
            # Sort functions by complexity (highest first)
            functions.sort(key=lambda f: f["complexity"], reverse=True)
            
            # Calculate overall complexity (max of all functions)
            overall_complexity = max([f["complexity"] for f in functions]) if functions else 1
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
            logger.error(f"Error computing cyclomatic complexity with queries: {e}")
            # Fallback to regex-based calculation
            return self._compute_with_regex(code, language, file_path)
    
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
        
        # Count branch statements using regex
        branch_count = 0
        for line in lines:
            for pattern in self.default_branch_patterns:
                if re.search(pattern, line):
                    branch_count += 1
                    break
        
        # Calculate complexity
        complexity = 1 + branch_count
        complexity_level = self.get_complexity_level(complexity)
        
        return {
            "metric": self.name,
            "value": complexity,
            "language": language,
            "file_path": file_path,
            "overall_complexity_level": complexity_level,
            "description": "Calculated using regex pattern matching (simplified)",
            "recommendations": self.get_recommendations(complexity)
        }
    
    def get_complexity_level(self, value: Union[int, float]) -> str:
        """Get the complexity level for a given Cyclomatic Complexity value.
        
        Args:
            value: The computed Cyclomatic Complexity value
            
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
            value: The computed Cyclomatic Complexity value
            
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
                "Consider breaking down complex conditional logic into separate helper methods",
                "Use early returns to reduce nesting levels"
            ]
        elif value <= self.complexity_thresholds["high"]:
            # High complexity
            recommendations = [
                "Extract blocks of code into smaller, focused methods",
                "Simplify complex conditional expressions with clear variable names",
                "Consider using the Strategy pattern to handle conditional behavior",
                "Use polymorphism instead of complex type-checking conditionals"
            ]
        else:
            # Very high complexity
            recommendations = [
                "Refactor this method urgently - it's too complex to maintain safely",
                "Break down into multiple smaller methods or classes with single responsibilities",
                "Replace conditional logic with polymorphism or the Strategy pattern",
                "Consider a state machine approach for complex state transitions",
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