# Development Guide

This guide provides information for developers working on the Code Pattern Analyzer.

## Project Structure

```
code-pattern-analyzer/
├── code_pattern_analyzer.py    # Unified entry point
├── run_refactoring_suggestions.py  # Standalone refactoring script
├── run_batch_refactoring.py     # Batch refactoring script
├── src/                        # Source code
│   ├── analyzer.py             # Main analyzer class
│   ├── cli.py                  # CLI implementation
│   ├── flow/                   # Flow analysis
│   │   ├── control_flow.py     # Control flow analysis
│   │   └── data_flow.py        # Data flow analysis
│   ├── metrics/                # Code metrics
│   │   └── complexity/         # Complexity metrics
│   ├── patterns/               # Pattern detection
│   ├── refactoring/            # Refactoring module
│   │   ├── refactoring_suggestion.py  # Suggestion generation
│   │   ├── code_transformer.py        # Code transformation
│   │   └── interactive_refactoring.py # Interactive sessions
│   ├── templates/              # HTML templates
│   └── web/                    # Web UI components
│       ├── app.py              # Web application
│       ├── dashboard.py        # Interactive dashboard
│       └── vscode_extension/   # VS Code integration
├── docs/                       # Documentation
└── tests/                      # Unit tests
```

## Development Setup

### Prerequisites

- Python 3.8 or later
- Node.js 14 or later (for VS Code extension)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kylork/code-pattern-analyzer.git
   cd code-pattern-analyzer
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install node dependencies (for VS Code extension):
   ```bash
   cd src/web/vscode_extension
   npm install
   ```

## Development Workflow

### Running Tests

Run all tests:
```bash
python -m pytest
```

Run specific tests:
```bash
python -m pytest tests/test_refactoring_suggestions.py
```

### Linting

Lint the code:
```bash
flake8 src tests
```

### Type Checking

Check types with mypy:
```bash
mypy src
```

### Development Server

Run the web app in development mode:
```bash
python -m src.web.app --debug
```

Run the dashboard in development mode:
```bash
python -m src.web.dashboard
```

### VS Code Extension Development

1. Open the extension directory in VS Code:
   ```bash
   code src/web/vscode_extension
   ```

2. Press F5 to launch the extension in a new VS Code window.

## Architecture Overview

### Core Components

1. **Analyzer**: The central component that orchestrates analysis
2. **Flow Analysis**: Control and data flow analysis
3. **Metrics**: Code complexity and quality metrics
4. **Pattern Detection**: Detection of design patterns and anti-patterns
5. **Refactoring**: Suggestion and application of code improvements
6. **Visualization**: Visualization of analysis results

### Key Interfaces

#### `CodeAnalyzer` Class

The main entry point for code analysis:

```python
from src.analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
results = analyzer.analyze_file("path/to/file.py")
```

#### Flow Analysis

```python
from src.flow.control_flow import ControlFlowAnalyzer
from src.flow.data_flow import DataFlowAnalyzer

cfg_analyzer = ControlFlowAnalyzer()
cfg_results = cfg_analyzer.analyze("path/to/file.py")

df_analyzer = DataFlowAnalyzer()
df_results = df_analyzer.analyze("path/to/file.py")
```

#### Refactoring

```python
from src.refactoring.refactoring_suggestion import CompositeSuggestionGenerator
from src.refactoring.code_transformer import BatchTransformer

# Generate suggestions
generator = CompositeSuggestionGenerator()
suggestions = generator.generate_all_suggestions("path/to/project")

# Apply transformations
transformer = BatchTransformer()
results = transformer.apply_suggestions(suggestions)
```

## Code Style and Guidelines

### Python Code Style

- Follow PEP 8
- Use type hints
- Keep line length to 100 characters or less
- Use docstrings in Google format

Example:
```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of the function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
    # Implementation
    pass
```

### JavaScript Code Style (VS Code Extension)

- Use ES6 features
- Follow the VS Code extension guidelines
- Use JSDoc comments

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `python -m pytest`
4. Run linting: `flake8 src tests`
5. Push your branch: `git push origin feature/my-feature`
6. Create a Pull Request

## Release Process

1. Update the version number in `setup.py`
2. Update the changelog in `CHANGELOG.md`
3. Create and push a tag: `git tag v0.1.0 && git push --tags`
4. Build the package: `python setup.py sdist bdist_wheel`
5. Upload to PyPI: `twine upload dist/*`

## Documentation

The documentation is built using Markdown files in the `docs/` directory. To view the docs locally:

```bash
mkdocs serve
```

## Getting Help

If you need help with development, check:
- The GitHub issues page
- The project's development Slack channel
- The documentation