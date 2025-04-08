# Tree-Sitter Integration

The Code Pattern Analyzer uses [tree-sitter](https://tree-sitter.github.io/tree-sitter/) for robust and accurate code parsing. This document explains how the tree-sitter integration works and how to use it effectively.

## Architecture

The tree-sitter integration consists of several components:

- **TreeSitterManager**: Downloads, builds, and manages language grammars
- **CodeParser**: Uses the manager to parse files and code
- **QueryBasedPattern**: Base class for patterns using tree-sitter queries
- **TreeSitterWrapper**: Provides a simple interface to the tree-sitter functionality

## Toggle Between Implementations

The analyzer supports two implementations:

1. **Mock Implementation**: A simple regex-based approach for quick testing
2. **Real Tree-Sitter Implementation**: Full tree-sitter integration for accurate parsing

You can toggle between these implementations in several ways:

### 1. Command-Line Flag

All CLI commands support a `--real/--mock` flag:

```bash
# Use the real tree-sitter implementation
code-pattern analyze --file path/to/file.py --real

# Use the mock implementation
code-pattern analyze --file path/to/file.py --mock
```

### 2. Environment Variable

Set an environment variable to change the default:

```bash
# Set default to real implementation
export CODE_PATTERN_USE_MOCK=False

# Run command (uses real implementation by default)
code-pattern analyze --file path/to/file.py
```

### 3. Programmatically

When using the API directly:

```python
from code_pattern_analyzer import CodeAnalyzer

# Use real implementation
analyzer = CodeAnalyzer(use_mock=False)

# Or toggle at runtime
analyzer.set_implementation(use_mock=False)  # Switch to real
analyzer.set_implementation(use_mock=True)   # Switch to mock
```

## Supported Languages

The analyzer supports the following languages with tree-sitter:

- Python
- JavaScript
- TypeScript
- Ruby
- Go
- Java
- C
- C++
- Rust

## Grammar Installation

When using the real tree-sitter implementation, language grammars are automatically downloaded and built as needed. This requires:

- A C compiler (GCC, Clang, MSVC, etc.)
- Git (optional, direct downloads as fallback)
- Python development headers

The grammars are stored in the `tree_sitter_languages` directory within the package.

## Writing Tree-Sitter Queries

Tree-sitter uses a query language to match patterns in the syntax tree. Here's an example query for Python functions:

```
(function_definition
  name: (identifier) @name
  parameters: (parameters) @params
  body: (block) @body)
```

This query captures:
- Function names as `@name`
- Parameter lists as `@params`
- Function bodies as `@body`

For more information on writing queries, see the [tree-sitter documentation](https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax).

## Creating Custom Patterns

To create a custom pattern using tree-sitter:

1. Create a new class that inherits from `QueryBasedPattern`
2. Define queries for each supported language
3. Optionally override `_process_query_results` to extract additional information

Example:

```python
from code_pattern_analyzer.pattern_base import QueryBasedPattern

class MyCustomPattern(QueryBasedPattern):
    def __init__(self):
        super().__init__(
            name="my_custom_pattern",
            description="Identifies my custom pattern",
            languages=["python", "javascript"]
        )
        
        # Define language-specific queries
        self.queries = {
            'python': """
                (your_query_here) @capture_name
            """,
            'javascript': """
                (your_query_here) @capture_name
            """
        }
```

## Testing

You can test both implementations using the included script:

```bash
python test_implementations.py
```

This runs both implementations on a sample file and displays the results for comparison.