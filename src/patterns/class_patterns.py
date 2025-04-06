"""
Patterns for detecting classes and class-related structures.
"""

from typing import Dict, List, Optional, Union

import tree_sitter

from ..pattern_base import QueryBasedPattern, CompositePattern


class ClassDefinitionPattern(QueryBasedPattern):
    """Pattern for detecting class definitions."""
    
    def __init__(self):
        """Initialize a pattern for detecting class definitions."""
        super().__init__(
            name="class_definition",
            description="Identifies class definitions in code",
            languages=["python", "javascript", "typescript", "ruby", "java", "cpp", "rust"],
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                (class_definition
                  name: (identifier) @name
                  body: (block) @body)
            """,
            'javascript': """
                (class_declaration
                  name: (identifier) @name
                  body: (class_body) @body)
                
                (class_expression
                  name: (identifier) @name
                  body: (class_body) @body)
            """,
            'typescript': """
                (class_declaration
                  name: (identifier) @name
                  body: (class_body) @body)
                
                (class_expression
                  name: (identifier) @name
                  body: (class_body) @body)
            """,
            'ruby': """
                (class
                  name: (constant) @name
                  body: (body_statement) @body)
            """,
            'java': """
                (class_declaration
                  name: (identifier) @name
                  body: (class_body) @body)
            """,
            'cpp': """
                (class_specifier
                  name: (type_identifier) @name
                  body: (field_declaration_list) @body)
                
                (struct_specifier
                  name: (type_identifier) @name
                  body: (field_declaration_list) @body)
            """,
            'rust': """
                (struct_item
                  name: (type_identifier) @name
                  body: (field_declaration_list) @body)
                
                (impl_item
                  trait: (type_identifier) @trait
                  type: (type_identifier) @name
                  body: (block) @body)
            """,
        }
        
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results for class definitions.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of class matches with details
        """
        # Use the generic implementation as a starting point
        matches = super()._process_query_results(query_results, code, language, file_path, parser)
        
        # Extract additional information
        for match in matches:
            # Set the match type specifically
            match['type'] = 'class'
            
            # Handle special cases for Rust impl blocks
            if language == 'rust' and 'trait' in match:
                match['trait'] = match['trait']['text']
                match['is_impl'] = True
        
        return matches


class InterfaceDefinitionPattern(QueryBasedPattern):
    """Pattern for detecting interface definitions."""
    
    def __init__(self):
        """Initialize a pattern for detecting interface definitions."""
        super().__init__(
            name="interface_definition",
            description="Identifies interface definitions in code",
            languages=["typescript", "java"],
        )
        
        # Define language-specific queries
        self.queries = {
            'typescript': """
                (interface_declaration
                  name: (type_identifier) @name
                  body: (object_type) @body)
            """,
            'java': """
                (interface_declaration
                  name: (identifier) @name
                  body: (interface_body) @body)
            """,
        }
        
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results for interface definitions.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of interface matches with details
        """
        # Use the generic implementation as a starting point
        matches = super()._process_query_results(query_results, code, language, file_path, parser)
        
        # Extract additional information
        for match in matches:
            # Set the match type specifically
            match['type'] = 'interface'
        
        return matches


class ClassWithInheritancePattern(QueryBasedPattern):
    """Pattern for detecting classes with inheritance."""
    
    def __init__(self):
        """Initialize a pattern for detecting classes with inheritance."""
        super().__init__(
            name="class_inheritance",
            description="Identifies classes that inherit from other classes",
            languages=["python", "javascript", "typescript", "ruby", "java", "cpp"],
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                (class_definition
                  name: (identifier) @name
                  superclasses: (argument_list
                    (identifier) @parent)
                  body: (block) @body)
            """,
            'javascript': """
                (class_declaration
                  name: (identifier) @name
                  extends: (extends_clause
                    (identifier) @parent)
                  body: (class_body) @body)
            """,
            'typescript': """
                (class_declaration
                  name: (identifier) @name
                  extends: (extends_clause
                    (identifier) @parent)
                  body: (class_body) @body)
            """,
            'ruby': """
                (class
                  name: (constant) @name
                  superclass: (constant) @parent
                  body: (body_statement) @body)
            """,
            'java': """
                (class_declaration
                  name: (identifier) @name
                  extends: (extends_clause
                    (type_identifier) @parent)
                  body: (class_body) @body)
            """,
            'cpp': """
                (class_specifier
                  name: (type_identifier) @name
                  base_class_clause: (base_class_clause
                    (type_identifier) @parent)
                  body: (field_declaration_list) @body)
            """,
        }
        
    def _process_query_results(self, 
                              query_results: List[Dict], 
                              code: str, 
                              language: str,
                              file_path: Optional[str] = None,
                              parser=None) -> List[Dict]:
        """Process query results for classes with inheritance.
        
        Args:
            query_results: Results from running a tree-sitter query
            code: The source code that was parsed
            language: The language of the source code
            file_path: Optional path to the file that was parsed
            parser: Optional CodeParser instance
            
        Returns:
            A list of class inheritance matches with details
        """
        # Use the generic implementation as a starting point
        matches = super()._process_query_results(query_results, code, language, file_path, parser)
        
        # Extract additional information
        for match in matches:
            # Set the match type specifically
            match['type'] = 'class_inheritance'
            
            # Extract parent class information
            if 'parent' in match:
                match['parent_class'] = match['parent']['text']
        
        return matches


class AllClassPatternsPattern(CompositePattern):
    """A composite pattern that matches all class-related patterns."""
    
    def __init__(self):
        """Initialize a pattern for detecting all class-related structures."""
        super().__init__(
            name="all_classes",
            description="Identifies all class-related structures (classes, interfaces, inheritance)",
            patterns=[
                ClassDefinitionPattern(),
                InterfaceDefinitionPattern(),
                ClassWithInheritancePattern(),
            ],
        )