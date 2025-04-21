# Code Pattern Analyzer Usage Guide

This guide explains how to set up and use the Code Pattern Analyzer.

## Installation

### From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/kylork/code-pattern-analyzer.git
   cd code-pattern-analyzer
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

This will install the `code-pattern` command line tool.

## Basic Usage

### List Available Patterns

To see what patterns the analyzer can detect:

```bash
code-pattern list-patterns
```

### Analyze a Single File

To analyze a single file for all patterns:

```bash
code-pattern analyze --file sample.py
```

To look for a specific pattern:

```bash
code-pattern analyze --file sample.py --pattern function_definition
```

### Analyze a Directory

To analyze all supported files in a directory:

```bash
code-pattern analyze --directory src/
```

To filter by file extension:

```bash
code-pattern analyze --directory src/ --extensions .py,.js
```

To exclude certain directories:

```bash
code-pattern analyze --directory src/ --exclude node_modules,dist
```

### Output Formats

To change the output format:

```bash
code-pattern analyze --file sample.py --format text
```

To save the output to a file:

```bash
code-pattern analyze --directory src/ --output report.json
```

## Examples

### Finding Functions

```bash
code-pattern analyze --file sample.py --pattern function_definition
```

Example output:
```json
[
  {
    "file": "sample.py",
    "language": "python",
    "patterns": {
      "function_definition": [
        {
          "type": "function",
          "name": "greet",
          "line": 5,
          "column": 4
        },
        {
          "type": "function",
          "name": "calculate_average",
          "line": 23,
          "column": 4
        }
      ]
    }
  }
]
```

### Finding Classes

```bash
code-pattern analyze --file sample.py --pattern class_definition
```

Example output:
```json
[
  {
    "file": "sample.py",
    "language": "python",
    "patterns": {
      "class_definition": [
        {
          "type": "class",
          "name": "Person",
          "line": 8,
          "column": 6
        },
        {
          "type": "class",
          "name": "Calculator",
          "line": 29,
          "column": 6
        }
      ]
    }
  }
]
```

## Running the Demo

The project includes a demo script that you can run:

```bash
./run_demo.py
```

This will analyze the included sample.py file and show the results.

## Advanced Usage

### Programmatic API

You can use the analyzer from your own Python code:

```python
from src.analyzer import CodeAnalyzer

# Create an analyzer
analyzer = CodeAnalyzer()

# Analyze a file
results = analyzer.analyze_file("path/to/file.py")

# Generate a report
report = analyzer.generate_report([results], "json")
print(report)
```

## Troubleshooting

### Parser Issues

If you're getting parser errors:

- Make sure the file is valid and can be compiled/run
- Check that the language is supported
- Verify file encoding (UTF-8 recommended)

### Performance Issues

For large codebases:

- Use the `--extensions` option to limit file types
- Use the `--exclude` option to skip unnecessary directories
- Consider analyzing one directory at a time