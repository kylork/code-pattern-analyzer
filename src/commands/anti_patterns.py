"""
Command for analyzing architectural anti-patterns in a codebase.
"""

import os
import json
import click
import logging
from pathlib import Path

from ..analyzer import CodeAnalyzer
from ..patterns.architectural_styles import ArchitecturalStyleDetector
from ..patterns.architectural_anti_patterns import ArchitecturalAntiPatternDetector

# Set up logging
logger = logging.getLogger(__name__)

@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', help='Output file for the report')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text', 'html']), default='text', help='Output format')
@click.option('--exclude', help='Comma-separated list of directories to exclude')
@click.option('--extensions', '-e', help='Comma-separated list of file extensions to analyze')
@click.option('--real/--mock', 'use_real', default=False, help='Use real or mock implementation')
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
def anti_patterns_command(directory, output, output_format, exclude, extensions, use_real, debug):
    """Analyze architectural anti-patterns in a DIRECTORY.
    
    This command analyzes a codebase to identify architectural anti-patterns such as
    tight coupling, dependency cycles, and architectural erosion.
    """
    try:
        # Set up logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Set up analyzer
        analyzer = CodeAnalyzer(use_mock=not use_real)
        
        # Parse exclude and extensions
        exclude_dirs = None if not exclude else [dir.strip() for dir in exclude.split(',')]
        file_extensions = None if not extensions else [ext.strip() for ext in extensions.split(',')]
        
        click.echo(f"Analyzing architectural anti-patterns in {directory}...")
        
        # First, analyze all files in the directory
        results = analyzer.analyze_directory(
            directory,
            exclude_dirs=exclude_dirs,
            file_extensions=file_extensions
        )
        
        # First, detect architectural styles (needed for anti-pattern detection)
        style_detector = ArchitecturalStyleDetector()
        architectural_styles = style_detector.analyze_codebase(
            results,
            {},  # No architectural intents needed for this analysis
            codebase_root=directory
        )
        
        # Now detect anti-patterns using the architectural style information
        anti_pattern_detector = ArchitecturalAntiPatternDetector()
        anti_pattern_analysis = anti_pattern_detector.analyze_codebase(
            results,
            architectural_styles,
            codebase_root=directory
        )
        
        # Generate output
        if output_format == 'json':
            output_content = json.dumps(anti_pattern_analysis, indent=2)
        elif output_format == 'text':
            output_content = generate_text_report(anti_pattern_analysis, directory)
        elif output_format == 'html':
            output_content = generate_html_report(anti_pattern_analysis, directory)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Write to output file or print to console
        if output:
            Path(output).write_text(output_content)
            click.echo(f"Anti-pattern analysis written to {output}")
        else:
            click.echo(output_content)
            
    except Exception as e:
        logger.error(f"Error analyzing anti-patterns: {e}")
        click.echo(f"Error: {e}", err=True)
        raise

def generate_text_report(anti_pattern_analysis, directory):
    """Generate a text report from the anti-pattern analysis results."""
    lines = []
    lines.append(f"Architectural Anti-Pattern Analysis for {directory}")
    lines.append("=" * 80)
    
    # Add overall severity score
    severity = anti_pattern_analysis.get('overall_severity', 0.0)
    lines.append(f"Overall Anti-Pattern Severity: {severity:.2f} ({int(severity * 100)}%)")
    
    # Add overall summary
    if 'summary' in anti_pattern_analysis:
        lines.append("\nSummary:")
        lines.append(anti_pattern_analysis['summary'])
    
    # Add recommendations
    if 'recommendations' in anti_pattern_analysis:
        lines.append("\nRecommendations:")
        for recommendation in anti_pattern_analysis['recommendations']:
            lines.append(f"- {recommendation}")
    
    # Add details for each anti-pattern
    lines.append("\nDetailed Analysis:")
    for pattern_name, results in anti_pattern_analysis.get('anti_patterns', {}).items():
        lines.append(f"\n{pattern_name.replace('_', ' ').title()}:")
        lines.append("-" * 40)
        
        # Add severity score
        severity = results.get('severity', 0.0)
        lines.append(f"Severity: {severity:.2f} ({int(severity * 100)}%)")
        
        # Add description
        if 'description' in results:
            lines.append(f"\nDescription: {results['description']}")
        
        # Add metrics
        if 'metrics' in results:
            lines.append("\nMetrics:")
            for metric, value in results['metrics'].items():
                if isinstance(value, float):
                    lines.append(f"  {metric}: {value:.2f}")
                else:
                    lines.append(f"  {metric}: {value}")
        
        # Add instances
        if 'instances' in results:
            instances = results['instances']
            if instances:
                lines.append(f"\nInstances ({len(instances)}):")
                # Only show top 5 instances to keep the report concise
                for instance in instances[:5]:
                    severity = instance.get('severity', 0.0)
                    description = instance.get('description', '')
                    lines.append(f"  - {description} (Severity: {severity:.2f})")
                
                if len(instances) > 5:
                    lines.append(f"  ... and {len(instances) - 5} more instances")
        
        # Add recommendations
        if 'recommendations' in results:
            lines.append("\nRecommendations:")
            for recommendation in results['recommendations']:
                lines.append(f"  - {recommendation}")
    
    return "\n".join(lines)

