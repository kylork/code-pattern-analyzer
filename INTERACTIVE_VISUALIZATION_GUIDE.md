# Interactive Visualization Guide

This guide explains how to use the interactive visualization tools in the Code Pattern Analyzer to explore and understand code architecture.

## Getting Started

The Code Pattern Analyzer includes several visualization tools that provide interactive, graphical representations of code structure and architectural patterns. These visualizations help you understand complex codebases and identify potential issues.

### Running Visualizations from the Command Line

You can generate visualizations directly from the command line using the `run_component_visualization.py` script:

```bash
python run_component_visualization.py /path/to/project [options]
```

#### Options:

- `--output/-o`: Name of the output HTML file (default: `component_graph.html`)
- `--output-dir/-d`: Directory to save the visualization (default: `reports`)
- `--title`: Title for the visualization (default: `Component Relationships`)
- `--style`: Architectural style to analyze (`layered`, `hexagonal`, `clean`, `event_driven`, `microservices`)
- `--mock`: Use mock implementation for faster analysis

#### Examples:

```bash
# Analyze a layered architecture
python run_component_visualization.py examples/layered_architecture

# Analyze event-driven architecture with a custom title
python run_component_visualization.py examples/event_driven --style event_driven --title "Event-Driven Architecture Analysis"

# Specify a custom output file and directory
python run_component_visualization.py src/ --output my_visualization.html --output-dir ./visualizations
```

### Using the Dashboard

The Dashboard provides an integrated visualization experience with interactive controls and multiple visualization types:

1. Open the web UI by running:
   ```bash
   python -m src.web.app
   ```

2. Navigate to a project's dashboard
3. Click the "Architecture" tab to access the visualization interface

## Visualization Types

### Force-Directed Graph

The force-directed graph visualization represents components as nodes and dependencies as edges, using physics-based layout to position related components near each other.

#### Interaction:

- **Pan**: Click and drag in empty space
- **Zoom**: Use mouse wheel or pinch gesture
- **Select Component**: Click on a node to see details
- **Move Component**: Drag a node to reposition it
- **Reset View**: Click the "Reset View" button

#### Grouping Options:

- **Layer**: Group components by architectural layer
- **Component Type**: Group by class, function, or module
- **Module**: Group by source directory
- **None**: Pure force-directed layout

#### Controls:

- **Visualization Type**: Select from different visualization styles
- **Group By**: Change the grouping method
- **Show Violations**: Toggle visibility of architectural violations
- **Reset View**: Return to default zoom and position

### Reading the Visualization

#### Node Colors:

- **Green**: Presentation layer
- **Blue**: Business layer
- **Orange**: Data access layer
- **Purple**: Domain layer
- **Gray**: Unknown or uncategorized

#### Node Size:

Larger nodes indicate components with more connections or higher importance.

#### Edge Types:

- **Solid Gray Line**: Normal dependency
- **Dashed Red Line**: Architectural violation

#### Component Details:

Click on a component to see:
- Name
- Type
- Layer
- File path
- Number of connections

## Interpreting Architectural Patterns

### Layered Architecture

In a layered architecture visualization:
- Components should be grouped by layer
- Dependencies should generally flow downward
- Few or no upward dependencies (violations)

### Event-Driven Architecture

In an event-driven architecture:
- Event producers and consumers should be visible
- The event bus should be central
- Components should connect primarily through events

### Dependency Inversion

In a system with dependency inversion:
- High-level modules depend on abstractions
- Low-level modules also depend on abstractions
- Few direct dependencies between components

## Tips for Analysis

1. **Start with the Overview**: First examine the overall structure to identify clusters and major components

2. **Look for Architectural Violations**: Red dashed lines indicate dependencies that violate architectural principles

3. **Identify Central Components**: Larger nodes with many connections may be candidates for refactoring

4. **Check Layer Separation**: In layered architectures, ensure components are properly separated by layer

5. **Compare Different Groupings**: Switch between grouping options to gain different perspectives on the codebase

## Troubleshooting

If visualizations appear empty or have no connections:
- Ensure the analyzed directory contains supported file types
- Try the `--mock` option for more permissive analysis
- Check if the architectural style matches the codebase

## Next Steps

After exploring visualizations:
1. Review architectural violations identified in the visualization
2. Consider refactoring highly coupled components
3. Enforce architectural boundaries in your development process
4. Document architectural decisions based on visualization findings

## Example Interpretations

### Healthy Layered Architecture

A healthy layered architecture visualization will show:
- Clear separation between layers
- Dependencies flowing primarily downward
- Few tightly coupled components
- No circular dependencies

### Problematic Patterns

Watch for these warning signs:
- Circular dependencies between components
- Components with too many connections
- Dependencies that bypass layers
- Isolated components with no connections