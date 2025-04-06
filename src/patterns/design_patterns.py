"""
Patterns for detecting common design patterns in code.
"""

from typing import Dict, List, Optional, Set, Union
from pathlib import Path
import logging

import tree_sitter

from ..pattern_base import QueryBasedPattern, CompositePattern, Pattern


class SingletonPatternPython(QueryBasedPattern):
    """Pattern for detecting Singleton design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Singleton pattern in Python."""
        super().__init__(
            name="singleton_python",
            description="Identifies Singleton pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python singletons
        self.queries = {
            'python': """
                ; Instance variable check
                (class_definition
                  name: (identifier) @name
                  body: (block
                    (expression_statement
                      (assignment
                        left: (identifier) @instance_var
                        (#match? @instance_var "^_instance$|^_singleton$|^instance$|^_INSTANCE$")
                        right: (none) @none_val))
                    
                    ; Method that checks instance and returns it
                    (function_definition
                      name: (identifier) @method_name
                      (#match? @method_name "^get_instance$|^getInstance$|^instance$")
                      parameters: (parameters) @params
                      body: (block
                        (if_statement
                          condition: (comparison_operator
                            left: (attribute 
                              object: (identifier) @class_ref
                              attribute: (identifier) @instance_check)
                            right: (none))
                          consequence: (block
                            (expression_statement
                              (assignment
                                left: (attribute
                                  object: (identifier) @class_assign
                                  attribute: (identifier) @instance_assign)
                                right: (call
                                  function: (identifier) @class_call)))))))))
                
                ; Alternative singleton pattern with __new__ method
                (class_definition
                  name: (identifier) @name
                  body: (block
                    (expression_statement
                      (assignment
                        left: (identifier) @instance_var
                        (#match? @instance_var "^_instance$|^_singleton$|^instance$|^_INSTANCE$")
                        right: (none) @none_val))
                    
                    ; __new__ method that implements singleton
                    (function_definition
                      name: (identifier) @method_name
                      (#eq? @method_name "__new__")
                      parameters: (parameters) @params
                      body: (block
                        (if_statement
                          condition: (comparison_operator
                            left: (attribute 
                              object: (identifier) @class_ref
                              attribute: (identifier) @instance_check)
                            right: (none))
                          consequence: (block
                            (expression_statement
                              (assignment
                                left: (attribute
                                  object: (identifier) @class_assign
                                  attribute: (identifier) @instance_assign)
                                right: (call
                                  function: (identifier) @class_call)))))))))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Singleton pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of singleton pattern matches with details
        """
        # Group captures by class name
        class_captures = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            if capture == 'name':
                class_name = text
                if class_name not in class_captures:
                    class_captures[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            else:
                # Add other captures to the class info
                class_name = None
                for name, info in class_captures.items():
                    if 'name' in info:
                        # Simple heuristic - assume the most recent class
                        class_name = name
                
                if class_name:
                    class_captures[class_name][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
        
        # Convert to matches
        matches = []
        for class_name, info in class_captures.items():
            # Check for minimum requirements of a singleton
            if ('instance_var' in info and 
                ('method_name' in info or 
                 ('method_name' in info and info['method_name']['text'] == '__new__'))):
                
                match = {
                    'type': 'design_pattern',
                    'pattern': 'singleton',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': 'python',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class SingletonPatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Singleton design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Singleton pattern in JavaScript."""
        super().__init__(
            name="singleton_javascript",
            description="Identifies Singleton pattern implementation in JavaScript/TypeScript",
            languages=["javascript", "typescript"],
        )
        
        # Define the query for JavaScript singletons
        self.queries = {
            'javascript': """
                ; Classic singleton with static instance
                (class_declaration
                  name: (identifier) @name
                  body: (class_body
                    (field_definition
                      (property_identifier) @instance_var
                      (#match? @instance_var "^_instance$|^_singleton$|^instance$|^_INSTANCE$")
                      (null) @null_val)
                    
                    (method_definition
                      (property_identifier) @method_name
                      (#match? @method_name "^getInstance$|^instance$|^get_instance$")
                      body: (statement_block
                        (if_statement
                          condition: (binary_expression
                            left: (member_expression
                              object: (this) @this
                              property: (property_identifier) @instance_check)
                            right: (null) @null_check)
                          consequence: (statement_block
                            (expression_statement
                              (assignment_expression
                                left: (member_expression
                                  object: (this) @this_assign
                                  property: (property_identifier) @instance_assign)
                                right: (new_expression
                                  constructor: (identifier) @constructor_call)))))))))
                
                ; Module/IIFE singleton
                (lexical_declaration
                  (variable_declarator
                    name: (identifier) @singleton_var
                    value: (call_expression
                      function: (function) @singleton_func
                      arguments: (arguments)
                      body: (statement_block
                        (lexical_declaration
                          (variable_declarator
                            name: (identifier) @instance_var
                            (#match? @instance_var "^_instance$|^instance$|^singleton$")))
                        (return_statement
                          (object
                            (method_definition
                              name: (property_identifier) @get_method
                              (#match? @get_method "^getInstance$|^instance$|^get_instance$")
                              body: (statement_block
                                (if_statement
                                  condition: (binary_expression
                                    left: (identifier) @instance_check
                                    operator: (=="==="))
                                  consequence: (statement_block
                                    (expression_statement
                                      (assignment_expression
                                        left: (identifier) @instance_assign
                                        right: (object) @singleton_obj))))))))))))
            """,
            'typescript': """
                ; Classic singleton with static instance
                (class_declaration
                  name: (identifier) @name
                  body: (class_body
                    (field_definition
                      name: (property_identifier) @instance_var
                      (#match? @instance_var "^_instance$|^_singleton$|^instance$|^_INSTANCE$")
                      value: (null) @null_val)
                    
                    (method_definition
                      name: (property_identifier) @method_name
                      (#match? @method_name "^getInstance$|^instance$|^get_instance$")
                      body: (statement_block
                        (if_statement
                          condition: (binary_expression
                            left: (member_expression
                              object: (this) @this
                              property: (property_identifier) @instance_check)
                            right: (null) @null_check)
                          consequence: (statement_block
                            (expression_statement
                              (assignment_expression
                                left: (member_expression
                                  object: (this) @this_assign
                                  property: (property_identifier) @instance_assign)
                                right: (new_expression
                                  constructor: (identifier) @constructor_call)))))))))
            """,
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Singleton pattern in JavaScript/TypeScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of singleton pattern matches with details
        """
        # Group captures by class name
        class_captures = {}
        iife_captures = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            if capture == 'name':
                class_name = text
                if class_name not in class_captures:
                    class_captures[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            elif capture == 'singleton_var':
                # Handle IIFE singleton
                var_name = text
                if var_name not in iife_captures:
                    iife_captures[var_name] = {
                        'name': var_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            else:
                # Add other captures to the class or IIFE info
                class_name = None
                for name, info in class_captures.items():
                    if 'name' in info:
                        # Simple heuristic - use the most recent class
                        class_name = name
                
                if class_name:
                    class_captures[class_name][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
                
                var_name = None
                for name, info in iife_captures.items():
                    if 'name' in info:
                        # Simple heuristic - use the most recent IIFE
                        var_name = name
                
                if var_name:
                    iife_captures[var_name][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
        
        # Convert to matches
        matches = []
        
        # Process class-based singletons
        for class_name, info in class_captures.items():
            # Check for minimum requirements of a singleton
            if ('instance_var' in info and 'method_name' in info):
                match = {
                    'type': 'design_pattern',
                    'pattern': 'singleton',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'implementation': 'class-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        # Process IIFE/module singletons
        for var_name, info in iife_captures.items():
            # Check for minimum requirements of a singleton
            if ('instance_var' in info and 'get_method' in info):
                match = {
                    'type': 'design_pattern',
                    'pattern': 'singleton',
                    'name': var_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'implementation': 'module-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class FactoryMethodPattern(QueryBasedPattern):
    """Pattern for detecting Factory Method design pattern."""
    
    def __init__(self):
        """Initialize a pattern for detecting Factory Method pattern."""
        super().__init__(
            name="factory_method",
            description="Identifies Factory Method pattern implementation",
            languages=["python", "javascript", "typescript", "java"],
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                ; Class method that creates and returns object instances
                (class_definition
                  name: (identifier) @class_name
                  body: (block
                    (function_definition
                      name: (identifier) @method_name
                      (#match? @method_name "^create|^make|^build|^get|^new")
                      body: (block
                        ; Look for return statement with a new object
                        (return_statement
                          (call
                            function: (identifier) @return_class))))))
                            
                ; Standalone function that creates and returns object instances
                (function_definition
                  name: (identifier) @function_name
                  (#match? @function_name "^create|^make|^build|^get|^new|^factory")
                  body: (block
                    ; Look for return statement with a new object
                    (return_statement
                      (call
                        function: (identifier) @return_class))))
            """,
            'javascript': """
                ; Class method that creates and returns object instances
                (class_declaration
                  name: (identifier) @class_name
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @method_name
                      (#match? @method_name "^create|^make|^build|^get|^new")
                      body: (statement_block
                        ; Look for return statement with a new object
                        (return_statement
                          (new_expression
                            constructor: (identifier) @return_class))))))
                            
                ; Standalone function that creates and returns object instances
                (function_declaration
                  name: (identifier) @function_name
                  (#match? @function_name "^create|^make|^build|^get|^new|^factory")
                  body: (statement_block
                    ; Look for return statement with a new object
                    (return_statement
                      (new_expression
                        constructor: (identifier) @return_class))))
            """,
            'typescript': """
                ; Class method that creates and returns object instances
                (class_declaration
                  name: (identifier) @class_name
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @method_name
                      (#match? @method_name "^create|^make|^build|^get|^new")
                      body: (statement_block
                        ; Look for return statement with a new object
                        (return_statement
                          (new_expression
                            constructor: (identifier) @return_class))))))
                            
                ; Standalone function that creates and returns object instances
                (function_declaration
                  name: (identifier) @function_name
                  (#match? @function_name "^create|^make|^build|^get|^new|^factory")
                  body: (statement_block
                    ; Look for return statement with a new object
                    (return_statement
                      (new_expression
                        constructor: (identifier) @return_class))))
            """,
            'java': """
                ; Class method that creates and returns object instances
                (class_declaration
                  name: (identifier) @class_name
                  body: (class_body
                    (method_declaration
                      name: (identifier) @method_name
                      (#match? @method_name "^create|^make|^build|^get|^new")
                      body: (block
                        ; Look for return statement with a new object
                        (return_statement
                          (object_creation_expression
                            type: (type_identifier) @return_class))))))
                            
                ; Standalone method that creates and returns object instances
                (method_declaration
                  name: (identifier) @method_name
                  (#match? @method_name "^create|^make|^build|^get|^new|^factory")
                  body: (block
                    ; Look for return statement with a new object
                    (return_statement
                      (object_creation_expression
                        type: (type_identifier) @return_class))))
            """,
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Factory Method pattern.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of factory method pattern matches with details
        """
        # Track factory methods by name and type
        factory_methods = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            if capture in ('method_name', 'function_name'):
                method_name = text
                method_type = 'class_method' if capture == 'method_name' else 'function'
                
                key = f"{method_name}:{method_type}"
                if key not in factory_methods:
                    factory_methods[key] = {
                        'name': method_name,
                        'type': method_type,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            elif capture == 'class_name':
                # Add class info to the most recently seen method
                class_name = text
                
                # Find the most recent method that doesn't have class info
                for key, info in factory_methods.items():
                    if info['type'] == 'class_method' and 'class' not in info:
                        info['class'] = class_name
                        break
            elif capture == 'return_class':
                # Add return class info to the most recently seen method
                return_class = text
                
                # Find the most recent method that doesn't have return info
                most_recent_key = None
                most_recent_line = -1
                
                for key, info in factory_methods.items():
                    if 'return_class' not in info and info['line'] > most_recent_line:
                        most_recent_key = key
                        most_recent_line = info['line']
                
                if most_recent_key:
                    factory_methods[most_recent_key]['return_class'] = return_class
        
        # Convert to matches
        matches = []
        
        for key, info in factory_methods.items():
            # Check for minimum requirements of a factory method
            if 'return_class' in info:
                match = {
                    'type': 'design_pattern',
                    'pattern': 'factory_method',
                    'name': info['name'],
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'creates': info['return_class'],
                    'implementation': info['type'],
                }
                
                if 'class' in info:
                    match['class'] = info['class']
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class SingletonPattern(CompositePattern):
    """A composite pattern that matches Singleton pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Singleton pattern."""
        super().__init__(
            name="singleton",
            description="Identifies Singleton pattern implementation across multiple languages",
            patterns=[
                SingletonPatternPython(),
                SingletonPatternJavaScript(),
            ],
        )


class DesignPatternsPattern(CompositePattern):
    """A composite pattern that matches all supported design patterns."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting all design patterns."""
        super().__init__(
            name="design_patterns",
            description="Identifies all supported design patterns",
            patterns=[
                SingletonPattern(),
                FactoryMethodPattern(),
            ],
        )