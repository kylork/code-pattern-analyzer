# Refactoring Suggestions Module

The refactoring suggestions module provides automated identification of potential code improvements in your codebase. By analyzing your code's structure, complexity, flow, and patterns, it generates actionable recommendations to enhance maintainability, readability, and adherence to design best practices.

## Overview

The refactoring suggestions feature analyzes your codebase from multiple angles:

- **Complexity Analysis**: Identifies functions with high cyclomatic or cognitive complexity that would benefit from simplification
- **Flow Analysis**: Detects issues in control flow (dead code, potential infinite loops) and data flow (unused variables, uninitialized variables)
- **Pattern Opportunities**: Recognizes code that could benefit from design pattern implementation
- **Architectural Analysis**: Finds architectural issues like dependency cycles and anti-patterns

Each suggestion includes a description, impact level, location information, and potential benefits of applying the refactoring.

## Installation and Setup

### Requirements

The refactoring module is part of the Code Pattern Analyzer package. Make sure you have installed all the dependencies:

```bash
pip install -r requirements.txt
```

### Setup

No additional setup is required if you've already installed the Code Pattern Analyzer package.

## Command-line Usage

The refactoring suggestions module can be used in several ways:

### 1. Using the dedicated script

```bash
python run_refactoring_suggestions.py /path/to/your/code -o output.html -f html
```

Options:
- `-o, --output`: Output file for the report (default: refactoring_suggestions.html)
- `-f, --format`: Output format (choices: html, json, text; default: html)
- `--log-level`: Set the logging level (choices: DEBUG, INFO, WARNING, ERROR, CRITICAL; default: INFO)

### 2. Using the refactoring CLI commands

```bash
# Generate suggestions
python -m src.cli refactoring suggest /path/to/your/code --output suggestions.html --format html --analysis-type all --min-impact low

# Interactive analysis
python -m src.cli refactoring analyze /path/to/your/code --suggested-only
```

Options for `suggest` command:
- `--output, -o`: Output file for the report
- `--format, -f`: Output format (html, json, text)
- `--analysis-type, -a`: Type of analysis to perform (all, pattern, complexity, flow, architectural)
- `--min-impact`: Minimum impact level to include (low, medium, high, critical)

## Refactoring Types

The module supports various types of refactoring suggestions:

| Type | Description |
|------|-------------|
| `EXTRACT_METHOD` | Split a complex method into smaller, more manageable pieces |
| `EXTRACT_CLASS` | Move related functionality into a separate class |
| `INLINE_METHOD` | Incorporate a simple method's body into its call site |
| `RENAME` | Improve naming for better clarity |
| `MOVE` | Relocate functionality to a more appropriate place |
| `PULL_UP` | Move shared functionality to a parent class |
| `PUSH_DOWN` | Move specialized functionality to subclasses |
| `ENCAPSULATE_FIELD` | Add accessor methods for fields |
| `REPLACE_CONDITIONAL_WITH_POLYMORPHISM` | Replace complex conditionals with polymorphic objects |
| `INTRODUCE_PARAMETER_OBJECT` | Group related parameters into a single object |
| `INTRODUCE_NULL_OBJECT` | Replace null checks with a null object pattern |
| `FACTORY_METHOD` | Implement the Factory Method pattern |
| `STRATEGY` | Implement the Strategy pattern |
| `OBSERVER` | Implement the Observer pattern |
| `DECORATOR` | Implement the Decorator pattern |
| `SINGLETON` | Implement the Singleton pattern |
| `ARCHITECTURAL` | Address architectural issues |
| `CUSTOM` | Other custom refactorings |

## Impact Levels

Suggestions are categorized by their impact level:

| Level | Description |
|-------|-------------|
| `CRITICAL` | Issues that could cause serious problems; should be addressed immediately |
| `HIGH` | Significant issues that should be addressed soon |
| `MEDIUM` | Moderate issues that would improve code quality |
| `LOW` | Minor issues that would slightly improve code quality |

The impact level is determined based on factors such as:
- The severity of the issue
- Potential for bugs or runtime errors
- Effect on maintainability
- Impact on code readability
- Confidence in the suggestion

## Example Outputs

### HTML Report

