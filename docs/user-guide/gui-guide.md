# Code Pattern Analyzer - GUI Guide

This guide explains how to use the Code Pattern Analyzer's graphical user interface for analyzing and visualizing code architecture.

## Launching the GUI

The Code Pattern Analyzer provides a unified web-based GUI that makes all of its capabilities accessible through a single interface:

```bash
# Start the Code Pattern Analyzer GUI
python code_pattern_analyzer_gui.py

# Optionally specify host and port
python code_pattern_analyzer_gui.py --host 0.0.0.0 --port 8888
```

This will start the web server and automatically open the GUI in your default browser. If the browser doesn't open automatically, you can manually navigate to:

```
http://localhost:8080
```

Or replace the port number with the one you specified.

## Main Interface

The GUI has two main sections:

1. **Analysis Panel** (left): Where you configure and run analyses
2. **Visualizations Panel** (right): Where you view and interact with results

### Running an Analysis

To analyze a codebase:

1. Enter the full path to the project directory in the "Project Directory" field
2. Select an architectural style from the dropdown (or leave the default)
3. Click "Analyze Project"

The status panel will show the progress of the analysis. Once complete, the visualization will be added to the list on the right.

### Viewing Visualizations

The right panel displays all available visualizations:

- Each visualization card shows the filename, creation date, and size
- Click the "Open Visualization" button to view an interactive visualization
- The visualization will open in a new browser tab

## Visualization Types

The Code Pattern Analyzer generates three main types of visualizations:

### 1. Component Visualization

Shows the components in your codebase and their relationships:

- **Nodes**: Represent components (classes, modules, packages)
- **Edges**: Represent relationships (dependencies, inheritance, etc.)
- **Colors**: Indicate component types or architectural layers
- **Interactive**: Hover for details, click to select, drag to rearrange

### 2. Code-Pattern Linkage

Connects architectural components directly to their code implementations:

- **Graph View**: Displays component relationships
- **Code View**: Shows actual code snippets when components are selected
- **Bidirectional**: Select components to see code, or search code to find components
- **Syntax Highlighting**: Makes code easier to read and understand

### 3. Architecture Analysis Reports

Provides detailed analysis of architectural patterns and potential issues:

- **Overview**: Summary of detected architecture
- **Pattern Detection**: Identified architectural patterns
- **Violations**: Highlights architectural rule violations
- **Metrics**: Quantitative measurements of code quality and architecture

## Common Tasks

### Analyzing a New Project

1. Enter the path to your project directory
2. Select the architectural style that best matches your project:
   - **Layered**: Traditional horizontal layers (UI, business logic, data access)
   - **Hexagonal**: Core domain with adapters to external systems
   - **Clean**: Separation of entities, use cases, interfaces, and frameworks
   - **Event-driven**: Components communicate through events
   - **Microservices**: Distributed services with clear boundaries
3. Click "Analyze Project"

### Exploring Component Relationships

In the visualization:
- **Zoom**: Use mouse wheel or pinch gesture
- **Pan**: Click and drag the background
- **Select**: Click on a component to view details
- **Rearrange**: Drag components to customize the layout
- **Hover**: Mouse over elements to see additional information

### Finding Architectural Issues

1. Run an analysis of your project
2. Open the visualization
3. Look for highlighted violations (usually in red)
4. Check the violations section for details on each issue
5. Review the code snippets to understand the context

### Sharing Results

The GUI provides several ways to share analysis results:

1. **Direct URL**: Share the visualization URL with team members
2. **Portable Bundle**:
   - Create a portable bundle using the command line:
     ```bash
     python view_visualization.py --bundle output/visualization.html --output-dir ./portable_visualizations
     ```
   - Share the entire bundle folder with others

## Keyboard Shortcuts

While using the visualizations:

- **F**: Focus on selected component
- **R**: Reset the view
- **+/-**: Zoom in/out
- **S**: Save current view (where supported)
- **H**: Toggle help overlay

## Advanced Options

The GUI supports additional options that can be accessed through command-line parameters:

```bash
# Show help information
python code_pattern_analyzer_gui.py --help
```

Common options include:
- `--host`: IP address to bind to (default: localhost)
- `--port`: Port to use (default: 8080)
- `--debug`: Enable debug mode for more detailed logging
- `--no-browser`: Don't automatically open the browser

## Troubleshooting

If you encounter issues with the GUI:

1. **Visualization doesn't load**
   - Check that the server is running (terminal should show activity)
   - Ensure your browser supports modern JavaScript features
   - Try a different browser if problems persist

2. **Analysis fails**
   - Verify the project path is correct and accessible
   - Check that the directory contains code in supported languages
   - Look for error messages in the status panel

3. **Browser doesn't open automatically**
   - Manually navigate to http://localhost:8080 (or your custom port)
   - Check if a firewall is blocking the connection
   - Try running with `--host 127.0.0.1` explicitly

## Next Steps

After getting familiar with the GUI:

1. Try analyzing different architectures (layered, hexagonal, etc.)
2. Compare analysis results between different codebases
3. Use the insights to improve your code architecture
4. Explore the visualizations to better understand your codebase