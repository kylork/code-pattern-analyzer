"""
Command for analyzing code complexity.
"""

import os
import json
import click
import logging
from pathlib import Path
from typing import Dict, List, Optional

from ..analyzer import CodeAnalyzer
from ..metrics.complexity import ComplexityAnalyzer

# Set up logging
logger = logging.getLogger(__name__)

@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for the report')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text', 'html']), default='text', help='Output format')
@click.option('--exclude', help='Comma-separated list of directories to exclude')
@click.option('--extensions', '-e', help='Comma-separated list of file extensions to analyze')
@click.option('--metrics', '-m', help='Comma-separated list of metrics to include (cyclomatic, cognitive, maintainability)')
@click.option('--threshold', '-t', type=int, help='Complexity threshold to highlight (values above this are flagged)')
@click.option('--real/--mock', 'use_real', default=True, help='Use real or mock implementation')
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
def complexity_command(path, output, output_format, exclude, extensions, metrics, threshold, use_real, debug):
    """Analyze code complexity in PATH.
    
    This command analyzes code complexity using various metrics including
    cyclomatic complexity, cognitive complexity, and maintainability index.
    It can analyze a single file or an entire directory.
    """
    try:
        # Set up logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Parse exclude and extensions
        exclude_dirs = None if not exclude else [dir.strip() for dir in exclude.split(',')]
        file_extensions = None if not extensions else [ext.strip() for ext in extensions.split(',')]
        
        # Parse metrics to include
        include_metrics = None
        if metrics:
            metric_map = {
                'cyclomatic': 'cyclomatic_complexity',
                'cognitive': 'cognitive_complexity',
                'maintainability': 'maintainability_index'
            }
            include_metrics = [metric_map.get(m.strip(), m.strip()) for m in metrics.split(',')]
        
        # Initialize analyzer
        analyzer = CodeAnalyzer(use_mock=not use_real)
        
        click.echo(f"Analyzing complexity of {path}...")
        
        # Analyze the path
        complexity_results = []
        
        if os.path.isfile(path):
            # Single file analysis
            file_results = analyzer.analyze_file(path)
            complexity_results = [analyze_file_complexity(file_results, include_metrics)]
        else:
            # Directory analysis
            file_results = analyzer.analyze_directory(
                path,
                exclude_dirs=exclude_dirs,
                file_extensions=file_extensions
            )
            
            for result in file_results:
                complexity_result = analyze_file_complexity(result, include_metrics)
                if complexity_result:
                    complexity_results.append(complexity_result)
        
        # Generate the report
        if output_format == 'json':
            report = json.dumps(complexity_results, indent=2)
        elif output_format == 'html':
            report = generate_html_report(complexity_results, path, threshold)
        else:  # text format
            report = generate_text_report(complexity_results, path, threshold)
        
        # Write to output file or print to console
        if output:
            Path(output).write_text(report)
            click.echo(f"Complexity analysis written to {output}")
        else:
            click.echo(report)
            
    except Exception as e:
        logger.error(f"Error analyzing complexity: {e}")
        click.echo(f"Error: {e}", err=True)
        raise

def analyze_file_complexity(file_result: Dict, include_metrics: Optional[List[str]] = None) -> Optional[Dict]:
    """Analyze the complexity of a single file.
    
    Args:
        file_result: Result from analyzing a file
        include_metrics: Optional list of metric names to include
        
    Returns:
        Complexity analysis result or None if analysis failed
    """
    try:
        # Check if the file was successfully parsed
        if "error" in file_result:
            logger.warning(f"Skipping file with error: {file_result.get('file', 'unknown')}")
            return None
        
        # Extract file info
        file_path = file_result.get("file")
        language = file_result.get("language")
        ast = file_result.get("ast")
        code = file_result.get("code")
        
        if not ast or not code or not language:
            logger.warning(f"Missing required data for file: {file_path}")
            return None
        
        # Create complexity analyzer
        complexity_analyzer = ComplexityAnalyzer()
        
        # Analyze complexity
        complexity_result = complexity_analyzer.analyze(
            ast, code, language, file_path, include_metrics
        )
        
        return complexity_result
        
    except Exception as e:
        logger.error(f"Error analyzing file complexity: {e}")
        return None

