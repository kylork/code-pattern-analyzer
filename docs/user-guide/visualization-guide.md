# Code Pattern Analyzer - Visualization Guide

This guide explains how to use and interpret the different visualizations produced by the Code Pattern Analyzer.

## Visualization Types

The Code Pattern Analyzer offers several types of visualizations to help you understand your codebase's architecture:

### 1. Force-Directed Graph

![Force-Directed Graph](../images/force_directed_example.png)

This is the primary visualization type used to show components and their relationships:

- **Nodes**: Represent components (classes, modules, packages, services)
- **Edges**: Represent relationships between components (dependencies, inheritance, etc.)
- **Colors**: Indicate component types or architectural layers
- **Size**: Often represents complexity or importance

#### Interaction Features:

- **Zoom**: Mouse wheel to zoom in/out
- **Pan**: Click and drag the background
- **Select**: Click on nodes to view details
- **Drag**: Move nodes to rearrange the layout
- **Hover**: See detailed information about components

### 2. Code-Pattern Linkage

![Code-Pattern Linkage](../images/code_pattern_linkage_example.png)

This visualization connects architectural components directly to their code implementations:

- **Split View**: Graph visualization on one side, code snippets on the other
- **Bidirectional Linking**: Select components to see code, or find components from code
- **Syntax Highlighting**: Makes code easier to read
- **Context View**: Shows surrounding code for better understanding

#### Using Code-Pattern Linkage:

1. Navigate the graph visualization on the left
2. Click on a component to select it
3. View the corresponding code snippet on the right
4. Use the navigation controls to explore related components

### 3. Architectural Style Visualizations

Different architectural styles have specialized visualizations:

#### Layered Architecture

![Layered Architecture](../images/layered_architecture_example.png)

- Horizontal layers (UI, business logic, data access)
- Arrows showing dependencies between layers
- Violation highlights for dependencies that break layering rules

#### Hexagonal Architecture

![Hexagonal Architecture](../images/hexagonal_architecture_example.png)

- Core domain in the center
- Ports and adapters around the periphery
- Clear separation between business logic and external systems

#### Event-Driven Architecture

![Event-Driven Architecture](../images/event_driven_example.png)

- Components connected through event channels
- Publishers and subscribers clearly marked
- Event flow visualization

## Interactive Features

All visualizations include interactive features to help you explore your code's architecture:

### Navigation Controls

- **Zoom Controls**: + and - buttons to zoom in and out
- **Reset View**: Button to reset the visualization to its default state
- **Full Screen**: Expand the visualization to fill the browser window

### Component Selection

- **Click**: Select a single component
- **Shift+Click**: Add to selection (select multiple components)
- **Hover**: Show brief information without changing selection

### Filtering and Highlighting

- **Filter Controls**: Filter components by type, name, or properties
- **Highlight Mode**: Emphasize specific patterns or violations
- **Focus Mode**: Concentrate on a selected component and its direct relationships

### Data Display

- **Details Panel**: Shows detailed information about selected components
- **Statistics View**: Displays metrics and quantitative data
- **Violation List**: Enumerates architectural rule violations

## Generating Visualizations

### From the GUI

1. Start the GUI:
   ```bash
   python code_pattern_analyzer_gui.py
   ```

2. Enter your project directory and select analysis options
3. Click "Analyze Project"
4. When analysis completes, click "Open Visualization"

### From the Command Line

#### Component Visualization

```bash
python run_component_visualization.py /path/to/project \
  --style layered \
  --output-dir ./output \
  --output visualization.html
```

#### Code-Pattern Linkage

```bash
python run_code_pattern_linkage.py /path/to/project \
  --style clean \
  --output-dir ./output \
  --output linkage_visualization.html
```

#### Viewing Visualizations

```bash
# Open directly in browser
python view_visualization.py output/visualization.html

# Start a local server (better for large visualizations)
python view_visualization.py --server output/

# Create a portable bundle for sharing
python view_visualization.py --bundle output/visualization.html --output-dir ./portable_visualizations
```

## Interpreting Visualizations

### Component Relationships

- **Solid Lines**: Direct dependencies
- **Dashed Lines**: Indirect dependencies
- **Red Lines**: Dependency violations
- **Arrow Direction**: Direction of dependency (points to the dependency)

### Color Coding

Typical color scheme (may vary by visualization type):

- **Blue**: UI components
- **Green**: Business logic
- **Yellow**: Data access components
- **Red**: External systems/dependencies
- **Purple**: Utilities/helpers
- **Orange**: Warning/violation indicators

### Metrics and Indicators

Visualizations may include various metrics:

- **Complexity Score**: Indicates component complexity
- **Dependency Count**: Number of dependencies
- **Violation Count**: Number of architectural rule violations
- **Coupling Score**: Measure of component interdependence

## Exporting and Sharing

### Export Formats

- **HTML**: Interactive visualization viewable in any modern browser
- **PNG/SVG**: Static image export for documentation (where available)
- **JSON**: Raw data export for further processing

### Sharing Options

- **Portable Bundle**: Self-contained package including HTML and assets
- **Direct URL**: Share the URL if using a hosted server
- **Embedded**: Some visualizations can be embedded in documentation

## Advanced Visualization Techniques

### Custom Styling

Visualizations can be customized by editing the generated HTML:

1. Generate the visualization
2. Open the HTML file in a text editor
3. Modify the CSS styles in the `<style>` section
4. Save and reload in browser

### Integration with Documentation

Visualizations can be integrated into project documentation:

1. Generate static images from visualizations
2. Include images in markdown/documentation
3. Link to interactive versions for detailed exploration

### Comparative Analysis

Compare architecture across projects or versions:

1. Generate visualizations for different projects/versions
2. Use side-by-side comparison
3. Look for pattern differences, added dependencies, or new violations

## Best Practices

1. **Start with an Overview**: Begin with high-level visualizations before diving into details
2. **Look for Patterns**: Identify recurring patterns and structures
3. **Focus on Violations**: Pay special attention to highlighted violations
4. **Compare with Intent**: Evaluate how well the actual architecture matches the intended design
5. **Share with Team**: Use visualizations to facilitate architectural discussions

## Troubleshooting

### Visualization Not Loading

- Check browser console for JavaScript errors
- Ensure all required assets are being loaded
- Try a different browser

### Incomplete or Incorrect Visualization

- Verify that the analyzer has access to all relevant code files
- Check for parsing errors in the analysis output
- Try using a different architectural style that may better match your code

### Performance Issues

- For large codebases, use filtering to focus on specific areas
- Increase browser memory limits for very large visualizations
- Consider breaking analysis into smaller components