# Architectural Intent Detection

This document describes the architectural intent detection capabilities added to the Code Pattern Analyzer.

## Overview

The architectural intent detection system identifies high-level architectural patterns and principles in a codebase, going beyond specific design patterns like Singleton or Observer. This helps developers understand the overall architectural approach and evaluate how well the codebase adheres to architectural principles.

## Key Features

- **Separation of Concerns Analysis**: Detects how well a codebase separates different responsibilities
- **Layer-based Architecture Detection**: Identifies layers (controller, service, repository, model) and analyzes their relationships
- **Domain-based Separation Analysis**: Analyzes how well the codebase separates by business domains
- **Architectural Health Scoring**: Provides overall and specific scores for architectural health
- **Visualization**: Generates text or HTML reports showing architectural insights

## Implementation Details

### Component Graph Analysis

The system builds a graph of components (files) and their relationships to analyze the architectural structure:

1. **Nodes**: Represent files/components in the codebase
2. **Edges**: Represent dependencies between components (via imports)
3. **Node Properties**: Include layer, domain, and responsibilities
4. **Analysis Metrics**: Layer diversity, clean layering score, domain isolation score

### Separation of Concerns Detection

The system detects layer-based and domain-based separation of concerns:

1. **Layer-based Separation**: Identifies components by their layer (controller, service, repository, model)
2. **Domain-based Separation**: Groups components by business domain (user, product, order, etc.)
3. **Responsibility Analysis**: Extracts component responsibilities from method names and patterns
4. **Dependency Analysis**: Examines cross-layer and cross-domain dependencies

### Reports and Visualization

The system provides multiple formats for viewing architectural analysis:

1. **Text Reports**: Detailed text output showing all analysis results
2. **HTML Reports**: Interactive visualization of architectural structure
3. **JSON Output**: Machine-readable analysis for integrating with other tools

## Usage

### CLI Command

```bash
python -m src.cli architecture <directory> [options]
```

Options:
- `--output/-o`: Output file for the report
- `--format`: Output format (json, text, html)
- `--real/--mock`: Use real or mock implementation

### Helper Script

For direct usage, you can also use the helper script:

```bash
python run_architecture_analysis.py <directory> [output_format]
```

## Example

The included layered architecture example demonstrates a typical layer-based architecture:

- **Controllers**: Handle HTTP requests and responses
- **Services**: Implement business logic
- **Repositories**: Handle data access
- **Models**: Define data structures

The analyzer detects this structure and provides insights into how well the architecture is implemented.

## Next Steps

- Additional architectural intent patterns (Information Hiding, Dependency Inversion)
- Enhanced visualization with interactive component graphs
- Machine learning-based pattern detection for more complex architectures
- Support for more programming languages and frameworks