# Integrated Usage Guide

This guide covers the unified workflow for using the Code Pattern Analyzer, showing how to combine the various analysis tools into an effective workflow for understanding and improving your codebase.

## Table of Contents

1. [Introduction](#introduction)
2. [Unified Command Line Interface](#unified-command-line-interface)
3. [Complete Workflow Example](#complete-workflow-example)
4. [Dashboard Interface](#dashboard-interface)
5. [VSCode Integration](#vscode-integration)
6. [Configuration Options](#configuration-options)

## Introduction

The Code Pattern Analyzer provides a comprehensive set of tools for analyzing code, detecting patterns, identifying issues, and suggesting improvements. While each component (pattern detection, flow analysis, complexity metrics, etc.) is valuable on its own, the real power comes from combining these tools into an integrated workflow.

This guide demonstrates how to use the unified entry point (`code_pattern_analyzer.py`) to perform comprehensive analyses and implement improvements based on the results.

## Unified Command Line Interface

The `code_pattern_analyzer.py` script serves as a unified entry point for the Code Pattern Analyzer, integrating all components:

```bash
./code_pattern_analyzer.py analyze /path/to/project -o report.html
```

This command runs a comprehensive analysis, including:
- Pattern detection
- Flow analysis (control flow and data flow)
- Complexity metrics
- Refactoring suggestions
- Architecture analysis

### Command Line Options

The unified interface supports the following commands:

- `analyze`: Run an integrated analysis on a file or directory
- `gui`: Start the Code Pattern Analyzer GUI
- `tutorial`: Show a tutorial for the Code Pattern Analyzer
- `examples`: Show examples for the Code Pattern Analyzer
- `dashboard`: Start the interactive dashboard
- `help`: Show help information

Common options include:

- `--output, -o`: Specify the output file or directory for the results
- `--format, -f`: Set the output format (html, json, text, markdown)
- `--include, -i`: Select which analysis types to include (all, patterns, flow, complexity, refactoring, architecture)
- `--log-level`: Set the logging level

For the GUI and dashboard commands:

- `--host`: Host to run the server on
- `--port`: Port to run the server on
- `--no-browser`: Don't automatically open a browser window

Example:

```bash
# Only include flow analysis and refactoring suggestions
./code_pattern_analyzer.py analyze /path/to/project -o report.html --include flow,refactoring

# Generate JSON output
./code_pattern_analyzer.py analyze /path/to/project -o results.json -f json

# Start the GUI on a custom port
./code_pattern_analyzer.py gui --port 8888
```

## Complete Workflow Example

Here's a complete workflow example showing how to analyze a project and implement improvements:

### 1. Initial Analysis

Start with a comprehensive analysis of your project:

```bash
./code_pattern_analyzer.py analyze path/to/project -o initial_analysis.html
```

This generates a detailed HTML report with findings from all analysis types.

### 2. Review Findings in the Dashboard

For an interactive exploration of the results:

```bash
./code_pattern_analyzer.py dashboard
```

In the dashboard:
1. Upload the `initial_analysis.json` file
2. Explore the different tabs: Overview, Complexity, Flow Analysis, Refactoring, Architecture
3. Identify the most critical issues to address

### 3. Apply Refactoring Suggestions

After identifying key improvement opportunities:

```bash
# Start an interactive refactoring session
code-pattern refactoring interactive path/to/project
```

This will:
1. Generate refactoring suggestions
2. Present them one by one
3. Allow you to apply, skip, or modify each suggestion
4. Track applied changes

### 4. Apply Design Pattern Transformations

For structural improvements:

```bash
# Apply Factory pattern transformations
code-pattern refactoring transform path/to/project --pattern factory --apply
```

### 5. Re-analyze After Changes

After implementing improvements, run another analysis to verify the changes:

```bash
./code_pattern_analyzer.py analyze path/to/project -o improved_analysis.html
```

### 6. Generate a Comparison Report

Compare the before and after state:

```bash
code-pattern compare initial_analysis.json improved_analysis.json -o comparison.html
```

## Dashboard Interface

The Code Pattern Analyzer dashboard provides an interactive visual interface for exploring analysis results:

```bash
./code_pattern_analyzer.py dashboard
```

The dashboard includes:

- **Analysis Options**: Upload results or run a new analysis
- **Overview**: Summary of all findings with metrics and charts
- **Complexity Analysis**: Detailed view of complexity metrics with charts for top complex functions
- **Flow Analysis**: Lists of dead code, infinite loops, unused variables, etc.
- **Refactoring Suggestions**: Interactive cards for each suggestion with code previews
- **Architecture Analysis**: Architectural style detection results and anti-patterns

### Using the Dashboard

1. **Upload Results or Run Analysis**:
   - Upload a results JSON file from a previous analysis
   - Or enter a project path and run a new analysis

2. **Explore the Overview**:
   - See metrics for each issue category
   - View the distribution of findings across categories

3. **Dive into Specific Areas**:
   - Click on tabs to explore different analysis types
   - Filter and sort results as needed

4. **View Code Examples**:
   - For refactoring suggestions, click "View Code" to see before/after code examples

## VSCode Integration

For a seamless development experience, the Code Pattern Analyzer integrates with Visual Studio Code:

1. **Install the VSCode Extension**:
   - Open VSCode
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Code Pattern Analyzer"
   - Click Install

2. **Use the Extension**:
   - Open the command palette (Ctrl+Shift+P)
   - Type "Code Pattern Analyzer" to see available commands
   - Execute analyses directly from VSCode
   - View results and apply refactorings within the editor

The extension provides:
- In-editor highlighting of issues
- Quick-fix actions for refactoring suggestions
- Inline visualization of complexity metrics
- Integration with VSCode's Problems panel

## Configuration Options

The Code Pattern Analyzer can be configured with a YAML configuration file:

```bash
# Use a configuration file
./code_pattern_analyzer.py analyze /path/to/project --config config.yml
```

Example `config.yml`:

```yaml
analysis:
  include:
    - patterns
    - flow
    - complexity
    - refactoring
  exclude_dirs:
    - node_modules
    - build
    - dist
    - venv

refactoring:
  min_impact: medium
  types:
    - EXTRACT_METHOD
    - FACTORY_METHOD
    - STRATEGY

complexity:
  thresholds:
    cyclomatic:
      warning: 10
      error: 15
    cognitive:
      warning: 15
      error: 25

flow:
  analysis:
    dead_code: true
    infinite_loops: true
    unused_variables: true
    undefined_variables: true

output:
  format: html
  path: analysis_report.html
  open_browser: true
```

This allows you to:
- Customize which analyses to run
- Set thresholds for complexity metrics
- Configure refactoring priorities
- Define output formats and locations
- Exclude directories from analysis