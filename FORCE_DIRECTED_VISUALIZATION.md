# Force-Directed Component Visualization

This document describes the implementation of the force-directed graph visualization for component relationships in the Code Pattern Analyzer.

## Overview

The force-directed graph visualization provides an interactive, intuitive way to explore component relationships in a codebase. It represents components as nodes and dependencies as edges, using physics-based layout algorithms to position related components close together while separating unrelated ones.

## Features

### Interactive Graph Visualization

- **Force-Directed Layout**: Components naturally organize based on their relationships
- **Zoom and Pan**: Explore complex graphs at different levels of detail
- **Draggable Nodes**: Reposition components for better visualization
- **Component Selection**: Click on components to view detailed information
- **Relationship Highlighting**: See dependencies and violations clearly

### Flexible Grouping Options

- **Layer-Based Grouping**: Components arranged by architectural layer
- **Type-Based Grouping**: Group by component type (class, function, module)
- **Module-Based Grouping**: Organize by source code module/directory
- **No Grouping**: Pure force-directed layout based only on dependencies

### Filtering Capabilities

- **Layer Filtering**: Focus on specific architectural layers
- **Violation Highlighting**: Toggle visibility of architectural violations
- **Connected Component Display**: Automatically show related components

### Detailed Component Information

- **Component Details Panel**: View detailed information about selected components
- **Comprehensive Metadata**: See component type, layer, file path, and connections
- **Visual Indicators**: Node size indicates connection count and importance

## Technical Implementation

### Backend Components

1. **`ForceDirectedVisualizer` Class**
   - Generates HTML for the visualization
   - Injects graph data into the page
   - Provides styling and interactive JavaScript

2. **`run_component_visualization.py` Script**
   - Command-line tool for generating visualizations
   - Extracts component graph from architectural style analysis
   - Formats data for the visualizer

### Frontend Integration

The visualization is integrated into the Dashboard UI with:

1. **Visualization Container**
   - Embedding the visualization via iframe
   - Controls for customizing the display

2. **Control Panel**
   - Visualization type selector
   - Grouping options
   - Filtering controls
   - View reset button

3. **Interactive Legend**
   - Color-coded layer indicators
   - Line style indicators for dependencies and violations

### D3.js Visualization Engine

The heart of the visualization is a D3.js-based rendering engine that provides:

1. **Physics-Based Layout**
   - Force simulation with attraction and repulsion
   - Collision detection to prevent node overlap
   - Customizable forces based on grouping selection

2. **Interactive Elements**
   - Draggable nodes with physics simulation
   - Zoom and pan behavior
   - Component selection
   - Tooltips and details panel

3. **Visual Encoding**
   - Node color indicates architectural layer
   - Node size represents connection count and importance
   - Line styles show dependencies and violations
   - Animated transitions for state changes

## Usage

### Command Line

```bash
python run_component_visualization.py /path/to/project --style layered --output visualization.html
```

Options:
- `--style`: Architectural style to visualize (layered, hexagonal, clean, event_driven, microservices)
- `--output`: Output HTML file path
- `--title`: Visualization title
- `--mock`: Use mock implementation

### Web Interface

In the Dashboard, select the Architecture tab to access the visualization with interactive controls:

1. Choose visualization type from the dropdown
2. Select grouping method
3. Toggle violation highlighting
4. Reset the view if needed

## Examples

### Layered Architecture Visualization

A layered architecture visualization typically shows:

- Presentation layer components at the top
- Business logic in the middle
- Data access and domain components at the bottom
- Dependencies flowing primarily downward
- Violations highlighted as dashed red lines

### Dependency Cycles

The visualization makes circular dependencies immediately apparent:

1. Components involved in cycles are positioned close together
2. The circular arrangement of arrows reveals the cycle
3. Violations are highlighted with dashed red lines
4. The details panel shows specific dependency information

## Implementation Details

### Data Structure

The graph data is structured as:

```json
{
  "nodes": [
    {
      "id": "unique_id",
      "name": "ComponentName",
      "type": "class|function|module",
      "layer": "presentation|business|data_access|domain",
      "file": "/path/to/file.js"
    }
  ],
  "links": [
    {
      "source": "source_id",
      "target": "target_id",
      "type": "dependency",
      "violation": true|false
    }
  ]
}
```

### Customization

The visualization can be customized with:

1. **Color Schemes**: Modify CSS variables to create different visual themes
2. **Layout Parameters**: Adjust force strengths, distances, and collision radiuses
3. **Node Sizing**: Change the algorithm for determining node importance
4. **Grouping Forces**: Add or modify the grouping strategies

## Future Enhancements

1. **Time-Series Visualization**: Show how component relationships evolve over time
2. **Cluster Analysis**: Automatically detect and highlight component clusters
3. **Comparative Views**: Compare different architectural styles side by side
4. **3D Visualization**: Extend to three dimensions for more complex relationships
5. **Interactive Editing**: Allow architectural refactoring suggestions directly in the visualization

## Conclusion

The force-directed component visualization transforms abstract architectural concepts into intuitive, explorable diagrams. By providing interactive tools for exploring component relationships, it bridges the gap between high-level architectural understanding and concrete code structures, making architectural thinking accessible to all developers.