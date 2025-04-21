# Code Pattern Analyzer

A powerful tool for analyzing and identifying patterns in source code across multiple programming languages.

## Overview

![Code Pattern Analyzer](https://img.shields.io/badge/Status-Prototype-blue)

The Code Pattern Analyzer is a framework for detecting patterns in source code. It can identify common structures like functions and classes, as well as more complex design patterns and anti-patterns. This tool aims to help developers understand existing codebases, identify refactoring opportunities, and enforce coding standards.

> **New Contributors**: Before diving into the code, please read the following documents in order:
> 1. [PHILOSOPHY.md](PHILOSOPHY.md) - Understanding the project's vision and purpose
> 2. [ONBOARDING.md](ONBOARDING.md) - Guide for new contributors
> 3. [CLAUDE.md](CLAUDE.md) - Technical implementation guide

## Features

- **Multi-Language Support**: Analyze code in Python, JavaScript, TypeScript, Ruby, Java, and more
- **Pattern Detection**: Identify functions, classes, design patterns, and code smells
- **Interactive Reports**: Generate detailed HTML reports with visualizations
- **Architecture Visualization**: Visualize detected architectural patterns with interactive diagrams
- **Extensible Architecture**: Easily add new patterns and languages
- **Command-Line Interface**: Simple CLI for integration into workflows
- **Comparison Tools**: Compare pattern usage between files
- **Web Interface**: User-friendly web UI for analyzing code and managing projects

## Pattern Types

### Basic Patterns
- Function and method definitions
- Class and interface definitions
- Inheritance relationships
- Constructor patterns

### Design Patterns
- Singleton pattern (multiple variants)
- Factory Method pattern
- Observer pattern
- Decorator pattern
- Strategy pattern

### Code Quality Patterns
- Long methods
- Deeply nested code
- Complex conditional expressions

### Architectural Patterns
- Separation of Concerns
- Information Hiding
- Dependency Inversion
- Layered Architecture
- Hexagonal Architecture
- Clean Architecture
- Event-Driven Architecture

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/kylork/code-pattern-analyzer.git
cd code-pattern-analyzer

# Install in development mode
pip install -e .
```

### With Docker

```bash
# Build the Docker image
docker build -t code-pattern-analyzer .

# Run the container
docker run -v $(pwd)/sample-code:/code -w /code code-pattern-analyzer analyze --file sample.py
```

## Usage

### Command Line Interface

```bash
# List available patterns
code-pattern list-patterns

# Analyze a file
code-pattern analyze --file sample.py

# Analyze a directory
code-pattern analyze --directory src/

# Generate a report
code-pattern report /path/to/project --format html

# Visualize architecture
code-pattern visualize /path/to/project --pattern layered_architecture

# Compare files
code-pattern compare file1.py file2.py
```

### Web Interface

The Code Pattern Analyzer includes a web interface for easier interaction:

```bash
# Set up the web UI
./scripts/setup_web_ui.sh

# Start the web interface
./scripts/start_web_ui.sh
```

The web interface provides:
- File upload and direct code input
- Project management
- Interactive visualization of results
- Pattern exploration

Visit http://localhost:3000 in your browser to access the web interface.

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
7. **Web UI**: Provides user-friendly web interface

## Extending

See [EXTENDING.md](EXTENDING.md) for details on adding new patterns.

## Project Status

This is a prototype implementation. For details about what has been implemented, see [ACHIEVEMENTS.md](ACHIEVEMENTS.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned future developments.

## License

MIT License"}}