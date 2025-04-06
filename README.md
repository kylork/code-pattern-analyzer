# Code Pattern Analyzer

A powerful tool for analyzing and identifying patterns in source code across multiple programming languages.

![Code Pattern Analyzer](https://img.shields.io/badge/Status-Prototype-blue)

## Features

- **Multi-Language Support**: Analyze code in Python, JavaScript, TypeScript, Ruby, Java, and more
- **Pattern Detection**: Identify functions, classes, design patterns, and code smells
- **Interactive Reports**: Generate detailed HTML reports with visualizations
- **Extensible Architecture**: Easily add new patterns and languages
- **Command-Line Interface**: Simple CLI for integration into workflows
- **Comparison Tools**: Compare pattern usage between files

## Pattern Types

### Basic Patterns
- Function and method definitions
- Class and interface definitions
- Inheritance relationships
- Constructor patterns

### Design Patterns
- Singleton pattern (multiple variants)
- Factory Method pattern

### Code Quality Patterns
- Long methods
- Deeply nested code
- Complex conditional expressions

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-pattern-analyzer.git
cd code-pattern-analyzer

# Install in development mode
pip install -e .
```

## Usage

### List Available Patterns

```bash
code-pattern list-patterns
```

### List Pattern Categories

```bash
code-pattern list-categories
```

### Analyze a File

```bash
code-pattern analyze --file path/to/your/file.py
```

### Analyze with Specific Pattern

```bash
code-pattern analyze --file path/to/your/file.py --pattern singleton
```

### Analyze a Directory

```bash
code-pattern report /path/to/project --format html
```

### Compare Files

```bash
code-pattern compare file1.py file2.py
```

## Configuration

Environment variables:
- `CODE_PATTERN_USE_MOCK`: Set to 'False' to use the real tree-sitter implementation (default: 'True')

## Example Output

```
File: example.py
Language: python
Total patterns: 3

Pattern: singleton
  Singleton (design_pattern) at line 5

Pattern: function_definition
  calculate_value (function) at line 25
  process_data (function) at line 42

Pattern: class_definition
  DataProcessor (class) at line 18
```

## Architecture

The Code Pattern Analyzer is built with a modular architecture:

1. **Parser**: Uses tree-sitter to parse source code into ASTs
2. **Pattern Registry**: Manages available patterns
3. **Pattern Recognizer**: Applies patterns to ASTs
4. **Analyzer**: Coordinates analysis of files and directories
5. **Reporter**: Generates reports in various formats
6. **CLI**: Provides command-line interface

## Extending

See [EXTENDING.md](EXTENDING.md) for details on adding new patterns.

## Project Status

This is a prototype implementation. For details about what has been implemented, see [ACHIEVEMENTS.md](ACHIEVEMENTS.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned future developments.

## License

MIT License