# Code Complexity Metrics

Code Pattern Analyzer includes robust capabilities for analyzing code complexity to help identify maintainability issues and refactoring opportunities. The complexity analysis module provides multiple metrics that give a comprehensive view of your codebase's complexity.

## Supported Metrics

### Cyclomatic Complexity

Cyclomatic Complexity measures the number of linearly independent paths through a program's source code. Developed by Thomas McCabe in 1976, it provides a quantitative measure of the complexity of code by counting:

- The number of decision points in code (if, while, for, case, etc.)
- Boolean operators in conditions (and, or)
- Each entry point to the code

Higher cyclomatic complexity indicates more complex code that is harder to understand, test, and maintain.

**Interpretation:**
- **1-10**: Low complexity - generally easy to maintain
- **11-20**: Moderate complexity - moderately difficult to maintain
- **21-30**: High complexity - difficult to maintain
- **>30**: Very high complexity - very difficult to maintain and test

### Cognitive Complexity

Cognitive Complexity measures how difficult code is to understand for humans. Developed by SonarSource, it considers:

- Nesting level (more nesting = higher complexity)
- Structural complexity (loops, conditionals, etc.)
- Additional cost for sequences, interrupts, and continuations

Cognitive complexity differs from cyclomatic complexity by focusing more on how humans perceive code rather than just counting logical paths.

**Interpretation:**
- **1-15**: Low complexity - easy to understand
- **16-30**: Moderate complexity - somewhat difficult to understand
- **31-50**: High complexity - difficult to understand
- **>50**: Very high complexity - extremely difficult to understand

### Maintainability Index

The Maintainability Index is a composite metric that combines:

1. Halstead Volume (measuring the "size" and complexity of operations)
2. Cyclomatic Complexity (measuring the number of independent paths)
3. Lines of Code (measuring the physical size of the code)

It provides a single score from 0-100 indicating how maintainable the code is.

**Interpretation:**
- **80-100**: High maintainability
- **60-79**: Moderate maintainability
- **40-59**: Low maintainability
- **0-39**: Very low maintainability

## Usage

### Command Line

Analyze complexity metrics using the CLI:

```bash
# Analyze a single file
code-pattern complexity sample.py

# Analyze a directory
code-pattern complexity src/

# Generate HTML report
code-pattern complexity src/ --format html --output complexity_report.html

# Focus on specific metrics
code-pattern complexity src/ --metrics cyclomatic,cognitive

# Set a threshold to highlight only high-complexity code
code-pattern complexity src/ --threshold 20
```

### Using the Script

The project includes a dedicated script for complexity analysis:

```bash
# Analyze a directory with HTML output
python run_complexity_analysis.py src/

# Exclude certain directories
python run_complexity_analysis.py src/ --exclude "tests,docs,examples"

# Analyze only specific file types
python run_complexity_analysis.py src/ --extensions ".py,.js"
```

## Example Output

The HTML report includes:

- Overall complexity distribution chart
- Per-file complexity breakdown
- Function-level complexity details
- Recommendations for improving maintainability
- Color-coded indicators of complexity levels

## Practical Applications

1. **Technical Debt Management**: Identify complex code that may be difficult to maintain
2. **Code Review**: Use complexity metrics to focus reviews on high-risk areas
3. **Refactoring Prioritization**: Target functions with the highest complexity first
4. **Quality Gates**: Set thresholds for maximum allowed complexity in new code
5. **Architectural Improvement**: Use metrics to guide architectural decisions

## Integration with Other Features

Complexity metrics work alongside other Code Pattern Analyzer features:

- **Pattern Detection**: Find complex implementations of design patterns
- **Anti-Pattern Analysis**: Identify where complexity contributes to architectural problems
- **Visualization**: Visualize complexity across your codebase