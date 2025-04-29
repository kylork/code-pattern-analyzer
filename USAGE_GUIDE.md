# Code Pattern Analyzer - Complete System Guide

This guide explains how to run and use the complete Code Pattern Analyzer system with all its integrated components.

## Overview

The Code Pattern Analyzer system consists of several integrated components:

1. **Main Code Pattern Analyzer GUI** - The central interface for code analysis and visualization
2. **Pattern Transformation Tool** - For applying design patterns to existing code
3. **Pattern Recommendation System** - For receiving recommendations on which patterns to apply

## Running the System

### Option 1: All-in-One Launcher

The simplest way to start the entire system is to use the provided launcher script:

```bash
python run_all_services.py
```

This will start all three services in the correct order with the appropriate ports.

### Option 2: Individual Services

You can also run each service individually:

```bash
# Main GUI (Port 8080)
python code_pattern_analyzer_gui.py

# Pattern Transformation GUI (Port 8082)
python pattern_transformation_gui.py

# Pattern Recommendation GUI (Port 8081)
python pattern_recommendation_gui.py
```

## Accessing the Interfaces

Once all services are running, you can access them at:

- **Main Interface**: http://localhost:8080
- **Pattern Transformation**: http://localhost:8082
- **Pattern Recommendation**: http://localhost:8081

The main interface also provides links to launch the other tools directly from its UI.

## Working with the Integrated System

### Analyzing Code

1. In the **Main GUI**, go to the "Analyze" tab
2. Enter the path to your code project
3. Select the architectural style to analyze for
4. Click "Analyze Project"

### Transforming Code with Design Patterns

1. From the **Main GUI**, go to the "Transform" tab
2. Click "Open Pattern Transformation Tool"
3. In the transformation tool, provide a file path or paste code
4. Select a pattern to apply from the detected opportunities
5. Review and customize the transformation
6. Apply the transformation

### Getting Pattern Recommendations

1. From the **Main GUI**, use the links to access the Pattern Recommendation tool
2. Enter the path to your code
3. Select which patterns to check for
4. Run the analysis to get recommendations

## Features

- **Architectural Pattern Detection** - Identify existing architectural patterns
- **Code Visualization** - Visualize code structure and relationships
- **Pattern Transformation** - Apply design patterns to improve code
- **Pattern Recommendations** - Get smart suggestions for design improvements

## Recent Transformations

When you apply pattern transformations, they will appear in the "Recent Transformations" section in the main GUI's Transform tab. From there, you can view the transformed files directly.

## Generating Reports

The main GUI allows you to generate shareable reports from visualizations and analyses. These reports can be accessed from the "Available Visualizations" section.