# Code Pattern Analyzer - Getting Started

This guide will help you get started with the Code Pattern Analyzer.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

### From Source

1. Clone or download the repository:
   ```bash
   git clone https://github.com/kylork/code-pattern-analyzer.git
   cd code-pattern-analyzer
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

This will install the `code-pattern` command line tool.

### Quick Demo

The package includes a demo script that showcases the main features:

```bash
./demo.sh
```

This will run the analyzer on the included sample files and generate HTML reports in the `reports` directory.

## Basic Usage

### List Available Patterns

To see what patterns the analyzer can detect:

```bash
code-pattern list-patterns
```

### List Pattern Categories

To see the available pattern categories:

```bash
code-pattern list-categories
```

### Analyze a File

To analyze a single file for all patterns:

```bash
code-pattern analyze --file your_file.py
```

### Analyze a Directory

To analyze an entire directory:

```bash
code-pattern report /path/to/project
```

### Generate HTML Reports

To generate an HTML report with visualizations:

```bash
code-pattern report /path/to/project --format html
```

### Compare Files

To compare pattern detection between multiple files:

```bash
code-pattern compare file1.py file2.py
```

## Configuration

By default, the tool uses a mock implementation for demonstration purposes. To use the real tree-sitter implementation, set the environment variable:

```bash
export CODE_PATTERN_USE_MOCK=False
```

## Next Steps

1. Try analyzing your own codebase:
   ```bash
   code-pattern report /path/to/your/code --format html
   ```

2. Check the [extending guide](../developer-guide/extending.md) for information on adding new patterns.

3. Review the [web UI design document](../features/web-ui/design.md) to learn about the planned web interface.

4. Explore the [roadmap](../project/roadmap.md) to see future development plans.

## Troubleshooting

If you encounter issues:

1. Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Check the logs for error messages (usually printed to console).

3. For problems with tree-sitter:
   ```bash
   python -c "import tree_sitter; print(tree_sitter.__version__)"
   ```
   This should print the tree-sitter version if it's installed correctly.

## Getting Help

If you need assistance:

- Check the documentation in the repository
- Open an issue on GitHub
- Refer to the test files for usage examples