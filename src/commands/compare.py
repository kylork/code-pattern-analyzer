"""
Command to compare pattern detection between multiple files.
"""

import click
import os
import logging
from pathlib import Path
import sys

from ..analyzer import CodeAnalyzer
from ..utils import AnalysisComparer

logger = logging.getLogger(__name__)

@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Path to output file')
@click.option('--format', '-f', type=click.Choice(['json', 'text', 'html']), default='text', help='Output format')
@click.option('--pattern', '-p', help='Specific pattern to look for')
@click.option('--category', '-c', help='Specific category of patterns to look for')
@click.option('--open', 'open_report', is_flag=True, help='Open the report after generation')
def compare(files, output, format, pattern, category, open_report):
    """Compare pattern detection between multiple files.
    
    FILES are two or more files to compare.
    """
    if len(files) < 2:
        click.echo("Error: At least two files must be provided for comparison.", err=True)
        sys.exit(1)
        
    if pattern and category:
        click.echo("Error: Cannot specify both --pattern and --category.", err=True)
        sys.exit(1)
    
    try:
        # Create the comparer
        analyzer = CodeAnalyzer()
        comparer = AnalysisComparer(analyzer)
        
        # Compare the files
        report = comparer.compare_files(
            files,
            pattern_name=pattern,
            category=category,
            output_format=format
        )
        
        # Output the report
        if output:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
            
            # Write the report
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report)
                
            click.echo(f"Comparison report written to {output}")
            
            # Open the report if requested
            if open_report:
                if format == 'html':
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(output)}")
                elif format in ('text', 'json'):
                    os.system(f"cat {output}")
        else:
            # Print the report to stdout
            click.echo(report)
            
    except Exception as e:
        logger.error(f"Error comparing files: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)