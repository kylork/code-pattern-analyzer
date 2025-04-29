# Creating Example Architecture Projects

The Code Pattern Analyzer includes a tool to generate example projects with specific architectural styles. These example projects are perfect for:

1. Learning about different architectural patterns
2. Testing the analyzer on known architecture types
3. Teaching software architecture principles
4. Comparing different architectural approaches

## Using the Example Project Creator

The `create_example_project.py` script generates fully-functional Python projects that demonstrate specific architectural styles.

```bash
# Create a layered architecture example
python create_example_project.py --style layered --output ./my_examples/layered

# Create a hexagonal architecture example
python create_example_project.py --style hexagonal --output ./my_examples/hexagonal

# Create a clean architecture example
python create_example_project.py --style clean --output ./my_examples/clean
```

## Available Architectural Styles

### Layered Architecture

```bash
python create_example_project.py --style layered
```

Creates a classic three-tier architecture with:
- **UI Layer**: Controllers and views
- **Business Logic Layer**: Services
- **Data Access Layer**: Repositories and models

Perfect for understanding traditional layered applications where dependencies flow downward.

### Hexagonal Architecture

```bash
python create_example_project.py --style hexagonal
```

Creates a ports and adapters architecture with:
- **Domain Core**: Models and services
- **Ports**: Interface definitions
- **Adapters**: Implementations for different contexts (web, database, etc.)

Great for understanding dependency inversion and domain isolation.

### Clean Architecture

```bash
python create_example_project.py --style clean
```

Creates a clean architecture with:
- **Entities Layer**: Core business models
- **Use Cases Layer**: Application business rules
- **Interface Adapters Layer**: Controllers and interfaces
- **Frameworks Layer**: External frameworks and tools

Demonstrates how dependencies point inward toward higher-level policies.

## Running the Examples

Each generated example includes a complete, runnable application:

```bash
cd my_examples/layered
python app.py
```

The example applications simulate API operations and demonstrate how the different architectural components interact.

## Analyzing Generated Examples

After creating an example, you can analyze it with the Code Pattern Analyzer:

```bash
# Generate a visualization of the example
python run_code_pattern_linkage.py my_examples/layered --style layered

# View the visualization
python view_visualization.py output/layered_architecture_visualization.html
```

This allows you to see how the analyzer detects and visualizes the architectural patterns in the generated code.

## Learning Path

For a comprehensive learning experience, follow these steps:

1. Generate examples of all three architectural styles:
   ```bash
   python create_example_project.py --style layered --output ./examples/layered
   python create_example_project.py --style hexagonal --output ./examples/hexagonal
   python create_example_project.py --style clean --output ./examples/clean
   ```

2. Study each example's code and README to understand the architectural principles.

3. Run each example to see how they work:
   ```bash
   cd examples/layered && python app.py
   cd examples/hexagonal && python app.py
   cd examples/clean && python app.py
   ```

4. Analyze each example with the Code Pattern Analyzer:
   ```bash
   python run_code_pattern_linkage.py examples/layered --style layered
   python run_code_pattern_linkage.py examples/hexagonal --style hexagonal
   python run_code_pattern_linkage.py examples/clean --style clean
   ```

5. Compare the visualizations to understand how the architectural differences appear in the analysis.

## Customizing Examples

You can modify the generated examples to experiment with architectural variations:

1. Add new components to see how they affect the architecture.
2. Deliberately introduce architectural violations to see how they appear in the analysis.
3. Refactor an example from one architectural style to another.

This hands-on approach helps solidify your understanding of architectural patterns and how they're detected by the Code Pattern Analyzer.

## Using Examples for Presentations

The generated examples and their visualizations make excellent educational materials:

1. Generate examples and visualizations.
2. Create a report bundle for sharing:
   ```bash
   python view_visualization.py --bundle output/layered_architecture_visualization.html
   ```
3. Include the bundle in your presentations or documentation.

This provides a complete, interactive demonstration of architectural patterns and their analysis.