def generate_text_report(results: List[Dict], path: str, threshold: Optional[int] = None) -> str:
    """Generate a text report from the complexity analysis results.
    
    Args:
        results: List of complexity analysis results
        path: The analyzed path
        threshold: Optional complexity threshold to highlight
        
    Returns:
        Text report
    """
    lines = []
    lines.append(f"Complexity Analysis for {path}")
    lines.append("=" * 80)
    
    # Skip empty results
    if not results:
        lines.append("No files analyzed successfully.")
        return "\n".join(lines)
    
    # Add summary
    high_complexity_files = sum(1 for r in results 
                               if r.get("overall_assessment", {}).get("complexity_level") in ["high", "very_high"])
    total_files = len(results)
    
    lines.append(f"Analyzed {total_files} files")
    lines.append(f"High complexity files: {high_complexity_files} ({high_complexity_files/total_files*100:.1f}%)")
    
    # Sort results by complexity level (highest first)
    sorted_results = sorted(
        results, 
        key=lambda r: {
            "very_high": 4,
            "high": 3,
            "moderate": 2,
            "low": 1,
            "unknown": 0
        }.get(r.get("overall_assessment", {}).get("complexity_level", "unknown"), 0),
        reverse=True
    )
    
    # Add detailed results
    lines.append("\nDetailed Results:")
    for result in sorted_results:
        file_path = result.get("file_path", "unknown")
        complexity_level = result.get("overall_assessment", {}).get("complexity_level", "unknown")
        
        # Skip files below threshold if specified
        if threshold and complexity_level in ["low", "moderate"]:
            cyclomatic = result.get("metrics", {}).get("cyclomatic_complexity", {}).get("value", 0)
            if cyclomatic and cyclomatic < threshold:
                continue
        
        lines.append(f"\n{file_path}")
        lines.append("-" * 80)
        
        # Add overall assessment
        assessment = result.get("overall_assessment", {})
        lines.append(f"Complexity Level: {complexity_level.upper()}")
        lines.append(f"Description: {assessment.get('description', 'No description available')}")
        
        # Add individual metrics
        metrics = result.get("metrics", {})
        
        # Cyclomatic complexity
        cc = metrics.get("cyclomatic_complexity", {})
        if cc and "value" in cc:
            lines.append(f"\nCyclomatic Complexity: {cc.get('value', 'N/A')}")
            
            # Add function details if available
            functions = cc.get("functions", [])
            if functions:
                lines.append("  Functions:")
                for func in functions[:5]:  # Show top 5 functions
                    name = func.get("name", "unknown")
                    complexity = func.get("complexity", 0)
                    line = func.get("line", 0)
                    lines.append(f"    {name} (line {line}): {complexity}")
                
                if len(functions) > 5:
                    lines.append(f"    ... and {len(functions) - 5} more functions")
        
        # Cognitive complexity
        cog = metrics.get("cognitive_complexity", {})
        if cog and "value" in cog:
            lines.append(f"\nCognitive Complexity: {cog.get('value', 'N/A')}")
            
            # Add function details if available
            functions = cog.get("functions", [])
            if functions:
                lines.append("  Functions:")
                for func in functions[:5]:  # Show top 5 functions
                    name = func.get("name", "unknown")
                    complexity = func.get("complexity", 0)
                    line = func.get("line", 0)
                    lines.append(f"    {name} (line {line}): {complexity}")
                
                if len(functions) > 5:
                    lines.append(f"    ... and {len(functions) - 5} more functions")
        
        # Maintainability index
        mi = metrics.get("maintainability_index", {})
        if mi and "value" in mi:
            lines.append(f"\nMaintainability Index: {mi.get('value', 'N/A')}")
            lines.append(f"  Maintainability Level: {mi.get('maintainability_level', 'unknown').upper()}")
            
            # Add component metrics if available
            component_metrics = mi.get("component_metrics", {})
            if component_metrics:
                lines.append("  Component Metrics:")
                for name, value in component_metrics.items():
                    lines.append(f"    {name}: {value}")
        
        # Add recommendations
        recommendations = assessment.get("recommendations", [])
        if recommendations:
            lines.append("\nRecommendations:")
            for rec in recommendations:
                lines.append(f"  - {rec}")
    
    return "\n".join(lines)

