# VSCode Integration

This guide explains how to use the Code Pattern Analyzer's Visual Studio Code extension to get integrated code analysis, refactoring suggestions, and pattern detection directly in your editor.

## Table of Contents

1. [Installation](#installation)
2. [Features](#features)
3. [Commands](#commands)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Visual Studio Code 1.60.0 or newer
- Code Pattern Analyzer installed and available in your PATH

### Extension Installation

1. Open Visual Studio Code
2. Go to the Extensions view by clicking on the Extensions icon in the Activity Bar or pressing `Ctrl+Shift+X`
3. Search for "Code Pattern Analyzer"
4. Click on the Install button
5. Restart VSCode when prompted

Alternatively, you can install the extension from the command line:

```bash
code --install-extension code-pattern-analyzer-vscode
```

## Features

The VSCode extension provides the following features:

### 1. In-Editor Analysis

- **Issue Highlighting**: Problems are highlighted directly in your code
- **Hover Information**: Hover over highlighted issues to see details
- **Problem Panel Integration**: All issues appear in VSCode's Problems panel

### 2. Refactoring Support

- **Quick Fix Actions**: Apply suggested refactorings with a single click
- **Refactoring Preview**: Preview changes before applying them
- **Batch Refactoring**: Apply multiple refactorings at once

### 3. Visualization

- **Complexity Heatmap**: Color-coding based on code complexity
- **Control Flow Visualization**: View control flow graphs for functions
- **Dependency Visualization**: See module dependencies graphically

### 4. Real-time Analysis

- **On Save Analysis**: Get immediate feedback when saving files
- **Background Analysis**: Continuous analysis as you type (configurable)
- **Full Project Analysis**: Run comprehensive analysis on the entire project

## Commands

Access these commands via the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS):

| Command | Description |
|---------|-------------|
| `Code Pattern Analyzer: Analyze Current File` | Run analysis on the active file |
| `Code Pattern Analyzer: Analyze Project` | Run analysis on the entire project |
| `Code Pattern Analyzer: Show Refactoring Suggestions` | Show all refactoring suggestions for the current file |
| `Code Pattern Analyzer: Apply All Suggested Refactorings` | Apply all refactoring suggestions in the current file |
| `Code Pattern Analyzer: Show Complexity Metrics` | Display complexity metrics for the current file |
| `Code Pattern Analyzer: Show Control Flow Graph` | Show the control flow graph for the current function |
| `Code Pattern Analyzer: Show Dependency Graph` | Display the dependency graph for the project |
| `Code Pattern Analyzer: Configure` | Open the extension configuration |

## Configuration

Configure the extension by opening VS Code's settings (`Ctrl+,`) and searching for "Code Pattern Analyzer" or by editing your `settings.json` file directly.

### Available Settings

```json
{
  "codePatternAnalyzer.analysisOnSave": true,
  "codePatternAnalyzer.backgroundAnalysis": false,
  "codePatternAnalyzer.includePaths": ["src/**/*"],
  "codePatternAnalyzer.excludePaths": ["**/node_modules/**", "**/dist/**"],
  "codePatternAnalyzer.severityLevels": {
    "deadCode": "warning",
    "unusedVariables": "information",
    "highComplexity": "warning",
    "infiniteLoops": "error"
  },
  "codePatternAnalyzer.complexityThreshold": {
    "warning": 10,
    "error": 15
  },
  "codePatternAnalyzer.showInlineComplexity": true,
  "codePatternAnalyzer.enableQuickFixes": true,
  "codePatternAnalyzer.pathToExecutable": "",
  "codePatternAnalyzer.autoOpenFlowGraphs": false
}
```

## Usage Examples

### Analyzing a File

1. Open a file in VSCode
2. Issues are automatically highlighted (if `analysisOnSave` is enabled)
3. Hover over highlighted issues to see details
4. Click on the lightbulb icon (or press `Ctrl+.`) to see available quick fixes
5. Select a quick fix to apply it

### Applying Refactorings

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Run "Code Pattern Analyzer: Show Refactoring Suggestions"
3. Review the suggestions in the sidebar
4. Click "Apply" next to a suggestion to implement it
5. Click "Apply All" to implement all suggestions

### Visualizing Control Flow

1. Place your cursor inside a function
2. Open the Command Palette (`Ctrl+Shift+P`)
3. Run "Code Pattern Analyzer: Show Control Flow Graph"
4. A graphical representation of the function's control flow appears

### Batch Analysis

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Run "Code Pattern Analyzer: Analyze Project"
3. Select which analysis types to include
4. When analysis completes:
   - Issues appear in the Problems panel
   - A notification shows the number of issues found
   - Click "Show Report" for a detailed HTML report

## Troubleshooting

### Common Issues

#### Extension Not Finding the Code Pattern Analyzer

If the extension cannot find the Code Pattern Analyzer executable:

1. Ensure it's installed and in your PATH
2. Or set the full path in settings: `codePatternAnalyzer.pathToExecutable`

#### Analysis Not Running Automatically

If analysis doesn't run when you save a file:

1. Check that `codePatternAnalyzer.analysisOnSave` is set to `true`
2. Verify the file is not excluded by `excludePaths` patterns
3. Check the Output panel (select "Code Pattern Analyzer" from the dropdown) for errors

#### Quick Fixes Not Appearing

If quick fixes aren't available for issues:

1. Ensure `codePatternAnalyzer.enableQuickFixes` is set to `true`
2. Some issues may not have corresponding quick fixes available
3. Try running "Show Refactoring Suggestions" command for more options

### Getting Help

For additional help:

1. Check the Output panel (select "Code Pattern Analyzer" from the dropdown) for detailed logs
2. Open the extension configuration to verify settings
3. Report issues on the GitHub repository