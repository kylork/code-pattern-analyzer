"""
Patterns for detecting functions and methods.
"""

from typing import Dict, List, Optional, Union

import tree_sitter

from ..pattern_base import QueryBasedPattern, CompositePattern


class FunctionDefinitionPattern(QueryBasedPattern):
    """Pattern for detecting function definitions."""
    
    def __init__(self):
        """Initialize a pattern for detecting function definitions."""
        super().__init__(
            name="function_definition",
            description="Identifies function definitions in code",
            languages=["python", "javascript", "typescript", "ruby", "go", "java", "c", "cpp", "rust"],
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                (function_definition
                  name: (identifier) @name
                  parameters: (parameters) @params
                  body: (block) @body)
            """,
            'javascript': """
                (function_declaration
                  name: (identifier) @name
                  parameters: (formal_parameters) @params
                  body: (statement_block) @body)
            """,
            'typescript': """
                (function_declaration
                  name: (identifier) @name
                  parameters: (formal_parameters) @params
                  body: (statement_block) @body)
            """,
            'ruby': """
                (method
                  name: (identifier) @name
                  parameters: (method_parameters) @params
                  body: (body_statement) @body)
            """,
            'go': """
                (function_declaration
                  name: (identifier) @name
                  parameters: (parameter_list) @params
                  body: (block) @body)
            """,
            'java': """
                (method_declaration
                  name: (identifier) @name
                  parameters: (formal_parameters) @params
                  body: (block) @body)
            """,
            'c': """
                (function_definition
                  declarator: (function_declarator
                    declarator: (identifier) @name)
                  body: (compound_statement) @body)
            """,
            'cpp': """
                (function_definition
                  declarator: (function_declarator
                    declarator: (identifier) @name)
                  body: (compound_statement) @body)
            """,
            'rust': """
                (function_item
                  name: (identifier) @name
                  parameters: (parameters) @params
                  body: (block) @body)
            """,
        }
        
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results for function definitions.
        
        This extracts additional information about functions like parameter names.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of function matches with details
        """
        # Use the generic implementation as a starting point
        matches = super()._process_query_results(query_results, code, language, file_path, parser)
        
        # Extract additional information
        for match in matches:
            # Set the match type specifically
            match['type'] = 'function'
            
            # Extract parameter information if available
            if 'params' in match:
                params_node = match['params']['text']
                # Simple parameter extraction - in a real implementation, we would
                # parse the parameters more carefully based on the language
                params = params_node.strip('()').split(',')
                match['parameters'] = [p.strip() for p in params if p.strip()]
            
        return matches


class MethodDefinitionPattern(QueryBasedPattern):
    """Pattern for detecting method definitions within classes."""
    
    def __init__(self):
        """Initialize a pattern for detecting method definitions."""
        super().__init__(
            name="method_definition",
            description="Identifies method definitions in classes",
            languages=["python", "javascript", "typescript", "ruby", "java", "cpp"],
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                (class_definition
                  body: (block 
                    (function_definition
                      name: (identifier) @name
                      parameters: (parameters) @params
                      body: (block) @body)))
            """,
            'javascript': """
                (class_declaration
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @name
                      parameters: (formal_parameters) @params
                      body: (statement_block) @body)))
            """,
            'typescript': """
                (class_declaration
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @name
                      parameters: (formal_parameters) @params
                      body: (statement_block) @body)))
            """,
            'ruby': """
                (class
                  body: (body_statement
                    (method
                      name: (identifier) @name
                      parameters: (method_parameters) @params
                      body: (body_statement) @body)))
            """,
            'java': """
                (class_declaration
                  body: (class_body
                    (method_declaration
                      name: (identifier) @name
                      parameters: (formal_parameters) @params
                      body: (block) @body)))
            """,
            'cpp': """
                (class_specifier
                  body: (field_declaration_list
                    (function_definition
                      declarator: (function_declarator
                        declarator: (field_identifier) @name)
                      body: (compound_statement) @body)))
            """,
        }
        
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results for method definitions.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of method matches with details
        """
        # Use the generic implementation as a starting point
        matches = super()._process_query_results(query_results, code, language, file_path, parser)
        
        # Set specific match type and extract additional information
        for match in matches:
            match['type'] = 'method'
            
            # Extract parameter information if available
            if 'params' in match:
                params_node = match['params']['text']
                # Simple parameter extraction
                params = params_node.strip('()').split(',')
                match['parameters'] = [p.strip() for p in params if p.strip()]
        
        return matches


class ConstructorPattern(QueryBasedPattern):
    """Pattern for detecting class constructors."""
    
    def __init__(self):
        """Initialize a pattern for detecting class constructors."""
        super().__init__(
            name="constructor",
            description="Identifies class constructors",
            languages=["python", "javascript", "typescript", "java", "cpp"],
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                (class_definition
                  body: (block 
                    (function_definition
                      name: (identifier) @name
                      (#eq? @name "__init__")
                      parameters: (parameters) @params
                      body: (block) @body)))
            """,
            'javascript': """
                (class_declaration
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @name
                      (#eq? @name "constructor")
                      parameters: (formal_parameters) @params
                      body: (statement_block) @body)))
            """,
            'typescript': """
                (class_declaration
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @name
                      (#eq? @name "constructor")
                      parameters: (formal_parameters) @params
                      body: (statement_block) @body)))
            """,
            'java': """
                (class_declaration
                  name: (identifier) @class_name
                  body: (class_body
                    (constructor_declaration
                      name: (identifier) @name
                      (#eq? @name @class_name)
                      parameters: (formal_parameters) @params
                      body: (block) @body)))
            """,
            'cpp': """
                (class_specifier
                  name: (type_identifier) @class_name
                  body: (field_declaration_list
                    (function_definition
                      declarator: (function_declarator
                        declarator: (field_identifier) @name
                        (#eq? @name @class_name))
                      body: (compound_statement) @body)))
            """,
        }
        
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results for constructors.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of constructor matches with details
        """
        # Use the generic implementation as a starting point
        matches = super()._process_query_results(query_results, code, language, file_path, parser)
        
        # Set specific match type and extract additional information
        for match in matches:
            match['type'] = 'constructor'
            
            # Extract parameter information if available
            if 'params' in match:
                params_node = match['params']['text']
                # Simple parameter extraction
                params = params_node.strip('()').split(',')
                match['parameters'] = [p.strip() for p in params if p.strip()]
                
            # Add class name if available
            if 'class_name' in match:
                match['class'] = match['class_name']['text']
        
        return matches


class AllFunctionsPattern(CompositePattern):
    """A composite pattern that matches all types of functions and methods."""
    
    def __init__(self):
        """Initialize a pattern for detecting all function types."""
        super().__init__(
            name="all_functions",
            description="Identifies all functions, methods, and constructors",
            patterns=[
                FunctionDefinitionPattern(),
                MethodDefinitionPattern(),
                ConstructorPattern(),
            ],
        )