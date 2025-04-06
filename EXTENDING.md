# Extending the Code Pattern Analyzer

This document explains how to add new pattern recognition capabilities to the analyzer.

## Adding a New Pattern

To add a new pattern to the analyzer, follow these steps:

1. Create a new pattern class in `src/patterns/`
2. Register the pattern with the PatternRecognizer
3. Create tree-sitter queries for your pattern

### Step 1: Create a Pattern Class

Create a new class that inherits from `Pattern` in a file like `src/patterns/my_pattern.py`:

```python
from typing import Dict, List
from ..pattern_recognizer import Pattern

class MyNewPattern(Pattern):
    """Pattern for recognizing [your pattern description]."""
    
    def __init__(self):
        super().__init__(
            name="my_new_pattern",
            description="Identifies [your pattern] in code"
        )
    
    def match(self, ast) -> List[Dict]:
        """Find [your pattern] in the AST."""
        # Implement your pattern matching logic here
        # Use tree-sitter queries to match patterns in the AST
        
        # Example:
        # query = "your tree-sitter query here"
        # matches = run_query(ast, query)
        
        # Format the results
        results = []
        # For each match, add details to results
        
        return results
```

### Step 2: Register the Pattern

In `src/pattern_recognizer.py`, import your new pattern and add it to the patterns dictionary:

```python
from .patterns.my_pattern import MyNewPattern

class PatternRecognizer:
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {
            "function_definition": FunctionDefinitionPattern(),
            "class_definition": ClassDefinitionPattern(),
            "my_new_pattern": MyNewPattern(),  # Add your pattern here
        }
```

### Step 3: Create Tree-Sitter Queries

Define tree-sitter queries for each supported language in your pattern class. These queries are the heart of pattern matching.

For example, to detect constructors:

```python
PYTHON_CONSTRUCTOR_QUERY = """
(class_definition
  body: (block 
    (function_definition
      name: (identifier) @method_name
      (#eq? @method_name "__init__"))))
"""

JAVASCRIPT_CONSTRUCTOR_QUERY = """
(class_declaration
  body: (class_body
    (method_definition
      name: (property_identifier) @method_name
      (#eq? @method_name "constructor"))))
"""
```

## Advanced Pattern Features

To create more sophisticated patterns:

1. **Pattern Composition**: Combine simpler patterns to build complex ones
2. **Context-Aware Matching**: Consider the surrounding code context
3. **Cross-File Analysis**: Analyze relationships between files
4. **Transformation Suggestions**: Provide suggestions for transforming detected patterns

## Example: Detecting Factory Methods

Here's a simplified example of how to detect factory method patterns:

```python
class FactoryMethodPattern(Pattern):
    """Pattern for recognizing factory methods."""
    
    def __init__(self):
        super().__init__(
            name="factory_method",
            description="Identifies factory methods in code"
        )
    
    def match(self, ast) -> List[Dict]:
        """Find factory methods in the AST."""
        # Query for methods that create and return objects
        results = []
        
        # This is simplified; real implementation would use tree-sitter
        # to identify methods that:
        # 1. Create new instances of objects
        # 2. Return those instances
        # 3. Are often static or class methods
        
        return results
```