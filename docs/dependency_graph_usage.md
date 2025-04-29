# Dependency Graph Generator

The Dependency Graph Generator is a powerful tool for analyzing import relationships between modules in your codebase. It helps you visualize dependencies, identify circular dependencies, and gain insights into the structure of your project.

## Features

- **Import Analysis**: Parse Python files to identify import statements and module dependencies
- **Visualization**: Generate interactive D3.js-based visualizations of module dependencies
- **Cycle Detection**: Identify circular dependencies that could cause issues
- **Metrics**: Calculate various dependency metrics including:
  - Centrality measures
  - In-degree and out-degree
  - Strongly connected components
  - Most important modules
- **Layer Detection**: Automatically categorize modules into architectural layers based on naming conventions
- **Detailed Reports**: Generate comprehensive HTML reports with dependency analysis

## Usage

### Basic Usage

```bash
python generate_dependency_graph.py /path/to/your/project
```

This will analyze the project and generate an interactive dependency graph visualization in the `reports` directory.

### Command Line Options

```
usage: generate_dependency_graph.py [-h] [--output-dir OUTPUT_DIR] [--output OUTPUT] [--report] [--plot] [--open]
                                   [--exclude EXCLUDE] [--extensions EXTENSIONS] [--debug]
                                   path

Generate a dependency graph for Python modules in a project

positional arguments:
  path                  Path to the directory to analyze

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR, -d OUTPUT_DIR
                        Output directory (default: reports)
  --output OUTPUT, -o OUTPUT
                        Output file name (default: dependency_graph.html)
  --report, -r          Generate a detailed HTML report
  --plot, -p            Generate a matplotlib visualization
  --open, -w            Open the visualization in a browser after generation
  --exclude EXCLUDE     Comma-separated list of directories to exclude
  --extensions EXTENSIONS, -e EXTENSIONS
                        Comma-separated list of file extensions to analyze (default: .py)
  --debug               Enable debug logging
```

### Examples

#### Generate a dependency graph with a detailed report

```bash
python generate_dependency_graph.py /path/to/project --report
```

#### Generate a dependency graph and open it in the browser

```bash
python generate_dependency_graph.py /path/to/project --open
```

#### Analyze a specific subset of files

```bash
python generate_dependency_graph.py /path/to/project --extensions .py,.pyx --exclude tests,docs
```

#### Generate both an interactive D3.js visualization and a static matplotlib plot

```bash
python generate_dependency_graph.py /path/to/project --plot
```

## Understanding the Visualization

The dependency graph visualization includes:

1. **Interactive Graph**: A force-directed graph where:
   - Nodes represent modules
   - Edges represent import dependencies
   - Colors represent architectural layers (presentation, business, data access, domain)
   - Red dashed lines indicate circular dependencies

2. **Controls**:
   - Group by: Organize modules by layer, type, or module
   - Filter: Focus on specific architectural layers
   - Highlight violations: Emphasize circular dependencies
   - Reset view: Return to the original view

3. **Module Details**: Click on any module to see detailed information:
   - Module name and type
   - File path
   - Number of incoming and outgoing dependencies
   - Architectural layer

## Metrics and Analysis

The dependency graph generator calculates various metrics to help you understand your codebase's structure:

- **Connectivity Metrics**: How interconnected your modules are
- **Centrality Metrics**: Which modules are most central to your codebase
- **Circular Dependencies**: Cycles in the dependency graph that can cause issues
- **Layer Analysis**: How well your code adheres to layered architecture principles

## Addressing Circular Dependencies

Circular dependencies can lead to various issues:

1. **Initialization Problems**: Modules that depend on each other can create initialization deadlocks
2. **Testing Difficulties**: Circular dependencies make unit testing more challenging
3. **Maintenance Issues**: Changes to one module can ripple through the cycle

Strategies to resolve circular dependencies:

1. **Dependency Inversion**: Create abstractions (interfaces) that both modules depend on
2. **Extract Common Functionality**: Move shared code to a third module that both can depend on
3. **Restructure Code**: Refactor to eliminate the need for bidirectional dependency

## Integration with Other Tools

The dependency graph generator integrates with other Code Pattern Analyzer features:

- **Architectural Analysis**: Use with architectural pattern detection
- **Code Complexity Analysis**: Combine with complexity metrics for comprehensive assessment
- **Pattern Detection**: Identify design patterns in the dependency structure

## Programmatic API

You can also use the `DependencyGraphGenerator` class programmatically in your own scripts:

```python
from generate_dependency_graph import DependencyGraphGenerator

# Initialize the generator
generator = DependencyGraphGenerator()

# Analyze a directory
generator.analyze_directory('/path/to/project')

# Access the dependency graph
graph = generator.graph

# Get circular dependencies
cycles = generator.cycles

# Generate visualizations
generator.visualize_with_d3(output_dir='output')
generator.plot_dependency_graph('output/graph.png')

# Generate reports
generator.generate_report('output/report.html')

# Get metrics
metrics = generator.metrics
```