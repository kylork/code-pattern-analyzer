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


class ObserverPatternPython(QueryBasedPattern):
    """Pattern for detecting Observer design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Observer pattern in Python."""
        super().__init__(
            name="observer_python",
            description="Identifies Observer pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python observer pattern
        self.queries = {
            'python': """
                ; Subject/Observable class with observer list and notify method
                (class_definition
                  name: (identifier) @subject_class
                  body: (block
                    ; Look for list of observers as instance variable
                    (function_definition
                      name: (identifier) @init_method
                      (#eq? @init_method "__init__")
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              (#eq? @self_ref "self")
                              attribute: (identifier) @observers_var
                              (#match? @observers_var "^_?observers$|^_?listeners$"))
                            right: (list) @empty_list)))))
                    
                    ; Methods to add/register observers
                    (function_definition
                      name: (identifier) @attach_method
                      (#match? @attach_method "^attach$|^register$|^add_observer$|^subscribe$")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @observer_param)
                      body: (block) @attach_body)
                    
                    ; Method to notify observers
                    (function_definition
                      name: (identifier) @notify_method
                      (#match? @notify_method "^notify$|^notify_all$|^update_all$")
                      parameters: (parameters
                        (identifier) @self_param)
                      body: (block
                        (for_statement
                          left: (identifier) @observer_var
                          right: (attribute
                            object: (identifier) @self_ref
                            (#eq? @self_ref "self")
                            attribute: (identifier) @observers_list)
                          body: (block
                            (expression_statement
                              (call
                                function: (attribute
                                  object: (identifier) @observer_obj
                                  attribute: (identifier) @update_method
                                  (#match? @update_method "^update$|^notify$|^on_change$"))
                                arguments: (argument_list) @call_args))))))
                ))
                
                ; Observer class with update method
                (class_definition
                  name: (identifier) @observer_class
                  body: (block
                    ; Update method
                    (function_definition
                      name: (identifier) @update_method
                      (#match? @update_method "^update$|^on_change$|^on_notify$")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @subject_param)
                      body: (block) @update_body)
                ))
                
                ; Abstract observer class with update method
                (class_definition
                  (identifier) @observer_base_class
                  body: (block
                    ; Abstract update method
                    (function_definition
                      name: (identifier) @update_method
                      (#match? @update_method "^update$|^on_change$|^on_notify$")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @subject_param)
                      body: (block
                        (raise_statement) @not_implemented
                        (#match? @not_implemented ".*NotImplementedError.*")))
                ))
                
                ; Event emitter pattern (alternative implementation)
                (class_definition
                  name: (identifier) @emitter_class
                  body: (block
                    ; Dictionary of listeners
                    (function_definition
                      name: (identifier) @init_method
                      (#eq? @init_method "__init__")
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              (#eq? @self_ref "self")
                              attribute: (identifier) @events_var
                              (#match? @events_var "^_?events$|^_?listeners$|^_?callbacks$"))
                            right: (dictionary) @empty_dict))))
                    
                    ; Method to add event listener
                    (function_definition
                      name: (identifier) @on_method
                      (#match? @on_method "^on$|^add_listener$|^add_event_listener$")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @event_name_param
                        (identifier) @callback_param)
                      body: (block) @on_body)
                    
                    ; Method to emit/trigger event
                    (function_definition
                      name: (identifier) @emit_method
                      (#match? @emit_method "^emit$|^trigger$|^fire$")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @event_name_param)
                      body: (block) @emit_body)
                ))
            """
        }
        
    def _process_query_results(self, 
                             query_results: List[Dict], 
                             code: str, 
                             language: str,
                             file_path: Optional[str] = None,
                             parser=None) -> List[Dict]:
        """Process query results for Observer pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of observer pattern matches with details
        """
        # Group captures by class role (subject, observer, emitter)
        subjects = {}
        observers = {}
        emitters = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Subject class
            if capture == 'subject_class':
                class_name = text
                if class_name not in subjects:
                    subjects[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'subject',
                    }
            
            # Observer class
            elif capture == 'observer_class':
                class_name = text
                if class_name not in observers:
                    observers[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'observer',
                    }
            
            # Observer base/abstract class
            elif capture == 'observer_base_class':
                class_name = text
                if class_name not in observers:
                    observers[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'observer_base',
                    }
            
            # Event emitter class (alternative implementation)
            elif capture == 'emitter_class':
                class_name = text
                if class_name not in emitters:
                    emitters[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'emitter',
                    }
            
            # Capture methods to associate with classes
            elif capture in ('attach_method', 'notify_method', 'observers_var'):
                # Associate with most recent subject
                if subjects:
                    most_recent = list(subjects.keys())[-1]
                    subjects[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            
            # Capture update method to associate with observer
            elif capture == 'update_method':
                # Associate with most recent observer if possible
                if observers:
                    most_recent = list(observers.keys())[-1]
                    observers[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            
            # Capture emitter methods
            elif capture in ('on_method', 'emit_method', 'events_var'):
                # Associate with most recent emitter
                if emitters:
                    most_recent = list(emitters.keys())[-1]
                    emitters[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
        
        # Convert to matches
        matches = []
        
        # Process subject classes
        for class_name, info in subjects.items():
            # Check for minimum requirements of a subject
            has_observers_list = 'observers_var' in info
            has_attach = 'attach_method' in info
            has_notify = 'notify_method' in info
            
            if has_observers_list and (has_attach or has_notify):
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': 'python',
                    'role': 'subject',
                    'implementation': 'class-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        # Process observer classes
        for class_name, info in observers.items():
            # Check for minimum requirements of an observer
            has_update = 'update_method' in info
            
            if has_update:
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': 'python',
                    'role': info['role'],
                    'implementation': 'class-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        # Process emitter classes (alternative implementation)
        for class_name, info in emitters.items():
            # Check for minimum requirements of an emitter
            has_events_dict = 'events_var' in info
            has_on = 'on_method' in info
            has_emit = 'emit_method' in info
            
            if has_events_dict and (has_on or has_emit):
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': 'python',
                    'role': 'subject',
                    'implementation': 'event-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class ObserverPatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Observer design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Observer pattern in JavaScript."""
        super().__init__(
            name="observer_javascript",
            description="Identifies Observer pattern implementation in JavaScript/TypeScript",
            languages=["javascript", "typescript"],
        )
        
        # Define the query for JavaScript observer pattern
        self.queries = {
            'javascript': """
                ; Subject/Observable class with observer list and notify method
                (class_declaration
                  name: (identifier) @subject_class
                  body: (class_body
                    ; Look for constructor with array of observers
                    (method_definition
                      name: (property_identifier) @constructor_method
                      (#eq? @constructor_method "constructor")
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @observers_var
                              (#match? @observers_var "^_?observers$|^_?listeners$"))
                            right: (array) @empty_array))))
                    
                    ; Methods to add/register observers
                    (method_definition
                      name: (property_identifier) @attach_method
                      (#match? @attach_method "^attach$|^register$|^addObserver$|^subscribe$")
                      body: (statement_block) @attach_body)
                    
                    ; Method to notify observers
                    (method_definition
                      name: (property_identifier) @notify_method
                      (#match? @notify_method "^notify$|^notifyAll$|^updateAll$")
                      body: (statement_block
                        (for_statement
                          (member_expression
                            object: (this)
                            property: (property_identifier) @observers_array))
                        ))
                ))
                
                ; Observer class with update method
                (class_declaration
                  name: (identifier) @observer_class
                  body: (class_body
                    ; Update method
                    (method_definition
                      name: (property_identifier) @update_method
                      (#match? @update_method "^update$|^onChange$|^onNotify$")
                      body: (statement_block) @update_body)
                ))
                
                ; Abstract observer class with update method that throws error
                (class_declaration
                  name: (identifier) @observer_base_class
                  body: (class_body
                    ; Abstract update method
                    (method_definition
                      name: (property_identifier) @update_method
                      (#match? @update_method "^update$|^onChange$|^onNotify$")
                      body: (statement_block
                        (throw_statement) @throw_error))
                ))
                
                ; EventEmitter pattern (alternative implementation)
                (class_declaration
                  name: (identifier) @emitter_class
                  body: (class_body
                    ; Object of listeners
                    (method_definition
                      name: (property_identifier) @constructor_method
                      (#eq? @constructor_method "constructor") 
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @events_var
                              (#match? @events_var "^_?events$|^_?listeners$|^_?callbacks$"))
                            right: (object) @empty_obj))))
                    
                    ; Method to add event listener
                    (method_definition
                      name: (property_identifier) @on_method
                      (#match? @on_method "^on$|^addEventListener$|^addListener$")
                      body: (statement_block) @on_body)
                    
                    ; Method to emit/trigger event
                    (method_definition
                      name: (property_identifier) @emit_method
                      (#match? @emit_method "^emit$|^trigger$|^fire$")
                      body: (statement_block) @emit_body)
                ))
            """,
            'typescript': """
                ; Subject/Observable class with observer list and notify method
                (class_declaration
                  name: (identifier) @subject_class
                  body: (class_body
                    ; Look for property declaration of observers array
                    (public_field_definition
                      name: (property_identifier) @observers_var
                      (#match? @observers_var "^_?observers$|^_?listeners$")
                      value: (array) @empty_array)
                    
                    ; Or look for constructor with array of observers
                    (method_definition
                      name: (property_identifier) @constructor_method
                      (#eq? @constructor_method "constructor")
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @observers_var
                              (#match? @observers_var "^_?observers$|^_?listeners$"))
                            right: (array) @empty_array))))
                    
                    ; Methods to add/register observers
                    (method_definition
                      name: (property_identifier) @attach_method
                      (#match? @attach_method "^attach$|^register$|^addObserver$|^subscribe$")
                      body: (statement_block) @attach_body)
                    
                    ; Method to notify observers
                    (method_definition
                      name: (property_identifier) @notify_method
                      (#match? @notify_method "^notify$|^notifyAll$|^updateAll$")
                      body: (statement_block
                        (for_statement
                          (member_expression
                            object: (this)
                            property: (property_identifier) @observers_array))
                        ))
                ))
                
                ; Observer interface with update method
                (interface_declaration
                  name: (identifier) @observer_interface
                  body: (interface_body
                    (method_signature
                      name: (property_identifier) @update_method
                      (#match? @update_method "^update$|^onChange$|^onNotify$"))
                ))
                
                ; Observer class with update method
                (class_declaration
                  name: (identifier) @observer_class
                  body: (class_body
                    ; Update method
                    (method_definition
                      name: (property_identifier) @update_method
                      (#match? @update_method "^update$|^onChange$|^onNotify$")
                      body: (statement_block) @update_body)
                ))
                
                ; Abstract observer class with update method 
                (class_declaration
                  name: (identifier) @observer_base_class
                  superclass: (identifier) @abstract_superclass
                  (#eq? @abstract_superclass "AbstractObserver") 
                  body: (class_body
                    ; Abstract update method implementation
                    (method_definition
                      name: (property_identifier) @update_method
                      (#match? @update_method "^update$|^onChange$|^onNotify$")
                      body: (statement_block) @update_body)
                ))
                
                ; EventEmitter pattern (alternative implementation)
                (class_declaration
                  name: (identifier) @emitter_class
                  body: (class_body
                    ; Object of listeners
                    (public_field_definition
                      name: (property_identifier) @events_var
                      (#match? @events_var "^_?events$|^_?listeners$|^_?callbacks$")
                      value: (object) @empty_obj)
                    
                    ; Or constructor with object init
                    (method_definition
                      name: (property_identifier) @constructor_method
                      (#eq? @constructor_method "constructor") 
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @events_var
                              (#match? @events_var "^_?events$|^_?listeners$|^_?callbacks$"))
                            right: (object) @empty_obj))))
                    
                    ; Method to add event listener
                    (method_definition
                      name: (property_identifier) @on_method
                      (#match? @on_method "^on$|^addEventListener$|^addListener$")
                      body: (statement_block) @on_body)
                    
                    ; Method to emit/trigger event
                    (method_definition
                      name: (property_identifier) @emit_method
                      (#match? @emit_method "^emit$|^trigger$|^fire$")
                      body: (statement_block) @emit_body)
                ))
            """
        }
        
    def _process_query_results(self, 
                             query_results: List[Dict], 
                             code: str, 
                             language: str,
                             file_path: Optional[str] = None,
                             parser=None) -> List[Dict]:
        """Process query results for Observer pattern in JavaScript/TypeScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of observer pattern matches with details
        """
        # Group captures by class role (subject, observer, emitter)
        subjects = {}
        observers = {}
        interfaces = {}
        emitters = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Subject class
            if capture == 'subject_class':
                class_name = text
                if class_name not in subjects:
                    subjects[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'subject',
                    }
            
            # Observer class
            elif capture == 'observer_class':
                class_name = text
                if class_name not in observers:
                    observers[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'observer',
                    }
            
            # Observer base/abstract class
            elif capture == 'observer_base_class':
                class_name = text
                if class_name not in observers:
                    observers[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'observer_base',
                    }
            
            # Observer interface (TypeScript)
            elif capture == 'observer_interface':
                interface_name = text
                if interface_name not in interfaces:
                    interfaces[interface_name] = {
                        'name': interface_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'observer_interface',
                    }
            
            # Event emitter class (alternative implementation)
            elif capture == 'emitter_class':
                class_name = text
                if class_name not in emitters:
                    emitters[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'emitter',
                    }
            
            # Capture methods to associate with classes
            elif capture in ('attach_method', 'notify_method', 'observers_var', 'observers_array'):
                # Associate with most recent subject
                if subjects:
                    most_recent = list(subjects.keys())[-1]
                    subjects[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            
            # Capture update method to associate with observer or interface
            elif capture == 'update_method':
                # Associate with most recent observer if possible
                if observers:
                    most_recent = list(observers.keys())[-1]
                    observers[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
                # Otherwise try to associate with an interface
                elif interfaces:
                    most_recent = list(interfaces.keys())[-1]
                    interfaces[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
            
            # Capture emitter methods
            elif capture in ('on_method', 'emit_method', 'events_var'):
                # Associate with most recent emitter
                if emitters:
                    most_recent = list(emitters.keys())[-1]
                    emitters[most_recent][capture] = {
                        'text': text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                    }
        
        # Convert to matches
        matches = []
        
        # Process subject classes
        for class_name, info in subjects.items():
            # Check for minimum requirements of a subject
            has_observers_list = 'observers_var' in info or 'observers_array' in info
            has_attach = 'attach_method' in info
            has_notify = 'notify_method' in info
            
            if has_observers_list and (has_attach or has_notify):
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'role': 'subject',
                    'implementation': 'class-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        # Process observer classes
        for class_name, info in observers.items():
            # Check for minimum requirements of an observer
            has_update = 'update_method' in info
            
            if has_update:
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'role': info['role'],
                    'implementation': 'class-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        # Process observer interfaces (TypeScript)
        for interface_name, info in interfaces.items():
            # Check for minimum requirements of an observer interface
            has_update = 'update_method' in info
            
            if has_update:
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': interface_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'role': 'observer_interface',
                    'implementation': 'interface-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        # Process emitter classes (alternative implementation)
        for class_name, info in emitters.items():
            # Check for minimum requirements of an emitter
            has_events_dict = 'events_var' in info
            has_on = 'on_method' in info
            has_emit = 'emit_method' in info
            
            if has_events_dict and (has_on or has_emit):
                match = {
                    'type': 'design_pattern',
                    'pattern': 'observer',
                    'name': class_name,
                    'line': info['line'],
                    'column': info['column'],
                    'language': language,
                    'role': 'subject',
                    'implementation': 'event-based',
                }
                
                if file_path:
                    match['file'] = file_path
                    
                matches.append(match)
        
        return matches


class ObserverPattern(CompositePattern):
    """A composite pattern that matches Observer pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Observer pattern."""
        super().__init__(
            name="observer",
            description="Identifies Observer pattern implementation across multiple languages",
            patterns=[
                ObserverPatternPython(),
                ObserverPatternJavaScript(),
            ],
        )


class DecoratorPatternPython(QueryBasedPattern):
    """Pattern for detecting Decorator design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Decorator pattern in Python."""
        super().__init__(
            name="decorator_python",
            description="Identifies Decorator pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python decorator pattern
        self.queries = {
            'python': """
                ; Class-based Decorator pattern with Component interface
                
                ; Abstract Component class/interface
                (class_definition
                  name: (identifier) @component_class
                  body: (block
                    (function_definition
                      name: (identifier) @component_method
                      (#match? @component_method "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (block) @component_method_body)))
                
                ; Concrete Component class implementing the interface
                (class_definition
                  name: (identifier) @concrete_component_class
                  superclasses: (argument_list
                    (identifier) @component_parent
                    (#match? @component_parent "^Component$|^AbstractComponent$|^IComponent$"))
                  body: (block
                    (function_definition
                      name: (identifier) @concrete_component_method
                      (#match? @concrete_component_method "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (block) @concrete_method_body)))
                
                ; Decorator base class
                (class_definition
                  name: (identifier) @decorator_base_class
                  (#match? @decorator_base_class "^Decorator$|^AbstractDecorator$|^BaseDecorator$")
                  superclasses: (argument_list
                    (identifier) @decorator_parent
                    (#match? @decorator_parent "^Component$|^AbstractComponent$|^IComponent$"))
                  body: (block
                    ; Constructor storing the decorated component
                    (function_definition
                      name: (identifier) @decorator_init
                      (#eq? @decorator_init "__init__")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @component_param)
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @component_attr
                              (#match? @component_attr "^_?component$|^_?decorated$|^_?wrapped"))
                            right: (identifier) @component_assign))))
                    
                    ; Operation method delegating to component
                    (function_definition
                      name: (identifier) @decorator_operation
                      (#match? @decorator_operation "^operation$|^execute$|^run$|^perform$|^do$")
                      parameters: (parameters)
                      body: (block
                        (return_statement
                          (call
                            function: (attribute
                              object: (attribute
                                object: (identifier) @self_ref2
                                attribute: (identifier) @component_attr2
                                (#match? @component_attr2 "^_?component$|^_?decorated$|^_?wrapped"))
                              attribute: (identifier) @delegate_method
                              (#match? @delegate_method "^operation$|^execute$|^run$|^perform$|^do$"))))))))
                
                ; Concrete decorator classes
                (class_definition
                  name: (identifier) @concrete_decorator_class
                  superclasses: (argument_list
                    (identifier) @concrete_decorator_parent
                    (#match? @concrete_decorator_parent "^Decorator$|^AbstractDecorator$|^BaseDecorator$"))
                  body: (block
                    (function_definition
                      name: (identifier) @concrete_decorator_operation
                      (#match? @concrete_decorator_operation "^operation$|^execute$|^run$|^perform$|^do$")
                      parameters: (parameters)
                      body: (block) @concrete_decorator_body)))
                      
                ; Function decorators (Python-specific)
                (function_definition
                  name: (identifier) @decorator_function
                  parameters: (parameters
                    (identifier) @function_param
                    (#match? @function_param "^func$|^function$|^f$|^method$|^m$|^callable$|^wrapped$"))
                  body: (block
                    (function_definition
                      name: (identifier) @wrapper_function
                      (#match? @wrapper_function "^wrapper$|^wrapped$|^inner$|^inside$|^_wrapper$")
                      parameters: (parameters) @wrapper_params
                      body: (block
                        (expression_statement
                          (call
                            function: (identifier) @original_function
                            (#match? @original_function "^func$|^function$|^f$|^method$|^m$|^callable$|^wrapped$")))
                        (return_statement) @wrapper_return))
                    (return_statement
                      (identifier) @return_wrapper
                      (#match? @return_wrapper "^wrapper$|^wrapped$|^inner$|^inside$|^_wrapper$"))))
                
                ; Object composition (no inheritance) based decorator pattern
                (class_definition
                  name: (identifier) @composition_decorator_class
                  body: (block
                    ; Constructor storing the decorated object
                    (function_definition
                      name: (identifier) @composition_init
                      (#eq? @composition_init "__init__")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @processor_param
                        (#match? @processor_param "^processor$|^component$|^wrapped$|^decoratee$|^subject$"))
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @processor_attr
                              (#match? @processor_attr "^processor$|^component$|^wrapped$|^decoratee$|^subject$"))
                            right: (identifier) @processor_assign
                            (#match? @processor_assign "^processor$|^component$|^wrapped$|^decoratee$|^subject$")))))
                    
                    ; Method that enhances the wrapped object's method
                    (function_definition
                      name: (identifier) @processor_method
                      (#match? @processor_method "^process$|^execute$|^run$|^operate$|^apply$")
                      parameters: (parameters
                        (identifier) @self_param2
                        (identifier) @text_param)
                      body: (block
                        (return_statement
                          (call
                            function: (attribute
                              object: (attribute
                                object: (identifier) @self_ref3
                                attribute: (identifier) @processor_attr2
                                (#match? @processor_attr2 "^processor$|^component$|^wrapped$|^decoratee$|^subject$"))
                              attribute: (identifier) @processor_method2
                              (#match? @processor_method2 "^process$|^execute$|^run$|^operate$|^apply$"))
                            arguments: (argument_list) @processor_args))))))
            """
        }
        
    def _process_query_results(self, 
                             query_results: List[Dict], 
                             code: str, 
                             language: str,
                             file_path: Optional[str] = None,
                             parser=None) -> List[Dict]:
        """Process query results for Decorator pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of decorator pattern matches with details
        """
        # Group captures by role in the pattern
        components = {}
        concrete_components = {}
        decorator_base = {}
        concrete_decorators = {}
        function_decorators = {}
        composition_decorators = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Component interface
            if capture == 'component_class':
                class_name = text
                if class_name not in components:
                    components[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'component',
                    }
            
            # Concrete component
            elif capture == 'concrete_component_class':
                class_name = text
                if class_name not in concrete_components:
                    concrete_components[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_component',
                    }
            
            # Decorator base class
            elif capture == 'decorator_base_class':
                class_name = text
                if class_name not in decorator_base:
                    decorator_base[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'decorator_base',
                    }
            
            # Concrete decorator
            elif capture == 'concrete_decorator_class':
                class_name = text
                if class_name not in concrete_decorators:
                    concrete_decorators[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_decorator',
                    }
            
            # Function decorator
            elif capture == 'decorator_function':
                function_name = text
                if function_name not in function_decorators:
                    function_decorators[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'function_decorator',
                    }
            
            # Composition-based decorator
            elif capture == 'composition_decorator_class':
                class_name = text
                if class_name not in composition_decorators:
                    composition_decorators[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'composition_decorator',
                    }
            
            # Store component parent info
            elif capture == 'component_parent':
                parent_name = text
                # Find most recent concrete component to associate with
                if concrete_components:
                    most_recent = list(concrete_components.keys())[-1]
                    concrete_components[most_recent]['parent'] = parent_name
            
            # Store decorator parent info
            elif capture == 'decorator_parent':
                parent_name = text
                # Find most recent decorator base to associate with
                if decorator_base:
                    most_recent = list(decorator_base.keys())[-1]
                    decorator_base[most_recent]['parent'] = parent_name
            
            # Store concrete decorator parent info
            elif capture == 'concrete_decorator_parent':
                parent_name = text
                # Find most recent concrete decorator to associate with
                if concrete_decorators:
                    most_recent = list(concrete_decorators.keys())[-1]
                    concrete_decorators[most_recent]['parent'] = parent_name
        
        # Convert to matches
        matches = []
        
        # Process component interface
        for class_name, info in components.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'component',
                'implementation': 'class-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process concrete components
        for class_name, info in concrete_components.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'concrete_component',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process decorator base class
        for class_name, info in decorator_base.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'decorator_base',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process concrete decorators
        for class_name, info in concrete_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'concrete_decorator',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process function decorators
        for function_name, info in function_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': function_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'function_decorator',
                'implementation': 'function-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process composition-based decorators
        for class_name, info in composition_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'composition_decorator',
                'implementation': 'composition-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        return matches


class DecoratorPatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Decorator design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Decorator pattern in JavaScript."""
        super().__init__(
            name="decorator_javascript",
            description="Identifies Decorator pattern implementation in JavaScript/TypeScript",
            languages=["javascript", "typescript"],
        )
        
        # Define the query for JavaScript decorator pattern
        self.queries = {
            'javascript': """
                ; Class-based Decorator pattern with Component interface
                
                ; Component class/interface
                (class_declaration
                  name: (identifier) @component_class
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @component_method
                      (#match? @component_method "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @component_method_body)))
                
                ; Concrete Component class extending the Component
                (class_declaration
                  name: (identifier) @concrete_component_class
                  superclass: (identifier) @component_parent
                  (#match? @component_parent "^Component$|^AbstractComponent$|^IComponent$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_component_method
                      (#match? @concrete_component_method "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @concrete_method_body)))
                
                ; Decorator base class
                (class_declaration
                  name: (identifier) @decorator_base_class
                  (#match? @decorator_base_class "^Decorator$|^AbstractDecorator$|^BaseDecorator$")
                  superclass: (identifier) @decorator_parent
                  (#match? @decorator_parent "^Component$|^AbstractComponent$|^IComponent$")
                  body: (class_body
                    ; Constructor storing the decorated component
                    (method_definition
                      name: (property_identifier) @constructor
                      (#eq? @constructor "constructor")
                      parameters: (formal_parameters
                        (identifier) @component_param)
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @component_attr
                              (#match? @component_attr "^_?component$|^_?decorated$|^_?wrapped"))
                            right: (identifier) @component_assign))))
                    
                    ; Operation method delegating to component
                    (method_definition
                      name: (property_identifier) @decorator_operation
                      (#match? @decorator_operation "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @component_attr2
                                (#match? @component_attr2 "^_?component$|^_?decorated$|^_?wrapped"))
                              property: (property_identifier) @delegate_method
                              (#match? @delegate_method "^operation$|^execute$|^run$|^perform$|^do$"))))))))
                
                ; Concrete decorator classes
                (class_declaration
                  name: (identifier) @concrete_decorator_class
                  superclass: (identifier) @concrete_decorator_parent
                  (#match? @concrete_decorator_parent "^Decorator$|^AbstractDecorator$|^BaseDecorator$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_decorator_operation
                      (#match? @concrete_decorator_operation "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @concrete_decorator_body)))
                      
                ; Function decorators (higher-order functions)
                (function_declaration
                  name: (identifier) @decorator_function
                  parameters: (formal_parameters
                    (identifier) @function_param
                    (#match? @function_param "^func$|^function$|^f$|^method$|^m$|^callable$|^wrapped$"))
                  body: (statement_block
                    (return_statement
                      (function) @wrapper_function
                      body: (statement_block
                        (expression_statement
                          (call_expression
                            function: (member_expression
                              object: (identifier) @original_function
                              (#match? @original_function "^func$|^function$|^f$|^method$|^m$|^callable$|^wrapped$")
                              property: (property_identifier) @apply_method
                              (#match? @apply_method "^apply$|^call$")))))))))
                
                ; Object composition (no inheritance) based decorator pattern
                (class_declaration
                  name: (identifier) @composition_decorator_class
                  body: (class_body
                    ; Constructor storing the decorated object
                    (method_definition
                      name: (property_identifier) @constructor
                      (#eq? @constructor "constructor")
                      parameters: (formal_parameters
                        (identifier) @processor_param
                        (#match? @processor_param "^processor$|^component$|^wrapped$|^decoratee$|^subject$"))
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @processor_attr
                              (#match? @processor_attr "^processor$|^component$|^wrapped$|^decoratee$|^subject$"))
                            right: (identifier) @processor_assign
                            (#match? @processor_assign "^processor$|^component$|^wrapped$|^decoratee$|^subject$")))))
                    
                    ; Method that enhances the wrapped object's method
                    (method_definition
                      name: (property_identifier) @processor_method
                      (#match? @processor_method "^process$|^execute$|^run$|^operate$|^apply$")
                      parameters: (formal_parameters
                        (identifier) @text_param)
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @processor_attr2
                                (#match? @processor_attr2 "^processor$|^component$|^wrapped$|^decoratee$|^subject$"))
                              property: (property_identifier) @processor_method2
                              (#match? @processor_method2 "^process$|^execute$|^run$|^operate$|^apply$"))
                            arguments: (arguments) @processor_args))))))
            """,
            'typescript': """
                ; Class-based Decorator pattern with Component interface
                
                ; Component interface
                (interface_declaration
                  name: (identifier) @component_interface
                  body: (interface_body
                    (method_signature
                      name: (property_identifier) @component_method
                      (#match? @component_method "^operation$|^execute$|^run$|^perform$|^do$"))))
                
                ; Component class/interface
                (class_declaration
                  name: (identifier) @component_class
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @component_method
                      (#match? @component_method "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @component_method_body)))
                
                ; Concrete Component class implementing the interface
                (class_declaration
                  name: (identifier) @concrete_component_class
                  implements: (implements_clause
                    (identifier) @component_interface_impl
                    (#match? @component_interface_impl "^Component$|^IComponent$"))
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_component_method
                      (#match? @concrete_component_method "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @concrete_method_body)))
                
                ; Concrete Component class extending the Component
                (class_declaration
                  name: (identifier) @concrete_component_class_extends
                  superclass: (identifier) @component_parent
                  (#match? @component_parent "^Component$|^AbstractComponent$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_component_method_ext
                      (#match? @concrete_component_method_ext "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @concrete_method_body_ext)))
                
                ; Decorator base class
                (class_declaration
                  name: (identifier) @decorator_base_class
                  (#match? @decorator_base_class "^Decorator$|^AbstractDecorator$|^BaseDecorator$")
                  implements: (implements_clause
                    (identifier) @decorator_interface_impl
                    (#match? @decorator_interface_impl "^Component$|^IComponent$"))
                  body: (class_body
                    ; Component property
                    (public_field_definition
                      name: (property_identifier) @component_field
                      (#match? @component_field "^_?component$|^_?decorated$|^_?wrapped"))
                    
                    ; Constructor storing the decorated component
                    (method_definition
                      name: (property_identifier) @constructor
                      (#eq? @constructor "constructor")
                      parameters: (formal_parameters
                        (required_parameter
                          pattern: (identifier) @component_param
                          (#match? @component_param "^component$|^decorated$|^wrapped$|^decoratee$")))
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @component_attr
                              (#match? @component_attr "^_?component$|^_?decorated$|^_?wrapped"))
                            right: (identifier) @component_assign))))
                    
                    ; Operation method delegating to component
                    (method_definition
                      name: (property_identifier) @decorator_operation
                      (#match? @decorator_operation "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @component_attr2
                                (#match? @component_attr2 "^_?component$|^_?decorated$|^_?wrapped"))
                              property: (property_identifier) @delegate_method
                              (#match? @delegate_method "^operation$|^execute$|^run$|^perform$|^do$"))))))))
                
                ; Concrete decorator classes
                (class_declaration
                  name: (identifier) @concrete_decorator_class
                  superclass: (identifier) @concrete_decorator_parent
                  (#match? @concrete_decorator_parent "^Decorator$|^AbstractDecorator$|^BaseDecorator$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_decorator_operation
                      (#match? @concrete_decorator_operation "^operation$|^execute$|^run$|^perform$|^do$")
                      body: (statement_block) @concrete_decorator_body)))
                
                ; TypeScript method decorator with decorator factory
                (lexical_declaration
                  (variable_declarator
                    name: (identifier) @ts_decorator_function
                    (#match? @ts_decorator_function "^[a-zA-Z]+Decorator$")
                    value: (function
                      parameters: (formal_parameters)
                      body: (statement_block
                        (return_statement
                          (lexical_declaration
                            (variable_declarator
                              name: (identifier) @descriptor_value
                              (#eq? @descriptor_value "descriptor")
                              value: (object
                                (method_definition
                                  name: (property_identifier) @value_prop
                                  (#eq? @value_prop "value")
                                  body: (statement_block)))))
                          )))))
            """
        }
        
    def _process_query_results(self, 
                             query_results: List[Dict], 
                             code: str, 
                             language: str,
                             file_path: Optional[str] = None,
                             parser=None) -> List[Dict]:
        """Process query results for Decorator pattern in JavaScript/TypeScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of decorator pattern matches with details
        """
        # Group captures by role in the pattern
        components = {}
        interfaces = {}
        concrete_components = {}
        decorator_base = {}
        concrete_decorators = {}
        function_decorators = {}
        composition_decorators = {}
        typescript_decorators = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Component class
            if capture == 'component_class':
                class_name = text
                if class_name not in components:
                    components[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'component',
                    }
            
            # TypeScript interface
            elif capture == 'component_interface':
                interface_name = text
                if interface_name not in interfaces:
                    interfaces[interface_name] = {
                        'name': interface_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'component_interface',
                    }
            
            # Concrete component
            elif capture in ('concrete_component_class', 'concrete_component_class_extends'):
                class_name = text
                if class_name not in concrete_components:
                    concrete_components[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_component',
                    }
            
            # Decorator base class
            elif capture == 'decorator_base_class':
                class_name = text
                if class_name not in decorator_base:
                    decorator_base[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'decorator_base',
                    }
            
            # Concrete decorator
            elif capture == 'concrete_decorator_class':
                class_name = text
                if class_name not in concrete_decorators:
                    concrete_decorators[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_decorator',
                    }
            
            # Function decorator
            elif capture == 'decorator_function':
                function_name = text
                if function_name not in function_decorators:
                    function_decorators[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'function_decorator',
                    }
            
            # Composition-based decorator
            elif capture == 'composition_decorator_class':
                class_name = text
                if class_name not in composition_decorators:
                    composition_decorators[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'composition_decorator',
                    }
            
            # TypeScript decorator
            elif capture == 'ts_decorator_function':
                decorator_name = text
                if decorator_name not in typescript_decorators:
                    typescript_decorators[decorator_name] = {
                        'name': decorator_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'typescript_decorator',
                    }
            
            # Store parent/implementation relationships
            elif capture in ('component_parent', 'decorator_parent', 'concrete_decorator_parent', 
                           'component_interface_impl', 'decorator_interface_impl'):
                parent_name = text
                # Associate with the appropriate element
                if capture == 'component_parent' and concrete_components:
                    most_recent = list(concrete_components.keys())[-1]
                    concrete_components[most_recent]['parent'] = parent_name
                elif capture == 'decorator_parent' and decorator_base:
                    most_recent = list(decorator_base.keys())[-1]
                    decorator_base[most_recent]['parent'] = parent_name
                elif capture == 'concrete_decorator_parent' and concrete_decorators:
                    most_recent = list(concrete_decorators.keys())[-1]
                    concrete_decorators[most_recent]['parent'] = parent_name
                elif capture == 'component_interface_impl' and concrete_components:
                    most_recent = list(concrete_components.keys())[-1]
                    concrete_components[most_recent]['implements'] = parent_name
                elif capture == 'decorator_interface_impl' and decorator_base:
                    most_recent = list(decorator_base.keys())[-1]
                    decorator_base[most_recent]['implements'] = parent_name
        
        # Convert to matches
        matches = []
        
        # Process component classes
        for class_name, info in components.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'component',
                'implementation': 'class-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process TypeScript interfaces
        for interface_name, info in interfaces.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': interface_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'component_interface',
                'implementation': 'interface-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process concrete components
        for class_name, info in concrete_components.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'concrete_component',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if 'implements' in info:
                match['implements'] = info['implements']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process decorator base class
        for class_name, info in decorator_base.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'decorator_base',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if 'implements' in info:
                match['implements'] = info['implements']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process concrete decorators
        for class_name, info in concrete_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'concrete_decorator',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process function decorators
        for function_name, info in function_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': function_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'function_decorator',
                'implementation': 'function-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process composition-based decorators
        for class_name, info in composition_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'composition_decorator',
                'implementation': 'composition-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process TypeScript decorators
        for decorator_name, info in typescript_decorators.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'decorator',
                'name': decorator_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'typescript_decorator',
                'implementation': 'typescript-decorator',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        return matches


class DecoratorPattern(CompositePattern):
    """A composite pattern that matches Decorator pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Decorator pattern."""
        super().__init__(
            name="decorator",
            description="Identifies Decorator pattern implementation across multiple languages",
            patterns=[
                DecoratorPatternPython(),
                DecoratorPatternJavaScript(),
            ],
        )


class StrategyPatternPython(QueryBasedPattern):
    """Pattern for detecting Strategy design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Strategy pattern in Python."""
        super().__init__(
            name="strategy_python",
            description="Identifies Strategy pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python strategy pattern
        self.queries = {
            'python': """
                ; Strategy interface/abstract class
                (class_definition
                  name: (identifier) @strategy_interface
                  body: (block
                    (function_definition
                      name: (identifier) @strategy_method
                      (#match? @strategy_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$")
                      parameters: (parameters) @strategy_params
                      body: (block) @strategy_method_body)))
                
                ; Concrete strategy implementation
                (class_definition
                  name: (identifier) @concrete_strategy
                  superclasses: (argument_list
                    (identifier) @strategy_parent
                    (#match? @strategy_parent "^[A-Za-z]*(Strategy|Algorithm|Processor|Handler|Formatter)$"))
                  body: (block
                    (function_definition
                      name: (identifier) @concrete_method
                      (#match? @concrete_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$")
                      parameters: (parameters) @concrete_params
                      body: (block) @concrete_method_body)))
                
                ; Context class that uses a strategy
                (class_definition
                  name: (identifier) @context_class
                  (#match? @context_class "^[A-Za-z]*(Context|Sorter|Processor|Calculator|Engine)$")
                  body: (block
                    ; Constructor that accepts a strategy
                    (function_definition
                      name: (identifier) @init_method
                      (#eq? @init_method "__init__")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @strategy_param
                        (#match? @strategy_param "^strategy$|^algorithm$|^processor$|^handler$|^sorter$|^formatter$"))
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @strategy_attr
                              (#match? @strategy_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?sorter$|^_?formatter$"))
                            right: (identifier) @strategy_assign))))
                    
                    ; Method that delegates to strategy
                    (function_definition
                      name: (identifier) @context_method
                      (#match? @context_method "^(execute|run|sort|calculate|process|do|handle|format)$")
                      parameters: (parameters) @context_params
                      body: (block
                        (return_statement
                          (call
                            function: (attribute
                              object: (attribute
                                object: (identifier) @self_ref2
                                attribute: (identifier) @strategy_attr2
                                (#match? @strategy_attr2 "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?sorter$|^_?formatter$"))
                              attribute: (identifier) @delegate_method
                              (#match? @delegate_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$"))
                            arguments: (argument_list) @delegate_args))))))
                
                ; Function-based strategies
                (function_definition
                  name: (identifier) @strategy_function
                  (#match? @strategy_function "^[a-z_]+(sort|algorithm|process|calculate|format)$")
                  parameters: (parameters
                    (identifier) @func_param
                    (#match? @func_param "^data$|^input$|^values$|^arr$|^items$|^text$"))
                  body: (block) @func_body)
                
                ; Context for function-based strategies
                (class_definition
                  name: (identifier) @functional_context
                  (#match? @functional_context "^[A-Za-z]*(Context|Processor|Calculator|Sorter|Formatter)$")
                  body: (block
                    ; Constructor that accepts a function strategy
                    (function_definition
                      name: (identifier) @func_init
                      (#eq? @func_init "__init__")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @func_strategy
                        (#match? @func_strategy "^strategy$|^algorithm$|^func$|^function$|^callback$|^handler$"))
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @func_attr
                              (#match? @func_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?func$|^_?callback$"))
                            right: (identifier) @func_assign))))
                    
                    ; Method that delegates to function strategy
                    (function_definition
                      name: (identifier) @func_context_method
                      (#match? @func_context_method "^(execute|sort|calculate|process|run|do|handle|format)$")
                      parameters: (parameters) @func_context_params
                      body: (block
                        (return_statement
                          (call
                            function: (attribute
                              object: (identifier) @self_ref3
                              attribute: (identifier) @func_attr2
                              (#match? @func_attr2 "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?func$|^_?callback$"))
                            arguments: (argument_list) @func_args))))))
                
                ; Dictionary-based strategies
                (class_definition
                  name: (identifier) @dict_context
                  (#match? @dict_context "^[A-Za-z]*(Processor|Handler|Calculator|Formatter)$")
                  body: (block
                    ; Dictionary of strategies
                    (expression_statement
                      (assignment
                        left: (identifier) @strategies_dict
                        (#match? @strategies_dict "^STRATEGIES$|^ALGORITHMS$|^HANDLERS$|^PROCESSORS$|^FORMATTERS$")
                        right: (dictionary) @strategies_dict_value))
                    
                    ; Constructor that selects a strategy by key
                    (function_definition
                      name: (identifier) @dict_init
                      (#eq? @dict_init "__init__")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @strategy_key
                        (#match? @strategy_key "^strategy$|^algorithm$|^key$|^method$|^type$"))
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @key_attr
                              (#match? @key_attr "^_?strategy$|^_?key$|^_?method$|^_?type$"))
                            right: (identifier) @key_assign))))
                    
                    ; Method that uses dictionary strategy
                    (function_definition
                      name: (identifier) @dict_method
                      (#match? @dict_method "^process|^calculate|^execute|^run|^handle|^do|^format")
                      parameters: (parameters) @dict_params
                      body: (block
                        (return_statement
                          (subscript
                            value: (attribute
                                  object: (identifier) @self_ref4
                                  attribute: (identifier) @strategies_attr
                                  (#match? @strategies_attr "^STRATEGIES$|^ALGORITHMS$|^HANDLERS$|^PROCESSORS$|^strategies$"))
                            subscript: (attribute
                                  object: (identifier) @self_ref5
                                  attribute: (identifier) @key_attr2
                                  (#match? @key_attr2 "^_?strategy$|^_?key$|^_?method$|^_?type$"))))))))
            """
        }
        
    def _process_query_results(self, 
                             query_results: List[Dict], 
                             code: str, 
                             language: str,
                             file_path: Optional[str] = None,
                             parser=None) -> List[Dict]:
        """Process query results for Strategy pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of strategy pattern matches with details
        """
        # Group captures by role in the pattern
        strategy_interfaces = {}
        concrete_strategies = {}
        contexts = {}
        function_strategies = {}
        functional_contexts = {}
        dict_contexts = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Strategy interface
            if capture == 'strategy_interface':
                class_name = text
                if class_name not in strategy_interfaces:
                    strategy_interfaces[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'strategy_interface',
                    }
            
            # Concrete strategy
            elif capture == 'concrete_strategy':
                class_name = text
                if class_name not in concrete_strategies:
                    concrete_strategies[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_strategy',
                    }
            
            # Context class
            elif capture == 'context_class':
                class_name = text
                if class_name not in contexts:
                    contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'context',
                    }
            
            # Function strategy
            elif capture == 'strategy_function':
                function_name = text
                if function_name not in function_strategies:
                    function_strategies[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'function_strategy',
                    }
            
            # Functional context
            elif capture == 'functional_context':
                class_name = text
                if class_name not in functional_contexts:
                    functional_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'functional_context',
                    }
            
            # Dictionary-based context
            elif capture == 'dict_context':
                class_name = text
                if class_name not in dict_contexts:
                    dict_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'dictionary_context',
                    }
            
            # Strategy parent info
            elif capture == 'strategy_parent':
                parent_name = text
                # Find most recent concrete strategy to associate with
                if concrete_strategies:
                    most_recent = list(concrete_strategies.keys())[-1]
                    concrete_strategies[most_recent]['parent'] = parent_name
        
        # Convert to matches
        matches = []
        
        # Process strategy interfaces
        for class_name, info in strategy_interfaces.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'strategy_interface',
                'implementation': 'class-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process concrete strategies
        for class_name, info in concrete_strategies.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'concrete_strategy',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process context classes
        for class_name, info in contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'context',
                'implementation': 'class-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process function strategies
        for function_name, info in function_strategies.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': function_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'function_strategy',
                'implementation': 'function-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process functional contexts
        for class_name, info in functional_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'functional_context',
                'implementation': 'function-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process dictionary-based contexts
        for class_name, info in dict_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'dictionary_context',
                'implementation': 'dictionary-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        return matches


class StrategyPatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Strategy design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Strategy pattern in JavaScript."""
        super().__init__(
            name="strategy_javascript",
            description="Identifies Strategy pattern implementation in JavaScript/TypeScript",
            languages=["javascript", "typescript"],
        )
        
        # Define the query for JavaScript strategy pattern
        self.queries = {
            'javascript': """
                ; Strategy interface/class
                (class_declaration
                  name: (identifier) @strategy_interface
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @strategy_method
                      (#match? @strategy_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$")
                      body: (statement_block) @strategy_method_body)))
                
                ; Concrete strategy implementation
                (class_declaration
                  name: (identifier) @concrete_strategy
                  superclass: (identifier) @strategy_parent
                  (#match? @strategy_parent "^[A-Za-z]*(Strategy|Algorithm|Processor|Handler|Formatter)$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_method
                      (#match? @concrete_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$")
                      body: (statement_block) @concrete_method_body)))
                
                ; Context class that uses a strategy
                (class_declaration
                  name: (identifier) @context_class
                  (#match? @context_class "^[A-Za-z]*(Context|Sorter|Processor|Calculator|Engine)$")
                  body: (class_body
                    ; Constructor that accepts a strategy
                    (method_definition
                      name: (property_identifier) @constructor
                      (#eq? @constructor "constructor")
                      parameters: (formal_parameters
                        (identifier) @strategy_param
                        (#match? @strategy_param "^strategy$|^algorithm$|^processor$|^handler$|^sorter$|^formatter$"))
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @strategy_attr
                              (#match? @strategy_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?sorter$|^_?formatter$"))
                            right: (identifier) @strategy_assign))))
                    
                    ; Method that delegates to strategy
                    (method_definition
                      name: (property_identifier) @context_method
                      (#match? @context_method "^(execute|run|sort|calculate|process|do|handle|format)$")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @strategy_attr2
                                (#match? @strategy_attr2 "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?sorter$|^_?formatter$"))
                              property: (property_identifier) @delegate_method
                              (#match? @delegate_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$"))
                            arguments: (arguments) @delegate_args))))))
                
                ; Function-based strategies
                (function_declaration
                  name: (identifier) @strategy_function
                  (#match? @strategy_function "^[a-z]+(Sort|Algorithm|Process|Calculate|Format)$")
                  parameters: (formal_parameters
                    (identifier) @func_param
                    (#match? @func_param "^data$|^input$|^values$|^arr$|^items$|^text$"))
                  body: (statement_block) @func_body)
                
                ; Context for function-based strategies
                (class_declaration
                  name: (identifier) @functional_context
                  (#match? @functional_context "^[A-Za-z]*(Context|Processor|Calculator|Sorter|Formatter)$")
                  body: (class_body
                    ; Constructor that accepts a function strategy
                    (method_definition
                      name: (property_identifier) @func_constructor
                      (#eq? @func_constructor "constructor")
                      parameters: (formal_parameters
                        (identifier) @func_strategy
                        (#match? @func_strategy "^strategy$|^algorithm$|^func$|^function$|^callback$|^handler$"))
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @func_attr
                              (#match? @func_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?func$|^_?callback$"))
                            right: (identifier) @func_assign))))
                    
                    ; Method that delegates to function strategy
                    (method_definition
                      name: (property_identifier) @func_context_method
                      (#match? @func_context_method "^(execute|sort|calculate|process|run|do|handle|format)$")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (this)
                              property: (property_identifier) @func_attr2
                              (#match? @func_attr2 "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?func$|^_?callback$"))
                            arguments: (arguments) @func_args))))))
                
                ; Object/dictionary-based strategies
                (class_declaration
                  name: (identifier) @dict_context
                  (#match? @dict_context "^[A-Za-z]*(Processor|Handler|Calculator|Formatter)$")
                  body: (class_body
                    ; Methods that return strategies object
                    (method_definition
                      name: (property_identifier) @strategies_getter
                      (#match? @strategies_getter "^(get)?[sS]trategies$|^(get)?[aA]lgorithms$|^(get)?[hH]andlers$|^(get)?[pP]rocessors$|^(get)?[fF]ormatters$")
                      body: (statement_block
                        (return_statement
                          (object) @strategies_object)))
                    
                    ; Method that uses object/dictionary strategy
                    (method_definition
                      name: (property_identifier) @dict_method
                      (#match? @dict_method "^process|^calculate|^execute|^run|^handle|^do|^format")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @strategies_obj)
                              property: (member_expression
                                object: (this)
                                property: (property_identifier) @strategy_key))
                            arguments: (arguments) @dict_args))))))
                
                ; Strategy with Dependency Injection
                (class_declaration
                  name: (identifier) @di_context
                  (#match? @di_context "^[A-Za-z]*(Generator|Builder|Creator|Processor)$")
                  body: (class_body
                    ; Constructor that accepts strategy object
                    (method_definition
                      name: (property_identifier) @di_constructor
                      (#eq? @di_constructor "constructor")
                      parameters: (formal_parameters
                        (identifier) @di_param
                        (#match? @di_param "^formatter$|^processor$|^handler$|^calculator$|^renderer$"))
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @di_attr
                              (#match? @di_attr "^formatter$|^processor$|^handler$|^calculator$|^renderer$"))
                            right: (identifier) @di_assign))))
                    
                    ; Method that uses injected strategy
                    (method_definition
                      name: (property_identifier) @di_method
                      (#match? @di_method "^generate|^build|^create|^process|^format|^render|^calculate$")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @di_obj)
                              property: (property_identifier) @di_obj_method)
                            arguments: (arguments) @di_args))))))
            """,
            'typescript': """
                ; Strategy interface
                (interface_declaration
                  name: (identifier) @strategy_interface
                  (#match? @strategy_interface "^[A-Za-z]*(Strategy|Algorithm|Processor|Handler|Formatter|Sorter)$")
                  body: (interface_body
                    (method_signature
                      name: (property_identifier) @strategy_method
                      (#match? @strategy_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$"))))
                
                ; Concrete strategy implementation with interface
                (class_declaration
                  name: (identifier) @concrete_strategy
                  implements: (implements_clause
                    (identifier) @strategy_interface_impl
                    (#match? @strategy_interface_impl "^[A-Za-z]*(Strategy|Algorithm|Processor|Handler|Formatter|Sorter)$"))
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @concrete_method
                      (#match? @concrete_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$")
                      body: (statement_block) @concrete_method_body)))
                
                ; Context class with typed strategy
                (class_declaration
                  name: (identifier) @typed_context
                  body: (class_body
                    ; Property with strategy interface type
                    (public_field_definition
                      name: (property_identifier) @strategy_field
                      (#match? @strategy_field "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?formatter$")
                      type: (type_annotation
                        (type_identifier) @strategy_type
                        (#match? @strategy_type "^[A-Za-z]*(Strategy|Algorithm|Processor|Handler|Formatter|Sorter)$")))
                    
                    ; Constructor with typed strategy parameter
                    (method_definition
                      name: (property_identifier) @ts_constructor
                      (#eq? @ts_constructor "constructor")
                      parameters: (formal_parameters
                        (required_parameter
                          name: (identifier) @ts_param
                          (#match? @ts_param "^strategy$|^algorithm$|^processor$|^handler$|^formatter$")
                          type: (type_annotation
                            (type_identifier) @ts_param_type
                            (#match? @ts_param_type "^[A-Za-z]*(Strategy|Algorithm|Processor|Handler|Formatter|Sorter)$"))))
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @ts_attr
                              (#match? @ts_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?formatter$"))
                            right: (identifier) @ts_assign))))
                    
                    ; Method that delegates to typed strategy
                    (method_definition
                      name: (property_identifier) @ts_method
                      (#match? @ts_method "^(execute|run|sort|calculate|process|do|handle|format)$")
                      body: (statement_block
                        (return_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @ts_strategy_attr
                                (#match? @ts_strategy_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$|^_?formatter$"))
                              property: (property_identifier) @ts_delegate_method
                              (#match? @ts_delegate_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$"))
                            arguments: (arguments) @ts_args))))))
            """
        }
        
    def _process_query_results(self, 
                             query_results: List[Dict], 
                             code: str, 
                             language: str,
                             file_path: Optional[str] = None,
                             parser=None) -> List[Dict]:
        """Process query results for Strategy pattern in JavaScript/TypeScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of strategy pattern matches with details
        """
        # Group captures by role in the pattern
        strategy_interfaces = {}
        concrete_strategies = {}
        contexts = {}
        function_strategies = {}
        functional_contexts = {}
        dict_contexts = {}
        di_contexts = {}
        typed_contexts = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Strategy interface/class
            if capture == 'strategy_interface':
                class_name = text
                if class_name not in strategy_interfaces:
                    strategy_interfaces[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'strategy_interface',
                    }
            
            # Concrete strategy
            elif capture == 'concrete_strategy':
                class_name = text
                if class_name not in concrete_strategies:
                    concrete_strategies[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_strategy',
                    }
            
            # Context class
            elif capture == 'context_class':
                class_name = text
                if class_name not in contexts:
                    contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'context',
                    }
            
            # Function strategy
            elif capture == 'strategy_function':
                function_name = text
                if function_name not in function_strategies:
                    function_strategies[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'function_strategy',
                    }
            
            # Functional context
            elif capture == 'functional_context':
                class_name = text
                if class_name not in functional_contexts:
                    functional_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'functional_context',
                    }
            
            # Dictionary-based context
            elif capture == 'dict_context':
                class_name = text
                if class_name not in dict_contexts:
                    dict_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'dictionary_context',
                    }
            
            # Dependency Injection context
            elif capture == 'di_context':
                class_name = text
                if class_name not in di_contexts:
                    di_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'di_context',
                    }
            
            # TypeScript typed context
            elif capture == 'typed_context':
                class_name = text
                if class_name not in typed_contexts:
                    typed_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'typed_context',
                    }
            
            # Inheritance/implementation relationships
            elif capture in ('strategy_parent', 'strategy_interface_impl', 'strategy_type', 'ts_param_type'):
                parent_name = text
                
                # Associate with appropriate element
                if capture == 'strategy_parent' and concrete_strategies:
                    most_recent = list(concrete_strategies.keys())[-1]
                    concrete_strategies[most_recent]['parent'] = parent_name
                elif capture == 'strategy_interface_impl' and concrete_strategies:
                    most_recent = list(concrete_strategies.keys())[-1]
                    concrete_strategies[most_recent]['implements'] = parent_name
                elif capture == 'strategy_type' and typed_contexts:
                    most_recent = list(typed_contexts.keys())[-1]
                    typed_contexts[most_recent]['strategy_type'] = parent_name
                elif capture == 'ts_param_type' and typed_contexts:
                    most_recent = list(typed_contexts.keys())[-1]
                    typed_contexts[most_recent]['param_type'] = parent_name
        
        # Convert to matches
        matches = []
        
        # Process strategy interfaces
        for class_name, info in strategy_interfaces.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'strategy_interface',
                'implementation': 'class-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process concrete strategies
        for class_name, info in concrete_strategies.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'concrete_strategy',
                'implementation': 'class-based',
            }
            
            if 'parent' in info:
                match['parent'] = info['parent']
            
            if 'implements' in info:
                match['implements'] = info['implements']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process context classes
        for class_name, info in contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'context',
                'implementation': 'class-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process function strategies
        for function_name, info in function_strategies.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': function_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'function_strategy',
                'implementation': 'function-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process functional contexts
        for class_name, info in functional_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'functional_context',
                'implementation': 'function-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process dictionary-based contexts
        for class_name, info in dict_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'dictionary_context',
                'implementation': 'dictionary-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process dependency injection contexts
        for class_name, info in di_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'di_context',
                'implementation': 'dependency-injection',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # Process TypeScript typed contexts
        for class_name, info in typed_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': language,
                'role': 'typed_context',
                'implementation': 'typed-interface',
            }
            
            if 'strategy_type' in info:
                match['strategy_type'] = info['strategy_type']
            
            if 'param_type' in info:
                match['param_type'] = info['param_type']
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        return matches


class StrategyPattern(CompositePattern):
    """A composite pattern that matches Strategy pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Strategy pattern."""
        super().__init__(
            name="strategy",
            description="Identifies Strategy pattern implementation across multiple languages",
            patterns=[
                StrategyPatternPython(),
                StrategyPatternJavaScript(),
            ],
        )


class CommandPatternPython(QueryBasedPattern):
    """Pattern for detecting Command design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Command pattern in Python."""
        super().__init__(
            name="command_python",
            description="Identifies Command pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python command pattern
        self.queries = {
            'python': """
                ; Abstract Command class
                (class_definition
                  name: (identifier) @command_interface
                  (#match? @command_interface "^Command$|^AbstractCommand$|^ICommand$")
                  body: (block
                    (function_definition
                      name: (identifier) @execute_method
                      (#match? @execute_method "^execute$|^run$|^do$|^call$"))))

                ; Concrete Command classes
                (class_definition
                  name: (identifier) @concrete_command
                  (#match? @concrete_command "Command$")
                  (argument_list
                    (identifier) @parent_class
                    (#match? @parent_class "^Command$|^AbstractCommand$|^ICommand$"))
                  body: (block
                    (function_definition
                      name: (identifier) @execute_impl
                      (#match? @execute_impl "^execute$|^run$|^do$|^call$")
                      body: (block
                        (expression_statement
                          (call
                            function: (attribute
                              object: (identifier) @receiver_ref)))))))

                ; Invoker class with command handling
                (class_definition
                  name: (identifier) @invoker
                  body: (block
                    (function_definition
                      parameters: (parameters
                        (parameter
                          (identifier) @param_name
                          (#match? @param_name "command")))
                      body: (block
                        (expression_statement
                          (call
                            function: (attribute
                              object: (identifier) @command_call
                              attribute: (identifier) @command_method
                              (#match? @command_method "^execute$|^run$|^do$|^call$"))))))))

                ; Command pattern with function-based commands
                (function_definition
                  name: (identifier) @function_command
                  (#match? @function_command "^create_.+command$|^make_.+command$")
                  body: (block
                    (return_statement
                      (call
                        function: (identifier) @command_class
                        (#match? @command_class "Command")))))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Command pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of command pattern matches with details
        """
        # Group captures by role in the pattern
        command_interfaces = {}
        concrete_commands = {}
        invokers = {}
        function_commands = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Command interface/abstract class
            if capture == 'command_interface':
                class_name = text
                if class_name not in command_interfaces:
                    command_interfaces[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'command_interface',
                    }
            
            # Concrete command class
            elif capture == 'concrete_command':
                class_name = text
                if class_name not in concrete_commands:
                    concrete_commands[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_command',
                    }
            
            # Invoker class
            elif capture == 'invoker':
                class_name = text
                if class_name not in invokers:
                    invokers[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'invoker',
                    }
            
            # Function-based command
            elif capture == 'function_command':
                function_name = text
                if function_name not in function_commands:
                    function_commands[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'function_command',
                    }
        
        # Combine all matches
        matches = []
        
        # Add command interfaces
        for name, interface in command_interfaces.items():
            matches.append(interface)
        
        # Add concrete commands
        for name, command in concrete_commands.items():
            matches.append(command)
        
        # Add invokers
        for name, invoker in invokers.items():
            matches.append(invoker)
        
        # Add function commands
        for name, func_command in function_commands.items():
            matches.append(func_command)
        
        return matches


class CommandPatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Command design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Command pattern in JavaScript."""
        super().__init__(
            name="command_javascript",
            description="Identifies Command pattern implementation in JavaScript",
            languages=["javascript"],
        )
        
        # Define the query for JavaScript command pattern
        self.queries = {
            'javascript': """
                ; Abstract Command class
                (class_declaration
                  name: (identifier) @command_interface
                  (#match? @command_interface "^Command$|^AbstractCommand$|^ICommand$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @execute_method
                      (#match? @execute_method "^execute$|^run$|^do$|^call$"))))

                ; Concrete Command classes
                (class_declaration
                  name: (identifier) @concrete_command
                  (#match? @concrete_command "Command$")
                  extends: (class_heritage
                    (identifier) @parent_class
                    (#match? @parent_class "^Command$|^AbstractCommand$|^ICommand$"))
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @execute_impl
                      (#match? @execute_impl "^execute$|^run$|^do$|^call$")
                      body: (statement_block
                        (expression_statement
                          (member_expression
                            object: (member_expression
                              object: (this))
                            property: (property_identifier) @receiver_ref))))))
                
                ; Invoker class with command handling
                (class_declaration
                  name: (identifier) @invoker
                  body: (class_body
                    (method_definition
                      parameters: (formal_parameters
                        (identifier) @param_name
                        (#match? @param_name "command"))
                      body: (statement_block
                        (expression_statement
                          (call_expression
                            function: (member_expression
                              object: (identifier) @command_call
                              property: (property_identifier) @command_method
                              (#match? @command_method "^execute$|^run$|^do$|^call$"))))))))
                
                ; Function-based Command Pattern
                (function_declaration
                  name: (identifier) @function_command
                  (#match? @function_command "^create.+Command$|^make.+Command$")
                  body: (statement_block
                    (return_statement
                      (new_expression
                        constructor: (identifier) @command_class
                        (#match? @command_class "Command")))))
                
                ; Object-based Command Pattern
                (variable_declaration
                  (variable_declarator
                    name: (identifier) @object_command
                    (#match? @object_command "Command$")
                    value: (object
                      (pair
                        property: (property_identifier) @command_method
                        (#match? @command_method "^execute$|^run$|^do$|^call$")))))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Command pattern in JavaScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of command pattern matches with details
        """
        # Group captures by role in the pattern
        command_interfaces = {}
        concrete_commands = {}
        invokers = {}
        function_commands = {}
        object_commands = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Command interface/abstract class
            if capture == 'command_interface':
                class_name = text
                if class_name not in command_interfaces:
                    command_interfaces[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'command_interface',
                    }
            
            # Concrete command class
            elif capture == 'concrete_command':
                class_name = text
                if class_name not in concrete_commands:
                    concrete_commands[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'concrete_command',
                    }
            
            # Invoker class
            elif capture == 'invoker':
                class_name = text
                if class_name not in invokers:
                    invokers[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'invoker',
                    }
            
            # Function-based command
            elif capture == 'function_command':
                function_name = text
                if function_name not in function_commands:
                    function_commands[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'function_command',
                    }
            
            # Object-based command
            elif capture == 'object_command':
                object_name = text
                if object_name not in object_commands:
                    object_commands[object_name] = {
                        'name': object_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'object_command',
                    }
        
        # Combine all matches
        matches = []
        
        # Add command interfaces
        for name, interface in command_interfaces.items():
            matches.append(interface)
        
        # Add concrete commands
        for name, command in concrete_commands.items():
            matches.append(command)
        
        # Add invokers
        for name, invoker in invokers.items():
            matches.append(invoker)
        
        # Add function commands
        for name, func_command in function_commands.items():
            matches.append(func_command)
        
        # Add object commands
        for name, obj_command in object_commands.items():
            matches.append(obj_command)
        
        return matches


class CommandPattern(CompositePattern):
    """A composite pattern that matches Command pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Command pattern."""
        super().__init__(
            name="command",
            description="Identifies Command pattern implementation across multiple languages",
            patterns=[
                CommandPatternPython(),
                CommandPatternJavaScript(),
            ],
        )


class AdapterPatternPython(QueryBasedPattern):
    """Pattern for detecting Adapter design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Adapter pattern in Python."""
        super().__init__(
            name="adapter_python",
            description="Identifies Adapter pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python adapter pattern
        self.queries = {
            'python': """
                ; Class Adapter Pattern (inheritance)
                (class_definition
                  name: (identifier) @adapter_class
                  (#match? @adapter_class "Adapter$")
                  (argument_list
                    (identifier) @target_class
                    (#match? @target_class "Target"))
                  body: (block
                    (function_definition
                      name: (identifier) @target_method
                      (#match? @target_method "^request$|^operation$")
                      body: (block
                        (expression_statement
                          (call
                            function: (attribute
                              object: (identifier) @object_ref
                              attribute: (identifier) @specific_method
                              (#match? @specific_method "^specific|legacy"))))))))

                ; Object Adapter Pattern (composition)
                (class_definition
                  name: (identifier) @object_adapter
                  (#match? @object_adapter "Adapter$")
                  (argument_list
                    (identifier) @target_class)
                  body: (block
                    (function_definition
                      name: (identifier) @init_method
                      (#eq? @init_method "__init__")
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @adaptee_attr
                              (#match? @adaptee_attr "^adaptee"))
                            right: (identifier) @adaptee_param))))
                    (function_definition
                      name: (identifier) @target_method
                      body: (block
                        (expression_statement
                          (call
                            function: (attribute
                              object: (attribute
                                object: (identifier) @self_ref
                                attribute: (identifier) @adaptee_ref
                                (#match? @adaptee_ref "^adaptee"))
                              attribute: (identifier) @adaptee_method)))))))
                            
                ; Function Adapter Pattern
                (function_definition
                  name: (identifier) @adapter_function
                  (#match? @adapter_function "^adapt|^wrapper")
                  parameters: (parameters
                    (parameter))
                  body: (block
                    (expression_statement
                      (assignment
                        left: (identifier) @result_var
                        right: (call
                          function: (identifier) @adaptee_function
                          (#not-match? @adaptee_function "^adapt|^wrapper"))))
                    (return_statement)))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Adapter pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of adapter pattern matches with details
        """
        # Group captures by role in the pattern
        adapter_classes = {}
        target_classes = {}
        adaptee_classes = {}
        adapter_functions = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Class adapter
            if capture == 'adapter_class':
                class_name = text
                if class_name not in adapter_classes:
                    adapter_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'adapter',
                        'type': 'class_adapter',
                    }
            
            # Object adapter
            elif capture == 'object_adapter':
                class_name = text
                if class_name not in adapter_classes:
                    adapter_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'adapter',
                        'type': 'object_adapter',
                    }
            
            # Target class
            elif capture == 'target_class':
                class_name = text
                if class_name not in target_classes:
                    target_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'target',
                    }
            
            # Adaptee class reference (through attribute)
            elif capture == 'adaptee_attr':
                attr_name = text
                # Use this to associate adaptee with adapter
                if result.get('self_ref'):
                    for adapter_name, adapter in adapter_classes.items():
                        if 'adaptee_attr' not in adapter:
                            adapter['adaptee_attr'] = attr_name
            
            # Function adapter
            elif capture == 'adapter_function':
                function_name = text
                if function_name not in adapter_functions:
                    adapter_functions[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'adapter',
                        'type': 'function_adapter',
                    }
            
            # Adaptee function (called by adapter function)
            elif capture == 'adaptee_function':
                function_name = text
                # Associate with the most recent adapter function
                for adapter_name, adapter in adapter_functions.items():
                    if 'adaptee_function' not in adapter:
                        adapter['adaptee_function'] = function_name
                        break
        
        # Combine all matches
        matches = []
        
        # Add adapter classes
        for name, adapter in adapter_classes.items():
            matches.append(adapter)
        
        # Add target classes
        for name, target in target_classes.items():
            matches.append(target)
        
        # Add adapter functions
        for name, func in adapter_functions.items():
            matches.append(func)
        
        return matches


class AdapterPatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Adapter design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Adapter pattern in JavaScript."""
        super().__init__(
            name="adapter_javascript",
            description="Identifies Adapter pattern implementation in JavaScript",
            languages=["javascript"],
        )
        
        # Define the query for JavaScript adapter pattern
        self.queries = {
            'javascript': """
                ; Class Adapter Pattern
                (class_declaration
                  name: (identifier) @adapter_class
                  (#match? @adapter_class "Adapter$")
                  extends: (class_heritage
                    (identifier) @target_class)
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @target_method
                      (#match? @target_method "^request$|^operation$")
                      body: (statement_block
                        (expression_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this))
                              property: (property_identifier) @adaptee_prop)))))))
                
                ; Object Adapter Pattern (composition)
                (class_declaration
                  name: (identifier) @object_adapter
                  (#match? @object_adapter "Adapter$")
                  body: (class_body
                    (method_definition
                      name: (property_identifier) @constructor
                      (#eq? @constructor "constructor")
                      parameters: (formal_parameters
                        (identifier) @adaptee_param)
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @adaptee_prop
                              (#match? @adaptee_prop "^adaptee"))
                            right: (identifier) @adaptee_ref))))
                    (method_definition
                      name: (property_identifier) @target_method
                      (#match? @target_method "^request$|^operation$")
                      body: (statement_block
                        (expression_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @adaptee_obj)
                              property: (property_identifier) @adaptee_method)))))))
                              
                ; Function Adapter Pattern
                (function_declaration
                  name: (identifier) @adapter_function
                  (#match? @adapter_function "^adapt|^wrapper")
                  body: (statement_block
                    (variable_declaration
                      (variable_declarator
                        name: (identifier) @result_var
                        value: (call_expression
                          function: (identifier) @adaptee_function)))
                    (return_statement)))
                    
                ; Object Literal Adapter Pattern
                (variable_declaration
                  (variable_declarator
                    name: (identifier) @object_adapter
                    (#match? @object_adapter "Adapter$|^adapter")
                    value: (object
                      (pair
                        property: (property_identifier) @method_name
                        value: (function
                          body: (statement_block
                            (expression_statement
                              (call_expression
                                function: (member_expression
                                  object: (identifier) @adaptee_obj
                                  property: (property_identifier) @adaptee_method)))))))))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Adapter pattern in JavaScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of adapter pattern matches with details
        """
        # Group captures by role in the pattern
        adapter_classes = {}
        object_adapters = {}
        target_classes = {}
        adapter_functions = {}
        object_literal_adapters = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Class adapter
            if capture == 'adapter_class':
                class_name = text
                if class_name not in adapter_classes:
                    adapter_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'adapter',
                        'type': 'class_adapter',
                    }
            
            # Object adapter
            elif capture == 'object_adapter':
                class_name = text
                if class_name not in object_adapters:
                    object_adapters[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'adapter',
                        'type': 'object_adapter',
                    }
            
            # Target class
            elif capture == 'target_class':
                class_name = text
                if class_name not in target_classes:
                    target_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'target',
                    }
            
            # Function adapter
            elif capture == 'adapter_function':
                function_name = text
                if function_name not in adapter_functions:
                    adapter_functions[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'adapter',
                        'type': 'function_adapter',
                    }
            
            # Adaptee function (called by adapter function)
            elif capture == 'adaptee_function':
                function_name = text
                # Associate with the most recent adapter function
                for adapter_name, adapter in adapter_functions.items():
                    if 'adaptee_function' not in adapter:
                        adapter['adaptee_function'] = function_name
                        break
        
        # Combine all matches
        matches = []
        
        # Add class adapters
        for name, adapter in adapter_classes.items():
            matches.append(adapter)
        
        # Add object adapters
        for name, adapter in object_adapters.items():
            matches.append(adapter)
        
        # Add target classes
        for name, target in target_classes.items():
            matches.append(target)
        
        # Add adapter functions
        for name, func in adapter_functions.items():
            matches.append(func)
        
        # Add object literal adapters
        for name, adapter in object_literal_adapters.items():
            matches.append(adapter)
        
        return matches


class AdapterPattern(CompositePattern):
    """A composite pattern that matches Adapter pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Adapter pattern."""
        super().__init__(
            name="adapter",
            description="Identifies Adapter pattern implementation across multiple languages",
            patterns=[
                AdapterPatternPython(),
                AdapterPatternJavaScript(),
            ],
        )


class FacadePatternPython(QueryBasedPattern):
    """Pattern for detecting Facade design pattern in Python."""
    
    def __init__(self):
        """Initialize a pattern for detecting Facade pattern in Python."""
        super().__init__(
            name="facade_python",
            description="Identifies Facade pattern implementation in Python",
            languages=["python"],
        )
        
        # Define the query for Python facade pattern
        self.queries = {
            'python': """
                ; Class-based Facade
                (class_definition
                  name: (identifier) @facade_class
                  (#match? @facade_class "Facade$|Service$")
                  body: (block
                    ; Constructor with multiple subsystem initializations
                    (function_definition
                      name: (identifier) @init_method
                      (#eq? @init_method "__init__")
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @subsystem_attr)))+))
                    
                    ; Facade method that uses multiple subsystems
                    (function_definition
                      name: (identifier) @facade_method
                      (#not-eq? @facade_method "__init__")
                      body: (block
                        (expression_statement
                          (call
                            function: (attribute
                              object: (attribute
                                object: (identifier) @self_ref
                                attribute: (identifier) @subsystem_ref)
                              attribute: (identifier) @subsystem_method)))+))))

                ; Function-based Facade
                (function_definition
                  name: (identifier) @facade_function
                  body: (block
                    ; Multiple calls to private/internal functions
                    (expression_statement
                      (assignment
                        left: (identifier) @result_var
                        right: (call
                          function: (identifier) @internal_function
                          (#match? @internal_function "^_"))))+
                    
                    ; Return the processed result
                    (return_statement)))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Facade pattern in Python.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of facade pattern matches with details
        """
        # Group captures by role in the pattern
        facade_classes = {}
        facade_methods = {}
        subsystems = {}
        facade_functions = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Facade class
            if capture == 'facade_class':
                class_name = text
                if class_name not in facade_classes:
                    facade_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade',
                        'type': 'class_facade',
                        'subsystems': set(),
                    }
            
            # Subsystem attribute reference
            elif capture == 'subsystem_attr':
                attr_name = text
                # Find the facade class this belongs to
                for result2 in query_results:
                    if result2['capture'] == 'facade_class':
                        facade_name = result2['text'].decode('utf-8') if isinstance(result2['text'], bytes) else str(result2['text'])
                        if facade_name in facade_classes:
                            facade_classes[facade_name]['subsystems'].add(attr_name)
                            break
            
            # Facade method
            elif capture == 'facade_method':
                method_name = text
                if method_name not in facade_methods:
                    facade_methods[method_name] = {
                        'name': method_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade_method',
                    }
            
            # Function-based facade
            elif capture == 'facade_function':
                function_name = text
                if function_name not in facade_functions:
                    facade_functions[function_name] = {
                        'name': function_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade',
                        'type': 'function_facade',
                        'internal_functions': set(),
                    }
            
            # Internal function called by facade function
            elif capture == 'internal_function':
                func_name = text
                # Find the facade function this belongs to
                for result2 in query_results:
                    if result2['capture'] == 'facade_function':
                        facade_name = result2['text'].decode('utf-8') if isinstance(result2['text'], bytes) else str(result2['text'])
                        if facade_name in facade_functions:
                            facade_functions[facade_name]['internal_functions'].add(func_name)
                            break
        
        # Combine all matches
        matches = []
        
        # Add facade classes
        for name, facade in facade_classes.items():
            # Convert set to list for serialization
            facade['subsystems'] = list(facade['subsystems'])
            matches.append(facade)
        
        # Add facade methods
        for name, method in facade_methods.items():
            matches.append(method)
        
        # Add facade functions
        for name, func in facade_functions.items():
            # Convert set to list for serialization
            func['internal_functions'] = list(func['internal_functions'])
            matches.append(func)
        
        return matches


class FacadePatternJavaScript(QueryBasedPattern):
    """Pattern for detecting Facade design pattern in JavaScript."""
    
    def __init__(self):
        """Initialize a pattern for detecting Facade pattern in JavaScript."""
        super().__init__(
            name="facade_javascript",
            description="Identifies Facade pattern implementation in JavaScript",
            languages=["javascript"],
        )
        
        # Define the query for JavaScript facade pattern
        self.queries = {
            'javascript': """
                ; Class-based Facade
                (class_declaration
                  name: (identifier) @facade_class
                  (#match? @facade_class "Facade$|Service$")
                  body: (class_body
                    ; Constructor with multiple subsystem initializations
                    (method_definition
                      name: (property_identifier) @constructor
                      (#eq? @constructor "constructor")
                      body: (statement_block
                        (expression_statement
                          (assignment_expression
                            left: (member_expression
                              object: (this)
                              property: (property_identifier) @subsystem_attr)))+))
                    
                    ; Facade method that uses multiple subsystems
                    (method_definition
                      name: (property_identifier) @facade_method
                      (#not-eq? @facade_method "constructor")
                      body: (statement_block
                        (expression_statement
                          (call_expression
                            function: (member_expression
                              object: (member_expression
                                object: (this)
                                property: (property_identifier) @subsystem_ref)
                              property: (property_identifier) @subsystem_method)))+))))

                ; Object Literal Facade
                (variable_declaration
                  (variable_declarator
                    name: (identifier) @object_facade
                    (#match? @object_facade "Facade$|Service$")
                    value: (object
                      (pair
                        property: (property_identifier) @facade_method
                        value: (function
                          body: (statement_block
                            (expression_statement
                              (call_expression
                                function: (member_expression
                                  object: (identifier) @subsystem_object
                                  property: (property_identifier) @subsystem_method))))+))+)))

                ; Module Facade (ES6 style)
                (export_statement
                  (object
                    (pair
                      property: (property_identifier) @facade_export
                      value: (function
                        body: (statement_block
                          (expression_statement
                            (call_expression
                              function: (member_expression
                                object: (identifier) @internal_module
                                property: (property_identifier) @internal_function)))+)))))
            """
        }
        
    def _process_query_results(self, 
                               query_results: List[Dict], 
                               code: str, 
                               language: str,
                               file_path: Optional[str] = None,
                               parser=None) -> List[Dict]:
        """Process query results for Facade pattern in JavaScript.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of facade pattern matches with details
        """
        # Group captures by role in the pattern
        facade_classes = {}
        object_facades = {}
        facade_methods = {}
        subsystems = set()
        module_facades = {}
        
        for result in query_results:
            capture = result['capture']
            node = result['node']
            text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
            
            # Class-based facade
            if capture == 'facade_class':
                class_name = text
                if class_name not in facade_classes:
                    facade_classes[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade',
                        'type': 'class_facade',
                        'subsystems': set(),
                    }
            
            # Object literal facade
            elif capture == 'object_facade':
                object_name = text
                if object_name not in object_facades:
                    object_facades[object_name] = {
                        'name': object_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade',
                        'type': 'object_facade',
                        'subsystems': set(),
                    }
            
            # Subsystem attribute
            elif capture == 'subsystem_attr':
                subsystems.add(text)
                # Find the facade class this belongs to
                for result2 in query_results:
                    if result2['capture'] == 'facade_class':
                        facade_name = result2['text'].decode('utf-8') if isinstance(result2['text'], bytes) else str(result2['text'])
                        if facade_name in facade_classes:
                            facade_classes[facade_name]['subsystems'].add(text)
                            break
            
            # Subsystem object reference
            elif capture == 'subsystem_object':
                subsystems.add(text)
                # Find the object facade this belongs to
                for result2 in query_results:
                    if result2['capture'] == 'object_facade':
                        facade_name = result2['text'].decode('utf-8') if isinstance(result2['text'], bytes) else str(result2['text'])
                        if facade_name in object_facades:
                            object_facades[facade_name]['subsystems'].add(text)
                            break
            
            # Facade method
            elif capture == 'facade_method':
                method_name = text
                if method_name not in facade_methods:
                    facade_methods[method_name] = {
                        'name': method_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade_method',
                    }
            
            # Module facade export
            elif capture == 'facade_export':
                export_name = text
                if export_name not in module_facades:
                    module_facades[export_name] = {
                        'name': export_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'facade',
                        'type': 'module_facade',
                        'subsystems': set(),
                    }
            
            # Internal module reference for module facade
            elif capture == 'internal_module':
                module_name = text
                subsystems.add(module_name)
                # Find the module facade this belongs to
                for result2 in query_results:
                    if result2['capture'] == 'facade_export':
                        facade_name = result2['text'].decode('utf-8') if isinstance(result2['text'], bytes) else str(result2['text'])
                        if facade_name in module_facades:
                            module_facades[facade_name]['subsystems'].add(module_name)
                            break
        
        # Combine all matches
        matches = []
        
        # Add class facades
        for name, facade in facade_classes.items():
            # Convert set to list for serialization
            facade['subsystems'] = list(facade['subsystems'])
            matches.append(facade)
        
        # Add object literal facades
        for name, facade in object_facades.items():
            # Convert set to list for serialization
            facade['subsystems'] = list(facade['subsystems'])
            matches.append(facade)
        
        # Add module facades
        for name, facade in module_facades.items():
            # Convert set to list for serialization
            facade['subsystems'] = list(facade['subsystems'])
            matches.append(facade)
        
        # Add facade methods
        for name, method in facade_methods.items():
            matches.append(method)
        
        return matches


class FacadePattern(CompositePattern):
    """A composite pattern that matches Facade pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting Facade pattern."""
        super().__init__(
            name="facade",
            description="Identifies Facade pattern implementation across multiple languages",
            patterns=[
                FacadePatternPython(),
                FacadePatternJavaScript(),
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
                ObserverPattern(),
                DecoratorPattern(),
                StrategyPattern(),
                CommandPattern(),
                AdapterPattern(),
                FacadePattern(),
            ],
        )