The HTML report provides an interactive view of all suggestions with filtering capabilities:
- Filter by impact level (Critical, High, Medium, Low)
- Filter by refactoring type
- View code examples before and after refactoring (when available)
- See benefits for each suggestion

![HTML Report Example](../../docs/images/refactoring_html_report.png) <!-- Note: this image doesn't exist yet, just a placeholder -->

### JSON Output

JSON output is useful for integrating with other tools:

```json
[
  {
    "refactoring_type": "extract_method",
    "description": "Extract methods from complex function 'process_data'",
    "file_path": "/path/to/file.py",
    "line_range": [45, 67],
    "impact": "high",
    "source": "complexity_metrics",
    "details": {
      "function_name": "process_data",
      "complexity": 25,
      "threshold": 20
    },
    "benefits": [
      "Reduce cyclomatic complexity",
      "Improve readability",
      "Make function more maintainable"
    ],
    "effort": 3
  }
]
```

### Text Report

The text report provides a simple summary that can be viewed directly in the terminal:

```
# Refactoring Suggestions Report

Total suggestions: 5

- Critical: 0
- High: 2
- Medium: 2
- Low: 1

## Suggestion Types
- extract_method: 3
- strategy: 1
- architectural: 1

## Detailed Suggestions

### 1. Extract methods from complex function 'process_data'
- **Type:** extract_method
- **Impact:** high
- **File:** /path/to/file.py
- **Lines:** 45-67
- **Source:** complexity_metrics
- **Effort:** 3 (1-5 scale)

**Benefits:**
- Reduce cyclomatic complexity
- Improve readability
- Make function more maintainable

...
```

## Extending the Refactoring Module

You can customize or extend the refactoring suggestions module in several ways:

### 1. Create a Custom Suggestion Generator

Create a new subclass of `SuggestionGenerator` and implement the `generate_suggestions` method:

```python
from src.refactoring.refactoring_suggestion import (
    SuggestionGenerator, 
    RefactoringSuggestion,
    RefactoringType,
    SuggestionImpact
)

class MyCustomSuggestionGenerator(SuggestionGenerator):
    def __init__(self):
        super().__init__()
        
    def generate_suggestions(self, target):
        suggestions = []
        
        # Your custom analysis logic here
        # ...
        
        # Create suggestions
        suggestions.append(RefactoringSuggestion(
            refactoring_type=RefactoringType.CUSTOM,
            description="Your custom suggestion",
            file_path="/path/to/file.py",
            line_range=(10, 20),
            impact=SuggestionImpact.MEDIUM,
            source="custom_analysis",
            details={"your_key": "your_value"},
            benefits=["Benefit 1", "Benefit 2"]
        ))
        
        return suggestions
```

### 2. Adding Your Generator to the Composite Generator

```python
from src.refactoring.refactoring_suggestion import CompositeSuggestionGenerator
from my_module import MyCustomSuggestionGenerator

# Create the composite generator
generator = CompositeSuggestionGenerator()

# Add your custom generator
generator.add_generator(MyCustomSuggestionGenerator())

# Generate suggestions
suggestions = generator.generate_all_suggestions("/path/to/target")
```

### 3. Creating Custom Refactoring Types

You can extend the `RefactoringType` enum to add your own refactoring types:

```python
from src.refactoring.refactoring_suggestion import RefactoringType
from enum import Enum

class ExtendedRefactoringType(Enum):
    # Include all existing types
    EXTRACT_METHOD = RefactoringType.EXTRACT_METHOD.value
    EXTRACT_CLASS = RefactoringType.EXTRACT_CLASS.value
    # ...
    
    # Add your custom types
    MY_CUSTOM_TYPE = "my_custom_type"
    ANOTHER_TYPE = "another_type"
```

## Contributing

Contributions to the refactoring module are welcome! Areas for improvement include:

1. Adding new suggestion generators for different languages or frameworks
2. Implementing more design pattern detectors
3. Improving the accuracy of existing generators
4. Adding more detailed before/after code examples
5. Enhancing the reporting formats

Before contributing, please read our [contribution guidelines](../../CONTRIBUTING.md).

## License

The Code Pattern Analyzer, including the refactoring module, is licensed under the [MIT License](../../LICENSE).