def generate_html_report(anti_pattern_analysis, directory):
    """Generate an HTML report from the anti-pattern analysis results."""
    # Basic HTML template with styling
    html = ["""
    <!DOCTYPE html>
    <html>
    <head>
    <title>Architectural Anti-Pattern Analysis</title>
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
        .severity-container {
            text-align: center;
            margin: 30px 0;
        }
        .severity {
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
        }
        .severity-label {
            font-size: 18px;
            color: #7f8c8d;
        }
        .summary {
            background-color: #f9f9f9;
            border-left: 5px solid #e74c3c;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .recommendations {
            background-color: #f9f9f9;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .pattern-section {
            margin: 30px 0;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .pattern-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .pattern-title {
            font-size: 20px;
            margin: 0;
        }
        .severity-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        .high {
            background-color: #ffebee;
            color: #c62828;
        }
        .medium {
            background-color: #fff8e1;
            color: #ff8f00;
        }
        .low {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        .metrics-section {
            margin: 20px 0;
        }
        .metrics-title {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .instances-section {
            margin: 20px 0;
        }
        .instance-item {
            padding: 10px;
            margin-bottom: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
    </head>
    <body>
    """]
    
    # Add header
    html.append(f"<h1>Architectural Anti-Pattern Analysis</h1>")
    html.append(f"<h2>Project: {os.path.basename(directory)}</h2>")
    
    # Add overall severity score
    severity = anti_pattern_analysis.get('overall_severity', 0.0)
    severity_percent = int(severity * 100)
    severity_class = "high" if severity > 0.7 else "medium" if severity > 0.4 else "low"
    
    html.append('<div class="severity-container">')
    html.append(f'<div class="severity">{severity_percent}%</div>')
    html.append('<div class="severity-label">Anti-Pattern Severity</div>')
    html.append('</div>')
    
    # Add summary
    if 'summary' in anti_pattern_analysis:
        html.append(f'<div class="summary">')
        html.append(f'<h3>Summary</h3>')
        html.append(f'<p>{anti_pattern_analysis["summary"]}</p>')
        html.append('</div>')
    
    # Add recommendations
    if 'recommendations' in anti_pattern_analysis:
        html.append(f'<div class="recommendations">')
        html.append(f'<h3>Recommendations</h3>')
        html.append('<ul>')
        for recommendation in anti_pattern_analysis['recommendations']:
            html.append(f'<li>{recommendation}</li>')
        html.append('</ul>')
        html.append('</div>')
    
    # Add details for each anti-pattern
    for pattern_name, results in anti_pattern_analysis.get('anti_patterns', {}).items():
        severity = results.get('severity', 0.0)
        severity_percent = int(severity * 100)
        severity_class = "high" if severity > 0.7 else "medium" if severity > 0.4 else "low"
        
        html.append(f'<div class="pattern-section">')
        
        # Pattern header
        html.append(f'<div class="pattern-header">')
        html.append(f'<h3 class="pattern-title">{pattern_name.replace("_", " ").title()}</h3>')
        html.append(f'<span class="severity-badge {severity_class}">{severity_percent}% Severity</span>')
        html.append('</div>')
        
        # Pattern description
        if 'description' in results:
            html.append(f'<p>{results["description"]}</p>')
        
        # Metrics
        if 'metrics' in results:
            html.append('<div class="metrics-section">')
            html.append('<h4 class="metrics-title">Metrics</h4>')
            html.append('<table>')
            html.append('<tr><th>Metric</th><th>Value</th></tr>')
            for metric, value in results['metrics'].items():
                if isinstance(value, float):
                    html.append(f'<tr><td>{metric.replace("_", " ").title()}</td><td>{value:.2f}</td></tr>')
                else:
                    html.append(f'<tr><td>{metric.replace("_", " ").title()}</td><td>{value}</td></tr>')
            html.append('</table>')
            html.append('</div>')
        
        # Instances
        if 'instances' in results:
            instances = results['instances']
            if instances:
                html.append('<div class="instances-section">')
                html.append(f'<h4>Top Instances ({len(instances)})</h4>')
                
                # Only show top 5 instances to keep the report concise
                for instance in instances[:5]:
                    instance_severity = instance.get('severity', 0.0)
                    instance_severity_percent = int(instance_severity * 100)
                    instance_class = "high" if instance_severity > 0.7 else "medium" if instance_severity > 0.4 else "low"
                    
                    html.append(f'<div class="instance-item">')
                    html.append(f'<div><strong>{instance.get("description", "")}</strong></div>')
                    html.append(f'<div>Severity: <span class="{instance_class}">{instance_severity_percent}%</span></div>')
                    
                    # Add additional instance details if available
                    if 'type' in instance:
                        html.append(f'<div>Type: {instance["type"].replace("_", " ").title()}</div>')
                    
                    html.append('</div>')
                
                if len(instances) > 5:
                    html.append(f'<p>... and {len(instances) - 5} more instances</p>')
                
                html.append('</div>')
        
        # Recommendations
        if 'recommendations' in results:
            html.append('<div class="recommendations">')
            html.append('<h4>Recommendations</h4>')
            html.append('<ul>')
            for recommendation in results['recommendations']:
                html.append(f'<li>{recommendation}</li>')
            html.append('</ul>')
            html.append('</div>')
        
        html.append('</div>')
    
    # Add footer
    html.append("""
    <footer>
    <p>Generated by Code Pattern Analyzer - Architectural Anti-Pattern Detection</p>
    </footer>
    </body>
    </html>
    """)
    
    return "".join(html)