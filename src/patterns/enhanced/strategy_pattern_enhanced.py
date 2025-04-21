"""
Enhanced Strategy Pattern detector implementation.

This file contains enhanced implementations of Strategy pattern detectors for Python and JavaScript,
including repository-based strategy implementations detection.
"""

from typing import Dict, List, Optional

from ...pattern_base import CompositePattern, QueryBasedPattern


class StrategyPatternPythonEnhanced(QueryBasedPattern):
    """Enhanced Pattern for detecting Strategy design pattern in Python."""
    
    def __init__(self):
        """Initialize an enhanced pattern for detecting Strategy pattern in Python."""
        super().__init__(
            name="strategy_python_enhanced",
            description="Identifies Strategy pattern implementation in Python with enhanced detection",
            languages=["python"],
        )
        
        # Define the query for Python strategy pattern with repository pattern detection
        self.queries = {
            'python': """
                ; ---- Standard Strategy Pattern Detection (from original) ----
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

                ; ---- NEW: Repository-based Strategy Pattern Detection ----
                
                ; Strategy repository class
                (class_definition
                  name: (identifier) @repository_class
                  (#match? @repository_class "^[A-Za-z]*(Repository|Registry|Factory|Provider|Manager)$")
                  body: (block
                    ; Dictionary of strategies
                    (expression_statement
                      (assignment
                        left: (attribute
                          object: (identifier) @cls_ref
                          (#eq? @cls_ref "cls")
                          attribute: (identifier) @strategies_repo
                          (#match? @strategies_repo "^_?strategies$|^_?registry$|^_?algorithms$|^_?handlers$"))
                        right: (dictionary) @repo_dict_value))
                    
                    ; Register method for adding strategies to repository
                    (function_definition
                      decorator: (decorator
                        (identifier) @register_decorator
                        (#match? @register_decorator "^classmethod$"))
                      name: (identifier) @register_method
                      (#match? @register_method "^register$|^add_strategy$|^register_strategy$|^add$")
                      parameters: (parameters
                        (identifier) @cls_param
                        (#eq? @cls_param "cls")
                        (identifier) @key_param
                        (identifier) @strategy_impl_param)
                      body: (block
                        (expression_statement
                          (assignment
                            left: (subscript
                              value: (attribute
                                object: (identifier) @cls_ref2
                                (#eq? @cls_ref2 "cls")
                                attribute: (identifier) @strategies_repo2
                                (#match? @strategies_repo2 "^_?strategies$|^_?registry$|^_?algorithms$|^_?handlers$"))
                              subscript: (identifier) @key_ref)
                            right: (identifier) @strategy_impl_ref))))
                    
                    ; Get method for retrieving strategies from repository
                    (function_definition
                      decorator: (decorator
                        (identifier) @get_decorator
                        (#match? @get_decorator "^classmethod$"))
                      name: (identifier) @get_method
                      (#match? @get_method "^get$|^get_strategy$|^create$|^get_instance$|^create_strategy$")
                      parameters: (parameters
                        (identifier) @cls_param2
                        (#eq? @cls_param2 "cls")
                        (identifier) @key_param2)
                      body: (block
                        (return_statement
                          (subscript
                            value: (attribute
                              object: (identifier) @cls_ref3
                              (#eq? @cls_ref3 "cls")
                              attribute: (identifier) @strategies_repo3
                              (#match? @strategies_repo3 "^_?strategies$|^_?registry$|^_?algorithms$|^_?handlers$"))
                            subscript: (identifier) @key_ref2))))))
                
                ; Context that uses strategy repository
                (class_definition
                  name: (identifier) @repo_context_class
                  (#match? @repo_context_class "^[A-Za-z]*(Context|Processor|Handler|Executor|Sorter)$")
                  body: (block
                    ; Constructor that accepts a strategy key/type
                    (function_definition
                      name: (identifier) @repo_init_method
                      (#eq? @repo_init_method "__init__")
                      parameters: (parameters
                        (identifier) @self_param
                        (identifier) @strategy_type_param
                        (#match? @strategy_type_param "^strategy_type$|^strategy_key$|^algorithm_type$|^processor_type$"))
                      body: (block
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @strategy_type_attr
                              (#match? @strategy_type_attr "^_?strategy_type$|^_?strategy_key$|^_?algorithm_type$|^_?processor_type$"))
                            right: (identifier) @strategy_type_assign))
                        (expression_statement
                          (assignment
                            left: (attribute
                              object: (identifier) @self_ref
                              attribute: (identifier) @strategy_attr
                              (#match? @strategy_attr "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$"))
                            right: (call
                              function: (attribute
                                object: (identifier) @repo_ref
                                (#match? @repo_ref "^[A-Za-z]*(Repository|Registry|Factory|Provider|Manager)$")
                                attribute: (identifier) @get_strategy_method
                                (#match? @get_strategy_method "^get$|^get_strategy$|^create$|^get_instance$|^create_strategy$"))
                              arguments: (argument_list
                                (identifier) @strategy_key_arg))))))
                    
                    ; Method that delegates to strategy from repository
                    (function_definition
                      name: (identifier) @repo_context_method
                      (#match? @repo_context_method "^(execute|run|sort|calculate|process|do|handle|format)$")
                      parameters: (parameters) @repo_context_params
                      body: (block
                        (return_statement
                          (call
                            function: (attribute
                              object: (attribute
                                object: (identifier) @self_ref2
                                attribute: (identifier) @strategy_attr2
                                (#match? @strategy_attr2 "^_?strategy$|^_?algorithm$|^_?processor$|^_?handler$"))
                              attribute: (identifier) @delegate_method
                              (#match? @delegate_method "^(algorithm|execute|sort|calculate|process|do|run|handle|format)$"))
                            arguments: (argument_list) @delegate_args))))))
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
        
        # NEW: Repository pattern components
        repositories = {}
        repo_contexts = {}
        
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
            
            # NEW: Strategy Repository
            elif capture == 'repository_class':
                class_name = text
                if class_name not in repositories:
                    repositories[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'strategy_repository',
                    }
            
            # NEW: Repository Context
            elif capture == 'repo_context_class':
                class_name = text
                if class_name not in repo_contexts:
                    repo_contexts[class_name] = {
                        'name': class_name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'role': 'repository_context',
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
        
        # NEW: Process repository classes
        for class_name, info in repositories.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'strategy_repository',
                'implementation': 'repository-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        # NEW: Process repository contexts
        for class_name, info in repo_contexts.items():
            match = {
                'type': 'design_pattern',
                'pattern': 'strategy',
                'name': class_name,
                'line': info['line'],
                'column': info['column'],
                'language': 'python',
                'role': 'repository_context',
                'implementation': 'repository-based',
            }
            
            if file_path:
                match['file'] = file_path
                
            matches.append(match)
        
        return matches


class StrategyPatternEnhanced(CompositePattern):
    """A composite pattern that matches enhanced Strategy pattern in multiple languages."""
    
    def __init__(self):
        """Initialize a composite pattern for detecting enhanced Strategy pattern."""
        super().__init__(
            name="strategy_enhanced",
            description="Identifies Strategy pattern implementation across multiple languages with enhanced detection",
            patterns=[
                StrategyPatternPythonEnhanced(),
                # Add JavaScript enhanced pattern when implemented
            ],
        )