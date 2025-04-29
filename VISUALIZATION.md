# Advanced Visualization in Code Pattern Analyzer

The Code Pattern Analyzer includes sophisticated visualization capabilities to help you understand code architecture, relationships between components, and potential issues in your codebase.

## Visualization Types

### 1. Force-Directed Component Graph

This interactive visualization shows components and their relationships using a physics-based force-directed layout algorithm. It allows you to:

- See all components in your codebase
- Understand how components are related
- Identify dependency cycles and architectural violations
- Group components by layer, module, or type
- Filter components to focus on specific areas

### 2. Architecture Visualization

Specialized visualizations for different architectural styles:

- **Layered Architecture**: Shows layers and inter-layer dependencies
- **Hexagonal Architecture**: Visualizes the core, ports, and adapters
- **Clean Architecture**: Displays entities, use cases, interfaces, and frameworks
- **Event-Driven Architecture**: Shows event producers, consumers, and message flows
- **Microservices Architecture**: Displays service boundaries and communication patterns

### 3. Anti-Pattern Visualization

Helps you identify and understand architectural anti-patterns:

- **Dependency Cycles**: Shows circular dependencies between components
- **God Components**: Visualizes overly complex components with too many responsibilities
- **Tight Coupling**: Highlights components with excessive dependencies
- **Architectural Erosion**: Shows where architectural boundaries have been violated

## Using Visualizations

### Command Line

Generate visualizations using the provided scripts:

```bash
# Generate a force-directed component visualization
python run_component_visualization.py /path/to/project --style layered

# Analyze and visualize architectural anti-patterns
python run_anti_pattern_analysis.py /path/to/project

# Compare different architectural approaches
python compare_architectures.py

# Visualize architecture evolution over time
python simulate_architecture_evolution.py

# Using CLI commands
code-pattern visualize /path/to/project --pattern layered_architecture
```

### Web Interface

The web interface provides an interactive way to generate and explore visualizations:

1. Start the web interface:
   ```bash
   ./scripts/start_web_ui.sh
   ```

2. Navigate to http://localhost:3000 in your browser

3. Upload your project or select an existing one

4. Click "Visualize" to generate interactive visualizations

### Sharing Visualizations

You can create portable, self-contained visualizations to share with others:

```bash
# Create a portable visualization bundle
python view_visualization.py --bundle reports/component_visualization.html --output-dir ./portable_visualizations
```

This creates a directory with the visualization and all required files that can be shared with others.

## Visualization Features

### Interactive Components

- **Zoom & Pan**: Navigate through large visualizations
- **Filtering**: Focus on specific components or layers
- **Grouping**: Organize components by various criteria
- **Component Details**: Click on components to see detailed information
- **Highlighting**: Emphasize violations and important relationships

### Customization Options

Customize your visualizations with various options:

```bash
# Customize the visualization
python run_component_visualization.py /path/to/project \
  --style layered \
  --title "My Project Architecture" \
  --output custom_visualization.html \
  --open
```

## Technical Implementation

The visualizations are built using:

- **HTML/CSS**: For responsive layout and styling
- **D3.js**: For interactive, data-driven visualizations
- **JavaScript**: For dynamic user interactions
- **SVG**: For scalable vector graphics
- **Chart.js**: For statistical charts and graphs

Implementation principles:

1. **Interactive**: Users can explore the visualization by interacting with elements
2. **Responsive**: Layouts adjust to different screen sizes
3. **Accessible**: Clear visual indicators with text alternatives
4. **Detailed**: Providing comprehensive information while maintaining clarity
5. **Actionable**: Including specific recommendations based on findings

## Examples

The repository includes several example projects with pre-generated visualizations:

- `examples/layered_architecture/` - Classic layered architecture example
- `examples/dependency_inversion/` - Example showing dependency inversion principle
- `examples/event_driven/` - Event-driven architecture with CQRS and event sourcing
- `examples/information_hiding/` - Information hiding principle in action

## Best Practices

- Generate visualizations regularly as your codebase evolves
- Compare visualizations over time to identify architectural drift
- Share visualizations with your team to ensure common understanding
- Use visualizations during code reviews to maintain architectural integrity
- Combine multiple visualization types for comprehensive understanding

## Sample Output

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