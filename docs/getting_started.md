# Getting Started with Code Pattern Analyzer

This guide will help you get started with the Code Pattern Analyzer, from installation to your first analysis.

## Installation

### Prerequisites

- Python 3.8 or later
- pip (Python package installer)
- Git (optional, for installation from source)

### Install from PyPI

The simplest way to install Code Pattern Analyzer is from PyPI:

```bash
pip install code-pattern-analyzer
```

### Install from Source

For the latest development version or to contribute to the project:

```bash
git clone https://github.com/kylork/code-pattern-analyzer.git
cd code-pattern-analyzer
pip install -e .
```

## Quick Start

### Basic Analysis

Analyze a single file:

```bash
./code_pattern_analyzer.py analyze path/to/your/file.py
```

Analyze an entire project:

```bash
./code_pattern_analyzer.py analyze path/to/your/project -o analysis_report.html
```

### Start the Dashboard

For an interactive experience:

```bash
./code_pattern_analyzer.py dashboard
```

Then upload a results file or run a new analysis from the dashboard interface.

### Generate Refactoring Suggestions

```bash
./code_pattern_analyzer.py analyze path/to/project --include refactoring -o refactoring.html
```

Or use the dedicated refactoring script:

```bash
./run_refactoring_suggestions.py path/to/project -o refactoring.html
```

## Key Features

### 1. Pattern Detection

Identify code patterns including:
- Design patterns (Factory, Strategy, Observer, etc.)
- Code smells
- Architectural patterns

### 2. Flow Analysis

Analyze control and data flow to find:
- Dead code
- Potential infinite loops
- Unused variables
- Undefined variables

### 3. Complexity Metrics

Calculate metrics including:
- Cyclomatic complexity
- Cognitive complexity
- Maintainability index

### 4. Refactoring Suggestions

Get actionable suggestions for:
- Extracting methods
- Applying design patterns
- Fixing flow issues
- Addressing architectural problems

### 5. Interactive Dashboard

Explore results visually with:
- Charts and graphs
- Code previews
- Interactive filtering
- Custom reports

## Example Workflows

### 1. Basic Code Analysis

```bash
# Analyze a project
./code_pattern_analyzer.py analyze path/to/project -o analysis.html

# Open the HTML report in a browser
open analysis.html
```

### 2. Finding and Fixing Complex Code

```bash
# Generate complexity analysis
./code_pattern_analyzer.py analyze path/to/project --include complexity -o complexity.html

# Start interactive refactoring for complex methods
code-pattern refactoring interactive path/to/project
```

### 3. Pattern-Based Refactoring

```bash
# Detect pattern opportunities
./code_pattern_analyzer.py analyze path/to/project --include patterns -o patterns.html

# Apply a specific pattern transformation
code-pattern refactoring transform path/to/project --pattern factory --apply
```

### 4. Comprehensive Codebase Improvement

```bash
# Run full analysis
./code_pattern_analyzer.py analyze path/to/project -o full_analysis.html

# Start the dashboard for in-depth exploration
./code_pattern_analyzer.py dashboard

# Apply batch refactoring
./run_batch_refactoring.py path/to/project --min-impact medium

# Re-analyze to verify improvements
./code_pattern_analyzer.py analyze path/to/project -o improved_analysis.html
```

## Configuration

Create a configuration file `code_analyzer_config.yml`:

```yaml
analysis:
  include:
    - patterns
    - flow
    - complexity
    - refactoring
  exclude_dirs:
    - node_modules
    - venv
    - dist

complexity:
  thresholds:
    cyclomatic:
      warning: 10
      error: 15

output:
  format: html
  open_browser: true
```

Use it with:

```bash
./code_pattern_analyzer.py analyze path/to/project --config code_analyzer_config.yml
```

## Next Steps

After getting familiar with the basic usage, you might want to:

1. **Explore the documentation** for advanced usage
2. **Try the VS Code extension** for editor integration
3. **Review the tutorials** in the docs directory
4. **Customize the configuration** for your specific needs
5. **Explore the API** for integration with other tools

Check out these resources:

- [Integrated Usage Guide](user-guide/integrated_usage.md)
- [VS Code Integration](user-guide/vscode_integration.md)
- [Configuration Guide](user-guide/configuration.md)
- [API Documentation](api/README.md)
- [Contributing Guide](../CONTRIBUTING.md)