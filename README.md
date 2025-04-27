# Code Pattern Analyzer

A powerful tool for analyzing and identifying patterns in source code across multiple programming languages.

## Overview

![Code Pattern Analyzer](https://img.shields.io/badge/Status-Prototype-blue)

The Code Pattern Analyzer is a framework for detecting patterns in source code. It can identify common structures like functions and classes, as well as more complex design patterns and anti-patterns. This tool aims to help developers understand existing codebases, identify refactoring opportunities, and enforce coding standards.

> **New Contributors**: Before diving into the code, please read the following documents in order:
> 1. [docs/overview/philosophy.md](docs/overview/philosophy.md) - Understanding the project's vision and purpose
> 2. [docs/project/claude.md](docs/project/claude.md) - Technical implementation guide 
> 3. [docs/developer-guide/extending.md](docs/developer-guide/extending.md) - Guide for adding new patterns

## Features

- **Multi-Language Support**: Analyze code in Python, JavaScript, TypeScript, Ruby, Java, and more
- **Pattern Detection**: Identify functions, classes, design patterns, and code smells
- **Interactive Reports**: Generate detailed HTML reports with visualizations
- **Architecture Analysis**: Detect architectural styles, intents, and anti-patterns
- **Architecture Visualization**: Visualize detected architectural patterns with interactive diagrams
- **Extensible Architecture**: Easily add new patterns and languages
- **Command-Line Interface**: Simple CLI for integration into workflows
- **Comparison Tools**: Compare pattern usage between files
- **Web Interface**: User-friendly web UI for analyzing code and managing projects

## Documentation

- [Overview](docs/overview/README.md)
  - [Philosophy](docs/overview/philosophy.md)
  - [Project Structure](docs/overview/structure.md)
  - [Project Summary](docs/overview/project-summary.md)

- [User Guide](docs/user-guide/getting-started.md)
  - [Getting Started](docs/user-guide/getting-started.md)

- [Developer Guide](docs/developer-guide/)
  - [Extending](docs/developer-guide/extending.md)
  - [Tree-Sitter Integration](docs/developer-guide/tree-sitter.md)

- [Features](docs/features/)
  - [Architecture Detection](docs/features/architecture-detection/overview.md)
  - [Architectural Intents](docs/features/architecture-detection/intents.md)
  - [Architectural Styles](docs/features/architecture-detection/styles.md)
  - [Architectural Anti-Patterns](docs/features/anti-patterns.md)
  - [Visualization](docs/features/visualization.md)
  - [Web UI](docs/features/web-ui/overview.md)

- [Project](docs/project/)
  - [Roadmap](docs/project/roadmap.md)
  - [Achievements](docs/project/achievements.md)
  - [Claude Implementation Guide](docs/project/claude.md)

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

# Analyze architectural styles
code-pattern architecture /path/to/project --style

# Detect architectural anti-patterns
code-pattern anti-patterns /path/to/project --format html

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

## License

MIT License