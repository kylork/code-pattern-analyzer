# Demo Mode and Report Generation

The Code Pattern Analyzer includes features to help you quickly get started and share your results with others.

## Demo Mode

The demo mode lets you try out the analyzer without having to provide your own codebase. This is perfect for:
- Getting familiar with the tool's capabilities
- Exploring different architectural styles
- Testing visualization features
- Training team members

### Using Demo Mode

1. Launch the Code Pattern Analyzer GUI:
   ```bash
   python code_pattern_analyzer_gui.py
   ```

2. Click on the "Demo" tab in the left sidebar.

3. Browse the available demo projects:
   - **Layered Architecture Example**: A classic layered architecture with controllers, services, and repositories
   - **Dependency Inversion Example**: Shows dependency inversion principle implementation
   - **Event-Driven Architecture Example**: Demonstrates event-driven systems with publishers, subscribers, and event bus
   - **Information Hiding Example**: Showcases information hiding principles with well-defined interfaces

4. Click the "Run Demo Analysis" button on any demo project card.

5. The analysis will run automatically, and when complete, the visualization will appear in the "Available Visualizations" section.

6. Click "Open Visualization" to explore the results.

### Sample Insights from Demo Projects

Each demo project highlights different architectural concepts:

#### Layered Architecture Example

- Clear separation between UI, business logic, and data access layers
- Proper dependency direction (top-down)
- Identifiable components in each layer

#### Dependency Inversion Example

- High-level modules depending on abstractions
- Low-level modules implementing interfaces
- Inversion of control patterns

#### Event-Driven Architecture Example

- Publishers producing events
- Event bus managing distribution
- Subscribers consuming events
- Asynchronous communication patterns

#### Information Hiding Example

- Encapsulation principles
- Public interfaces with hidden implementations
- Separation of concerns

## Report Generation

The report generation feature allows you to create shareable, portable bundles of your analysis results. This is ideal for:
- Sharing findings with team members
- Including in documentation
- Archiving analysis results
- Distributing to stakeholders without requiring them to install the tool

### Generating Reports

1. Launch the Code Pattern Analyzer GUI:
   ```bash
   python code_pattern_analyzer_gui.py
   ```

2. Run an analysis or view an existing visualization.

3. In the "Available Visualizations" section, find the visualization you want to report.

4. Click the "Generate Report" button next to the visualization.

5. The report generation will start, and you'll see a status update when it completes.

6. The report bundle will be created in a directory like:
   ```
   output/report_bundle_1683456789/
   ```

### Report Bundle Structure

Each report bundle contains:

- **HTML Visualization File**: The interactive visualization
- **README.txt**: Instructions for viewing the visualization
- **Resource Files**: Any supporting files (CSS, JavaScript, images)

### Sharing Reports

To share a report with others:

1. Locate the bundle directory (shown in the success message after generation)
2. Compress the entire directory into a ZIP file:
   ```bash
   cd output/
   zip -r report_bundle_1683456789.zip report_bundle_1683456789/
   ```
3. Share the ZIP file with your colleagues
4. Recipients can extract the ZIP file and follow the instructions in README.txt to view the visualization

### Viewing Shared Reports

When you receive a report bundle:

1. Extract the ZIP file to a directory on your computer
2. Open the HTML file in a modern web browser
3. The visualization will load with all interactive features intact

No installation of the Code Pattern Analyzer is required to view shared reports.

## Command-Line Alternatives

You can also use command-line tools for these features:

### Demo Projects from Command Line

```bash
# Run analysis on the layered architecture demo
python run_code_pattern_linkage.py examples/layered_architecture --style layered --output demo_layered.html
```

### Report Generation from Command Line

```bash
# Generate a portable bundle from an existing visualization
python view_visualization.py --bundle output/visualization.html --output-dir ./portable_visualizations
```

## Best Practices

1. **Demo Mode for Learning**: Use demo projects to learn about different architectural patterns before analyzing your own code.

2. **Documentation**: Include generated reports in your project documentation to communicate architectural decisions.

3. **Team Onboarding**: Use demo mode and shared reports to help new team members understand your project architecture.

4. **Before/After Comparisons**: Generate reports before and after refactoring to document architectural improvements.

5. **Regular Reviews**: Schedule periodic architecture reviews using the analyzer and share reports with stakeholders.