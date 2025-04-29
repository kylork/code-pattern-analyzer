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
- **Code Complexity Metrics**: Analyze cyclomatic complexity, cognitive complexity, and maintainability index
- **Code-Pattern Linkage**: Bidirectional linking between visualizations and code implementations
- **Smart Refactoring Suggestions**: AI-powered refactoring recommendations with automated code transformations
- **Extensible Architecture**: Easily add new patterns and languages
- **Command-Line Interface**: Simple CLI for integration into workflows
- **Comparison Tools**: Compare pattern usage between files
- **Web Interface**: User-friendly web UI for analyzing code and managing projects
- **Interactive Design Pattern Explorer**: Learn about design patterns with interactive examples and simulations

## Quick Start

The fastest way to get started with Code Pattern Analyzer is to use the unified GUI:

```bash
# Start the Code Pattern Analyzer GUI
python code_pattern_analyzer_gui.py
```

This will launch a web-based GUI in your browser, providing access to all the tool's features:
- Analyze projects for architectural patterns
- Generate interactive visualizations
- View code-pattern linkages
- Manage visualization outputs
- Explore design patterns interactively

### Educational Tools

Code Pattern Analyzer includes educational tools to help understand software architecture:

```bash
# Generate example projects with different architectural styles
python create_example_project.py --style layered

# Compare different architectural approaches side-by-side
python compare_architectures.py

# Simulate how architecture evolves over time
python simulate_architecture_evolution.py

# Explore design patterns with interactive examples
python explore_design_patterns.py --serve

# Explore multiple design patterns
python multi_pattern_explorer.py --serve
```

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
  - [Code Complexity Metrics](docs/features/complexity-metrics.md)
  - [Visualization](docs/features/visualization.md)
  - [Web UI](docs/features/web-ui/overview.md)
  - [Design Pattern Explorer](docs/features/design-patterns/overview.md)

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

### Unified GUI

```bash
# Start the Code Pattern Analyzer GUI
python code_pattern_analyzer_gui.py

# Optionally specify host and port
python code_pattern_analyzer_gui.py --host 0.0.0.0 --port 8888

# Integrate the Design Pattern Explorer with the GUI
python integrate_pattern_explorer.py --run-gui
```

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

# Analyze code complexity metrics
code-pattern complexity /path/to/project --format html

# Generate refactoring suggestions
code-pattern refactoring suggest /path/to/project --output suggestions.html --format html 

# Interactive refactoring session
code-pattern refactoring interactive /path/to/project

# Apply pattern transformations
code-pattern refactoring transform /path/to/project --pattern factory --apply

# Batch refactoring
./run_batch_refactoring.py /path/to/project --min-impact medium

# Visualize architecture
code-pattern visualize /path/to/project --pattern layered_architecture

# Generate component visualization
python run_component_visualization.py /path/to/project --style layered

# Generate interactive visualization with code-pattern linkage
python run_code_pattern_linkage.py /path/to/project --output visualization.html

# Compare files
code-pattern compare file1.py file2.py
```

### Visualization Tools

The Code Pattern Analyzer includes several tools for visualizing code patterns:

```bash
# Generate interactive visualization with code-pattern linkage
python run_code_pattern_linkage.py /path/to/project --output visualization.html

# View a visualization in the browser
python view_visualization.py output/visualization.html

# Start a local server to view visualizations
python view_visualization.py --server output/

# Create a portable visualization bundle for sharing
python view_visualization.py --bundle output/visualization.html --output-dir ./portable_visualizations
```

### Design Pattern Explorer

Explore and learn about design patterns interactively:

```bash
# Start the Design Pattern Explorer with the Observer pattern (default)
python explore_design_patterns.py --serve

# Start the Multi-Pattern Explorer to access all available patterns
python multi_pattern_explorer.py --serve

# List available design patterns
python multi_pattern_explorer.py --list-patterns

# Generate a specific pattern explorer
python multi_pattern_explorer.py --pattern "Factory Method" --serve
```

## Web Interface

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
- Design Pattern Explorer integration

Visit http://localhost:3000 in your browser to access the web interface.

## License

MIT License