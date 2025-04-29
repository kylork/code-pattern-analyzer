# Refactoring Engine

The Code Pattern Analyzer's Refactoring Engine provides powerful capabilities for analyzing code, generating refactoring suggestions, and automatically applying transformations to improve code quality.

## Overview

The Refactoring Engine works by analyzing your codebase from multiple perspectives:

- Detecting complex code that could benefit from simplification
- Identifying opportunities to apply design patterns
- Finding flow control and data flow issues
- Detecting architectural problems

Based on this analysis, it suggests specific, actionable refactorings and can automate the application of these changes.

## Features

### 1. Multi-source Suggestion Generation

The refactoring engine analyzes code from multiple perspectives:

- **Complexity Metrics**: Identifies methods and functions with high cyclomatic or cognitive complexity that would benefit from refactoring
- **Pattern Detection**: Recognizes code structures that could be improved by applying design patterns
- **Flow Analysis**: Detects issues in control flow (e.g., dead code, potential infinite loops) and data flow (e.g., unused variables)
- **Architectural Analysis**: Identifies architectural issues like dependency cycles and anti-patterns

### 2. Interactive Refactoring Workflow

The interactive refactoring tools allow you to:

- Review suggested refactorings with code previews
- See the benefits and impact of each suggestion
- Apply refactorings with a single command
- Edit suggested transformations before applying
- Skip refactorings that aren't appropriate

### 3. Automated Transformation

The transformation engine can automatically:

- Apply common refactorings like Extract Method
- Implement design patterns like Factory, Strategy, and Observer
- Fix simple issues like removing dead code
- Transform architectural components

### 4. Comprehensive Reporting

Refactoring reports provide:

- Impact-level classification (Critical, High, Medium, Low)
- Before/after code comparisons
- Expected benefits of each refactoring
- Interactive filtering by type and impact level
- Multiple output formats (HTML, JSON, text)

## Usage

### Generating Refactoring Suggestions

To generate refactoring suggestions for your codebase:

```bash
# Basic usage
code-pattern refactoring suggest /path/to/project

# Specify output format and file
code-pattern refactoring suggest /path/to/project --output report.html --format html

# Filter by analysis type
code-pattern refactoring suggest /path/to/project --analysis-type complexity

# Filter by minimum impact level
code-pattern refactoring suggest /path/to/project --min-impact high
```

### Interactive Refactoring Session

For an interactive session to review and apply refactorings:

```bash
# Start an interactive session
code-pattern refactoring interactive /path/to/project
```

The interactive session provides the following commands:
- `a` - Apply the current suggestion
- `s` - Skip the current suggestion
- `e` - Edit the transformed code before applying
- `d` - Show a unified diff of the before and after code
- `q` - Quit the interactive session
- `h` - Show help information

### Applying Design Pattern Transformations

To transform code to implement specific design patterns:

```bash
# Dry run (preview only)
code-pattern refactoring transform /path/to/project --pattern factory

# Apply changes
code-pattern refactoring transform /path/to/project --pattern factory --apply
```

Supported patterns:
- Factory Method
- Strategy
- Observer
- Decorator
- Composite

### Batch Refactoring

For automated application of multiple refactorings:

```bash
# Basic usage
./run_batch_refactoring.py /path/to/project

# Filter by minimum impact level
./run_batch_refactoring.py /path/to/project --min-impact high

# Filter by refactoring type
./run_batch_refactoring.py /path/to/project --refactoring-type EXTRACT_METHOD

# Dry run (no changes applied)
./run_batch_refactoring.py /path/to/project --dry-run
```

## Example Workflow

A typical refactoring workflow might look like this:

1. Generate suggestions:
   ```bash
   code-pattern refactoring suggest src/ --output refactorings.html --format html
   ```

2. Review the suggestions in the HTML report to get an overview

3. Start an interactive session to apply high-impact refactorings:
   ```bash
   code-pattern refactoring interactive src/ 
   ```
   (select 'high' as the minimum impact level when prompted)

4. Apply specific design pattern transformations:
   ```bash
   code-pattern refactoring transform src/ --pattern strategy --apply
   ```

5. Run automated tests to ensure refactorings didn't break functionality

## Technical Implementation

The Refactoring Engine is built with the following components:

- **Suggestion Generators**: Multiple analyzers that identify refactoring opportunities
- **Refactoring Suggestion Class**: Represents individual refactoring suggestions with details like description, impact, location, and code examples
- **Code Transformers**: Classes that apply specific refactorings to code
- **Interactive Session Handler**: Manages the interactive refactoring workflow
- **Report Generators**: Create HTML, JSON, and text reports of refactoring suggestions

## Extending the Refactoring Engine

The refactoring engine is designed to be extensible:

1. Create new suggestion generators by extending `SuggestionGenerator`
2. Implement new transformers by extending `CodeTransformer`
3. Add new refactoring types to the `RefactoringType` enum

For more details, see the [Refactoring Module README](/src/refactoring/README.md).