def generate_html_report(results: List[Dict], path: str, threshold: Optional[int] = None) -> str:
    """Generate an HTML report from the complexity analysis results.
    
    Args:
        results: List of complexity analysis results
        path: The analyzed path
        threshold: Optional complexity threshold to highlight
        
    Returns:
        HTML report
    """
    # Basic HTML template with styling
    html = ["""
    <!DOCTYPE html>
    <html>
    <head>
    <title>Code Complexity Analysis</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3 {
            color: #444;
        }
        .summary {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .file-card {
            margin: 30px 0;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .file-path {
            font-size: 16px;
            font-weight: bold;
            margin: 0;
            word-break: break-all;
        }
        .complexity-badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }
        .low {
            background-color: #d4edda;
            color: #155724;
        }
        .moderate {
            background-color: #fff3cd;
            color: #856404;
        }
        .high {
            background-color: #f8d7da;
            color: #721c24;
        }
        .very_high {
            background-color: #dc3545;
            color: white;
        }
        .unknown {
            background-color: #e9ecef;
            color: #495057;
        }
        .metric-section {
            margin: 15px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .metric-title {
            font-size: 16px;
            margin: 0 0 10px 0;
        }
        .function-list {
            margin: 10px 0;
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 5px;
        }
        .function-item {
            padding: 5px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
        }
        .function-item:last-child {
            border-bottom: none;
        }
        .recommendations {
            margin: 15px 0;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        .chart-container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            height: 400px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
    """]
    
    # Add header
    html.append(f"<h1>Complexity Analysis</h1>")
    html.append(f"<h2>Project: {os.path.basename(path)}</h2>")
    
    # Skip empty results
    if not results:
        html.append("<p>No files analyzed successfully.</p>")
        html.append("</body></html>")
        return "".join(html)
    
    # Add summary
    high_complexity_files = sum(1 for r in results 
                               if r.get("overall_assessment", {}).get("complexity_level") in ["high", "very_high"])
    total_files = len(results)
    
    html.append('<div class="summary">')
    html.append(f"<h3>Summary</h3>")
    html.append(f"<p>Analyzed {total_files} files</p>")
    html.append(f"<p>High complexity files: {high_complexity_files} ({high_complexity_files/total_files*100:.1f}%)</p>")
    html.append('</div>')
    
    # Add chart data
    html.append('<div class="chart-container">')
    html.append('<canvas id="complexityChart"></canvas>')
    html.append('</div>')
    
    # Add chart initialization
    complexity_levels = {
        "low": 0,
        "moderate": 0,
        "high": 0,
        "very_high": 0,
        "unknown": 0
    }
    
    for result in results:
        level = result.get("overall_assessment", {}).get("complexity_level", "unknown")
        complexity_levels[level] += 1
    
    html.append('<script>')
    html.append('const ctx = document.getElementById("complexityChart").getContext("2d");')
    html.append('const complexityChart = new Chart(ctx, {')
    html.append('    type: "pie",')
    html.append('    data: {')
    html.append('        labels: ["Low", "Moderate", "High", "Very High", "Unknown"],')
    html.append('        datasets: [{')
    html.append('            data: [')
    html.append(f'                {complexity_levels["low"]},')
    html.append(f'                {complexity_levels["moderate"]},')
    html.append(f'                {complexity_levels["high"]},')
    html.append(f'                {complexity_levels["very_high"]},')
    html.append(f'                {complexity_levels["unknown"]}')
    html.append('            ],')
    html.append('            backgroundColor: [')
    html.append('                "#d4edda",')
    html.append('                "#fff3cd",')
    html.append('                "#f8d7da",')
    html.append('                "#dc3545",')
    html.append('                "#e9ecef"')
    html.append('            ],')
    html.append('            borderWidth: 1')
    html.append('        }]')
    html.append('    },')
    html.append('    options: {')
    html.append('        responsive: true,')
    html.append('        plugins: {')
    html.append('            title: {')
    html.append('                display: true,')
    html.append('                text: "Complexity Distribution"')
    html.append('            }')
    html.append('        }')
    html.append('    }')
    html.append('});')
    html.append('</script>')
    
    # Sort results by complexity level (highest first)
    sorted_results = sorted(
        results, 
        key=lambda r: {
            "very_high": 4,
            "high": 3,
            "moderate": 2,
            "low": 1,
            "unknown": 0
        }.get(r.get("overall_assessment", {}).get("complexity_level", "unknown"), 0),
        reverse=True
    )
    
    # Add detailed results
    html.append("<h3>Detailed Results</h3>")
    
    for result in sorted_results:
        file_path = result.get("file_path", "unknown")
        complexity_level = result.get("overall_assessment", {}).get("complexity_level", "unknown")
        
        # Skip files below threshold if specified
        if threshold and complexity_level in ["low", "moderate"]:
            cyclomatic = result.get("metrics", {}).get("cyclomatic_complexity", {}).get("value", 0)
            if cyclomatic and cyclomatic < threshold:
                continue
        
        html.append(f'<div class="file-card">')
        
        # File header
        html.append(f'<div class="file-header">')
        html.append(f'<h3 class="file-path">{file_path}</h3>')
        html.append(f'<span class="complexity-badge {complexity_level}">{complexity_level}</span>')
        html.append('</div>')
        
        # Overall assessment
        assessment = result.get("overall_assessment", {})
        html.append(f'<p>{assessment.get("description", "No description available")}</p>')
        
        # Add individual metrics
        metrics = result.get("metrics", {})
        
        # Cyclomatic complexity
        cc = metrics.get("cyclomatic_complexity", {})
        if cc and "value" in cc:
            html.append(f'<div class="metric-section">')
            html.append(f'<h4 class="metric-title">Cyclomatic Complexity: {cc.get("value", "N/A")}</h4>')
            
            # Add function details if available
            functions = cc.get("functions", [])
            if functions:
                html.append('<div class="function-list">')
                for func in functions:
                    name = func.get("name", "unknown")
                    complexity = func.get("complexity", 0)
                    line = func.get("line", 0)
                    level = func.get("complexity_level", "unknown")
                    html.append(f'<div class="function-item">')
                    html.append(f'<span>{name} (line {line})</span>')
                    html.append(f'<span class="complexity-badge {level}">{complexity}</span>')
                    html.append('</div>')
                html.append('</div>')
            
            html.append('</div>')
        
        # Cognitive complexity
        cog = metrics.get("cognitive_complexity", {})
        if cog and "value" in cog:
            html.append(f'<div class="metric-section">')
            html.append(f'<h4 class="metric-title">Cognitive Complexity: {cog.get("value", "N/A")}</h4>')
            
            # Add function details if available
            functions = cog.get("functions", [])
            if functions:
                html.append('<div class="function-list">')
                for func in functions:
                    name = func.get("name", "unknown")
                    complexity = func.get("complexity", 0)
                    line = func.get("line", 0)
                    level = func.get("complexity_level", "unknown")
                    html.append(f'<div class="function-item">')
                    html.append(f'<span>{name} (line {line})</span>')
                    html.append(f'<span class="complexity-badge {level}">{complexity}</span>')
                    html.append('</div>')
                html.append('</div>')
            
            html.append('</div>')
        
        # Maintainability index
        mi = metrics.get("maintainability_index", {})
        if mi and "value" in mi:
            maintainability_level = mi.get("maintainability_level", "unknown")
            html.append(f'<div class="metric-section">')
            html.append(f'<h4 class="metric-title">Maintainability Index: {mi.get("value", "N/A")}</h4>')
            html.append(f'<p>Maintainability Level: <span class="complexity-badge {maintainability_level}">{maintainability_level}</span></p>')
            
            # Add component metrics if available
            component_metrics = mi.get("component_metrics", {})
            if component_metrics:
                html.append('<ul>')
                for name, value in component_metrics.items():
                    html.append(f'<li>{name}: {value}</li>')
                html.append('</ul>')
            
            html.append('</div>')
        
        # Add recommendations
        recommendations = assessment.get("recommendations", [])
        if recommendations:
            html.append('<div class="recommendations">')
            html.append('<h4>Recommendations</h4>')
            html.append('<ul>')
            for rec in recommendations:
                html.append(f'<li>{rec}</li>')
            html.append('</ul>')
            html.append('</div>')
        
        html.append('</div>')
    
    # Add footer
    html.append("""
    <footer>
    <p>Generated by Code Pattern Analyzer - Complexity Metrics</p>
    </footer>
    </body>
    </html>
    """)
    
    return "".join(html)