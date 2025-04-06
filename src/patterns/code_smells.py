"""
Patterns for detecting code smells and quality issues.
"""

from typing import Dict, List, Optional, Set, Union
from pathlib import Path
import logging

import tree_sitter

from ..pattern_base import QueryBasedPattern, CompositePattern, Pattern


class LongMethodPattern(Pattern):
    """Pattern for detecting methods that are too long."""
    
    def __init__(self, max_lines: int = 50):
        """Initialize a pattern for detecting long methods.
        
        Args:
            max_lines: Maximum acceptable number of lines for a method
        """
        super().__init__(
            name="long_method",
            description=f"Identifies methods with more than {max_lines} lines",
        )
        self.max_lines = max_lines
    
    def match(self, 
              tree: tree_sitter.Tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match long methods in the AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of matches, where each match is a dictionary with details
        """
        # First, find all methods in the code
        from ..pattern_recognizer import PatternRecognizer
        recognizer = PatternRecognizer()
        
        # Get all method patterns
        from .function_patterns import FunctionDefinitionPattern, MethodDefinitionPattern
        function_pattern = FunctionDefinitionPattern()
        method_pattern = MethodDefinitionPattern()
        
        # Match all functions and methods
        functions = function_pattern.match(tree, code, language, file_path)
        methods = method_pattern.match(tree, code, language, file_path)
        
        # Combine the results
        all_methods = functions + methods
        
        # Check each method for length
        matches = []
        
        for method in all_methods:
            if 'body' in method:
                # Get the body text
                body_text = method['body']['text']
                
                # Count lines
                lines = body_text.split('\n')
                line_count = len(lines)
                
                if line_count > self.max_lines:
                    match = {
                        'type': 'code_smell',
                        'smell': 'long_method',
                        'name': method['name'],
                        'line': method['line'],
                        'column': method['column'],
                        'language': language,
                        'line_count': line_count,
                        'max_lines': self.max_lines,
                    }
                    
                    if 'type' in method:
                        match['method_type'] = method['type']
                    
                    if file_path:
                        match['file'] = file_path
                        
                    matches.append(match)
        
        return matches


class DeepNestingPattern(QueryBasedPattern):
    """Pattern for detecting deeply nested code structures."""
    
    def __init__(self, max_depth: int = 3):
        """Initialize a pattern for detecting deep nesting.
        
        Args:
            max_depth: Maximum acceptable nesting depth
        """
        super().__init__(
            name="deep_nesting",
            description=f"Identifies code with nesting deeper than {max_depth} levels",
            languages=["python", "javascript", "typescript", "java", "c", "cpp"],
        )
        self.max_depth = max_depth
        
        # Define language-specific queries
        self.queries = {
            'python': """
                ; Capture all if statements with nested if statements
                (if_statement
                  consequence: (block
                    (if_statement) @nested_if))
                
                ; Capture all for loops with nested for loops
                (for_statement
                  body: (block
                    (for_statement) @nested_for))
                
                ; Capture all while loops with nested while loops
                (while_statement
                  body: (block
                    (while_statement) @nested_while))
            """,
            'javascript': """
                ; Capture all if statements with nested if statements
                (if_statement
                  consequence: (statement_block
                    (if_statement) @nested_if))
                
                ; Capture all for loops with nested for loops
                (for_statement
                  body: (statement_block
                    (for_statement) @nested_for))
                
                ; Capture all while loops with nested while loops
                (while_statement
                  body: (statement_block
                    (while_statement) @nested_while))
            """,
            'typescript': """
                ; Capture all if statements with nested if statements
                (if_statement
                  consequence: (statement_block
                    (if_statement) @nested_if))
                
                ; Capture all for loops with nested for loops
                (for_statement
                  body: (statement_block
                    (for_statement) @nested_for))
                
                ; Capture all while loops with nested while loops
                (while_statement
                  body: (statement_block
                    (while_statement) @nested_while))
            """,
            'java': """
                ; Capture all if statements with nested if statements
                (if_statement
                  consequence: (block
                    (if_statement) @nested_if))
                
                ; Capture all for loops with nested for loops
                (for_statement
                  body: (block
                    (for_statement) @nested_for))
                
                ; Capture all while loops with nested while loops
                (while_statement
                  body: (block
                    (while_statement) @nested_while))
            """,
            'c': """
                ; Capture all if statements with nested if statements
                (if_statement
                  consequence: (compound_statement
                    (if_statement) @nested_if))
                
                ; Capture all for loops with nested for loops
                (for_statement
                  body: (compound_statement
                    (for_statement) @nested_for))
                
                ; Capture all while loops with nested while loops
                (while_statement
                  body: (compound_statement
                    (while_statement) @nested_while))
            """,
            'cpp': """
                ; Capture all if statements with nested if statements
                (if_statement
                  consequence: (compound_statement
                    (if_statement) @nested_if))
                
                ; Capture all for loops with nested for loops
                (for_statement
                  body: (compound_statement
                    (for_statement) @nested_for))
                
                ; Capture all while loops with nested while loops
                (while_statement
                  body: (compound_statement
                    (while_statement) @nested_while))
            """,
        }
    
    def _calculate_nesting_depth(self, node) -> int:
        """Calculate the maximum nesting depth of a node.
        
        Args:
            node: A tree-sitter node
            
        Returns:
            The maximum nesting depth
        """
        # Base case: if the node has no children, return 1
        if not hasattr(node, 'children') or not node.children:
            return 1
            
        # Recursive case: return 1 + the maximum depth of any child
        max_child_depth = 0
        for child in node.children:
            child_depth = self._calculate_nesting_depth(child)
            max_child_depth = max(max_child_depth, child_depth)
            
        return 1 + max_child_depth
    
    def match(self, 
              tree: tree_sitter.Tree, 
              code: str, 
              language: str,
              file_path: Optional[str] = None) -> List[Dict]:
        """Match deeply nested code in the AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            
        Returns:
            A list of matches, where each match is a dictionary with details
        """
        if not self.supports_language(language):
            return []
            
        # Run the nested structure query
        matches = []
        
        # First, use the query to find all nested structures
        query_string = self.get_query_string(language)
        if not query_string:
            return []
            
        from ..parser import CodeParser
        parser = CodeParser()
        query_results = parser.query(tree, query_string, language)
        
        # Process the query results to find deep nesting
        for result in query_results:
            capture = result['capture']
            node = result['node']
            
            # Calculate the nesting depth
            depth = self._calculate_nesting_depth(node)
            
            if depth > self.max_depth:
                match = {
                    'type': 'code_smell',
                    'smell': 'deep_nesting',
                    'nesting_type': capture.replace('nested_', ''),
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1],
                    'end_line': node.end_point[0] + 1,
                    'end_column': node.end_point[1],
                    'language': language,
                    'depth': depth,
                    'max_depth': self.max_depth,
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class ComplexConditionPattern(QueryBasedPattern):
    """Pattern for detecting complex conditional expressions."""
    
    def __init__(self, max_operators: int = 3):
        """Initialize a pattern for detecting complex conditions.
        
        Args:
            max_operators: Maximum acceptable number of operators in a condition
        """
        super().__init__(
            name="complex_condition",
            description=f"Identifies conditions with more than {max_operators} logical operators",
            languages=["python", "javascript", "typescript", "java", "c", "cpp"],
        )
        self.max_operators = max_operators
        
        # Define language-specific queries
        self.queries = {
            'python': """
                ; Capture all binary expressions in if statements
                (if_statement
                  condition: (binary_operator) @condition)
                
                ; Capture all binary expressions in while statements
                (while_statement
                  condition: (binary_operator) @condition)
            """,
            'javascript': """
                ; Capture all binary expressions in if statements
                (if_statement
                  condition: (binary_expression) @condition)
                
                ; Capture all binary expressions in while statements
                (while_statement
                  condition: (binary_expression) @condition)
            """,
            'typescript': """
                ; Capture all binary expressions in if statements
                (if_statement
                  condition: (binary_expression) @condition)
                
                ; Capture all binary expressions in while statements
                (while_statement
                  condition: (binary_expression) @condition)
            """,
            'java': """
                ; Capture all binary expressions in if statements
                (if_statement
                  condition: (binary_expression) @condition)
                
                ; Capture all binary expressions in while statements
                (while_statement
                  condition: (binary_expression) @condition)
            """,
            'c': """
                ; Capture all binary expressions in if statements
                (if_statement
                  condition: (binary_expression) @condition)
                
                ; Capture all binary expressions in while statements
                (while_statement
                  condition: (binary_expression) @condition)
            """,
            'cpp': """
                ; Capture all binary expressions in if statements
                (if_statement
                  condition: (binary_expression) @condition)
                
                ; Capture all binary expressions in while statements
                (while_statement
                  condition: (binary_expression) @condition)
            """,
        }
    
    def _count_operators(self, node) -> int:
        """Count the number of operators in a binary expression.
        
        Args:
            node: A tree-sitter node
            
        Returns:
            The number of operators
        """
        # Base case: if the node is not a binary expression, return 0
        if not hasattr(node, 'type') or 'binary' not in node.type:
            return 0
            
        # Count this operator
        count = 1
        
        # Count operators in children
        if hasattr(node, 'children'):
            for child in node.children:
                count += self._count_operators(child)
                
        return count
    
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for complex conditions.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of complex condition matches with details
        """
        matches = []
        
        for result in query_results:
            node = result['node']
            
            # Count operators in the condition
            operator_count = self._count_operators(node)
            
            if operator_count > self.max_operators:
                match = {
                    'type': 'code_smell',
                    'smell': 'complex_condition',
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1],
                    'end_line': node.end_point[0] + 1,
                    'end_column': node.end_point[1],
                    'language': language,
                    'operator_count': operator_count,
                    'max_operators': self.max_operators,
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class CodeSmellsPattern(CompositePattern):
    """A composite pattern that matches all supported code smell patterns."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting code smells."""
        super().__init__(
            name="code_smells",
            description="Identifies all supported code smell patterns",
            patterns=[
                LongMethodPattern(),
                DeepNestingPattern(),
                ComplexConditionPattern(),
            ],
        )