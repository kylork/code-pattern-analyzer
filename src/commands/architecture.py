"""
Command for analyzing architectural intents in a codebase.
"""

import os
import json
import click
import logging
from pathlib import Path

from ..analyzer import CodeAnalyzer
from ..patterns.architectural_intents import ArchitecturalIntentDetector

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
def architecture_command(directory, output, output_format, exclude, extensions, use_real, debug):
    """Analyze architectural intents in a DIRECTORY.
    
    This command analyzes a codebase to identify architectural intents such as
    separation of concerns, information hiding, and dependency inversion.
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
        
        click.echo(f"Analyzing architecture of {directory}...")
        
        # First, analyze all files in the directory
        results = analyzer.analyze_directory(
            directory,
            category="architectural_intents",
            exclude_dirs=exclude_dirs,
            file_extensions=file_extensions
        )
        
        # Create an architectural intent detector
        architecture_detector = ArchitecturalIntentDetector()
        
        # Analyze the collective results
        architecture_analysis = architecture_detector.analyze_codebase(
            results,
            codebase_root=directory
        )
        
        # Generate output
        if output_format == 'json':
            output_content = json.dumps(architecture_analysis, indent=2)
        elif output_format == 'text':
            output_content = generate_text_report(architecture_analysis, directory)
        elif output_format == 'html':
            output_content = generate_html_report(architecture_analysis, directory)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Write to output file or print to console
        if output:
            Path(output).write_text(output_content)
            click.echo(f"Architectural analysis written to {output}")
        else:
            click.echo(output_content)
            
    except Exception as e:
        logger.error(f"Error analyzing architecture: {e}")
        click.echo(f"Error: {e}", err=True)
        raise

def generate_text_report(architecture_analysis, directory):
    """Generate a text report from the architecture analysis results."""
    lines = []
    lines.append(f"Architecture Analysis for {directory}")
    lines.append("=" * 80)
    
    # Add overall score
    score = architecture_analysis.get('architectural_score', 0.0)
    lines.append(f"Overall Architecture Score: {score:.2f} ({int(score * 100)}%)")
    
    # Add overall summary
    if 'summary' in architecture_analysis:
        lines.append("\nSummary:")
        lines.append(architecture_analysis['summary'])
    
    # Add details for each architectural intent
    lines.append("\nDetailed Analysis:")
    for intent_name, results in architecture_analysis.get('intents', {}).items():
        lines.append(f"\n{intent_name.replace('_', ' ').title()}:")
        lines.append("-" * 40)
        
        # Add confidence score
        confidence = results.get('confidence', 0.0)
        lines.append(f"Confidence: {confidence:.2f} ({int(confidence * 100)}%)")
        
        # Add primary pattern (for separation of concerns)
        if 'primary_pattern' in results:
            lines.append(f"Primary Pattern: {results['primary_pattern'].replace('_', ' ').title()}")
        
        # Add components analyzed
        if 'components_analyzed' in results:
            lines.append(f"Components Analyzed: {results['components_analyzed']}")
        
        # Add description
        if 'description' in results:
            lines.append(f"\nDescription: {results['description']}")
        
        # Add layer analysis for separation of concerns
        if 'layer_analysis' in results:
            layer_analysis = results['layer_analysis']
            lines.append("\nLayer Analysis:")
            lines.append(f"  Layer Diversity: {layer_analysis.get('layer_diversity', 0)}")
            
            if 'layer_distribution' in layer_analysis:
                lines.append("  Layer Distribution:")
                for layer, count in layer_analysis['layer_distribution'].items():
                    if layer is not None:
                        lines.append(f"    {layer}: {count}")
            
            if 'clean_layering_score' in layer_analysis:
                score = layer_analysis['clean_layering_score']
                lines.append(f"  Clean Layering Score: {score:.2f} ({int(score * 100)}%)")
            
            if 'layer_violations' in layer_analysis:
                lines.append(f"  Layer Violations: {layer_analysis['layer_violations']}")
        
        # Add domain analysis for separation of concerns
        if 'domain_analysis' in results:
            domain_analysis = results['domain_analysis']
            lines.append("\nDomain Analysis:")
            lines.append(f"  Domain Diversity: {domain_analysis.get('domain_diversity', 0)}")
            
            if 'domain_distribution' in domain_analysis:
                lines.append("  Domain Distribution:")
                for domain, count in domain_analysis['domain_distribution'].items():
                    if domain is not None:
                        lines.append(f"    {domain}: {count}")
            
            if 'domain_isolation_score' in domain_analysis:
                score = domain_analysis['domain_isolation_score']
                lines.append(f"  Domain Isolation Score: {score:.2f} ({int(score * 100)}%)")
            
            if 'cross_domain_dependencies' in domain_analysis:
                lines.append(f"  Cross-Domain Dependencies: {domain_analysis['cross_domain_dependencies']}")
            
            if 'internal_dependencies' in domain_analysis:
                lines.append(f"  Internal Dependencies: {domain_analysis['internal_dependencies']}")
    
    return "\n".join(lines)

def generate_html_report(architecture_analysis, directory):
    """Generate an HTML report from the architecture analysis results."""
    # For the prototype, we'll generate a simple HTML report
    # In a full implementation, this would be more sophisticated with charts, etc.
    html = ["""
    <!DOCTYPE html>
    <html>
    <head>
    <title>Architectural Intent Analysis</title>
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
        .score-container {
            text-align: center;
            margin: 30px 0;
        }
        .score {
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
        }
        .score-label {
            font-size: 18px;
            color: #7f8c8d;
        }
        .summary {
            background-color: #f9f9f9;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .intent-section {
            margin: 30px 0;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .intent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .intent-title {
            font-size: 20px;
            margin: 0;
        }
        .confidence {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
        }
        .high {
            background-color: #e6f7ff;
            color: #0077cc;
        }
        .medium {
            background-color: #fffbe6;
            color: #d48806;
        }
        .low {
            background-color: #fff2e6;
            color: #fa541c;
        }
        .analysis-section {
            margin: 20px 0;
        }
        .analysis-title {
            font-size: 18px;
            margin-bottom: 10px;
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
    html.append(f"<h1>Architectural Intent Analysis</h1>")
    html.append(f"<h2>Project: {os.path.basename(directory)}</h2>")
    
    # Add overall score
    score = architecture_analysis.get('architectural_score', 0.0)
    score_percent = int(score * 100)
    score_class = "high" if score > 0.7 else "medium" if score > 0.4 else "low"
    
    html.append('<div class="score-container">')
    html.append(f'<div class="score">{score_percent}%</div>')
    html.append('<div class="score-label">Architecture Health Score</div>')
    html.append('</div>')
    
    # Add summary
    if 'summary' in architecture_analysis:
        html.append(f'<div class="summary">{architecture_analysis["summary"]}</div>')
    
    # Add details for each intent
    for intent_name, results in architecture_analysis.get('intents', {}).items():
        confidence = results.get('confidence', 0.0)
        confidence_percent = int(confidence * 100)
        confidence_class = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        
        html.append(f'<div class="intent-section">')
        
        # Intent header
        html.append(f'<div class="intent-header">')
        html.append(f'<h3 class="intent-title">{intent_name.replace("_", " ").title()}</h3>')
        html.append(f'<span class="confidence {confidence_class}">{confidence_percent}% Confidence</span>')
        html.append('</div>')
        
        # Intent description
        if 'description' in results:
            html.append(f'<p>{results["description"]}</p>')
        
        # Components analyzed
        if 'components_analyzed' in results:
            html.append(f'<p>Components Analyzed: {results["components_analyzed"]}</p>')
        
        # Primary pattern
        if 'primary_pattern' in results:
            html.append(f'<p>Primary Pattern: {results["primary_pattern"].replace("_", " ").title()}</p>')
        
        # Layer analysis
        if 'layer_analysis' in results:
            layer_analysis = results['layer_analysis']
            html.append('<div class="analysis-section">')
            html.append('<h4 class="analysis-title">Layer Analysis</h4>')
            
            if 'layer_distribution' in layer_analysis:
                html.append('<table>')
                html.append('<tr><th>Layer</th><th>Component Count</th></tr>')
                for layer, count in layer_analysis['layer_distribution'].items():
                    if layer is not None:
                        html.append(f'<tr><td>{layer}</td><td>{count}</td></tr>')
                html.append('</table>')
            
            if 'clean_layering_score' in layer_analysis:
                score = layer_analysis['clean_layering_score']
                score_percent = int(score * 100)
                html.append(f'<p>Clean Layering Score: {score_percent}%</p>')
            
            html.append('</div>')
        
        # Domain analysis
        if 'domain_analysis' in results:
            domain_analysis = results['domain_analysis']
            html.append('<div class="analysis-section">')
            html.append('<h4 class="analysis-title">Domain Analysis</h4>')
            
            if 'domain_distribution' in domain_analysis:
                html.append('<table>')
                html.append('<tr><th>Domain</th><th>Component Count</th></tr>')
                for domain, count in domain_analysis['domain_distribution'].items():
                    if domain is not None:
                        html.append(f'<tr><td>{domain}</td><td>{count}</td></tr>')
                html.append('</table>')
            
            if 'domain_isolation_score' in domain_analysis:
                score = domain_analysis['domain_isolation_score']
                score_percent = int(score * 100)
                html.append(f'<p>Domain Isolation Score: {score_percent}%</p>')
            
            if 'cross_domain_dependencies' in domain_analysis and 'internal_dependencies' in domain_analysis:
                cross = domain_analysis['cross_domain_dependencies']
                internal = domain_analysis['internal_dependencies']
                total = cross + internal
                cross_percent = int(cross / total * 100) if total > 0 else 0
                internal_percent = int(internal / total * 100) if total > 0 else 0
                
                html.append('<p>Dependency Types:</p>')
                html.append('<table>')
                html.append('<tr><th>Type</th><th>Count</th><th>Percentage</th></tr>')
                html.append(f'<tr><td>Cross-Domain</td><td>{cross}</td><td>{cross_percent}%</td></tr>')
                html.append(f'<tr><td>Internal</td><td>{internal}</td><td>{internal_percent}%</td></tr>')
                html.append('</table>')
            
            html.append('</div>')
        
        html.append('</div>')
    
    # Add footer
    html.append("""
    <footer>
    <p>Generated by Code Pattern Analyzer - Architectural Intent Detection</p>
    </footer>
    </body>
    </html>
    """)
    
    return "".join(html)