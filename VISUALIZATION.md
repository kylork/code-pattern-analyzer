# Architectural Pattern Visualization

The Code Pattern Analyzer now includes advanced visualization capabilities for architectural patterns. This document provides an overview of the visualization features and how to use them.

## Overview

Visualizing architectural patterns helps in:

1. Better understanding of complex code organization
2. Identifying potential issues in the architecture
3. Communicating architectural concepts to team members
4. Documenting architectural decisions and evolution

## Supported Visualizations

### Layered Architecture

The layered architecture visualization provides:

- Visual representation of all detected layers
- Component counts for each layer
- Interactive dependency graph showing connections between layers
- Highlighting of dependency violations
- Detailed statistics on violations
- Recommendations for improving the architecture

#### Sample Output

The layered architecture visualization includes:

1. **Overview Section**
   - Confidence meter indicating detection confidence
   - Description of the detected architecture
   - Summary of findings

2. **Layer Composition Section**
   - Bar chart showing component distribution across layers
   - List of key components in each layer

3. **Dependency Graph**
   - Interactive D3.js visualization of layer dependencies
   - Color-coded nodes representing different layers
   - Directed arrows showing dependencies
   - Dashed red lines indicating violations

4. **Violation Analysis**
   - Count of dependency violations
   - Breakdown by source and target layers
   - Most common violation patterns
   - Detailed list of specific violations

5. **Recommendations**
   - Actionable suggestions for improving the architecture
   - Specific advice based on detected issues

## Usage

### Command-line

To generate visualizations from the command line:

```bash
# Visualize the layered architecture in a project
code-pattern visualize /path/to/project --pattern layered_architecture

# Analyze and visualize in one command
code-pattern analyze /path/to/project --visualize
```

### Programmatic Usage

You can use the visualization components directly in your code:

```python
from src.patterns.architectural_styles import LayeredArchitecturePattern
from src.visualization import LayeredArchitectureVisualizer

# Run the analysis
pattern = LayeredArchitecturePattern()
results = pattern.analyze('/path/to/project')

# Create the visualizer and generate the visualization
visualizer = LayeredArchitectureVisualizer()
output_path = visualizer.visualize(results)

print(f"Visualization saved to: {output_path}")
```

### Demo Script

For a quick demonstration of the visualization capabilities, you can run:

```bash
# Run the layered architecture visualization demo
./visualize_layered_architecture.py
```

This will create a sample layered architecture analysis with both valid and invalid dependencies, and generate a visualization in the `reports/` directory.

## Technical Implementation

The visualizations are built using:

- HTML/CSS for layout and styling
- D3.js for interactive graphs
- JS for user interactions
- SVG for vector graphics

The implementation follows these principles:

1. **Interactive**: Users can explore the visualization by interacting with elements
2. **Responsive**: Layouts adjust to different screen sizes
3. **Accessible**: Clear visual indicators with text alternatives
4. **Detailed**: Providing comprehensive information while maintaining clarity
5. **Actionable**: Including specific recommendations based on findings

## Future Plans

We plan to extend the visualization capabilities to include:

1. **Other Architectural Styles**
   - Hexagonal/Ports and Adapters architecture
   - Clean architecture
   - Microservices architecture
   - Event-driven architecture

2. **Enhanced Interactive Features**
   - Filtering options for large codebases
   - Zooming and panning for complex graphs
   - Collapsible sections for focused analysis
   - Saved view states for sharing

3. **Timeline Views**
   - Showing architectural evolution over time
   - Comparing architecture between versions
   - Tracking migration progress

4. **Integration with IDEs**
   - Visual Studio Code extension
   - IntelliJ IDEA plugin
   - Real-time architectural guidance