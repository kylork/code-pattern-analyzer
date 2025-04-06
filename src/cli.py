"""
Command-line interface for the code pattern analyzer.
"""

import sys
import os
import click
import json
import logging
from pathlib import Path

from .analyzer import CodeAnalyzer
from .mock_implementation import patch_analyzer
from .commands import report, compare

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Check if we should use the mock implementation
use_mock = os.environ.get('CODE_PATTERN_USE_MOCK', 'True').lower() in ('true', '1', 'yes')
if use_mock:
    logging.info("Using mock implementation")
    restore_original = patch_analyzer()
else:
    logging.info("Using tree-sitter implementation")


@click.group()
def cli():
    """Code Pattern Analyzer - Identify patterns in source code."""
    pass

# Add commands from commands module
cli.add_command(report)
cli.add_command(compare)


@cli.command()
def list_patterns():
    """List all available patterns that can be detected."""
    analyzer = CodeAnalyzer()
    patterns = analyzer.get_available_patterns()
    
    click.echo("Available patterns:")
    for pattern in patterns:
        click.echo(f"  - {pattern}")


@cli.command()
def list_categories():
    """List all available pattern categories."""
    analyzer = CodeAnalyzer()
    categories = analyzer.get_available_categories()
    
    click.echo("Available categories:")
    for category in categories:
        click.echo(f"  - {category}")
        
        # Show patterns in this category
        patterns = analyzer.get_patterns_by_category(category)
        for pattern in patterns:
            click.echo(f"    - {pattern}")


@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="Path to the file to analyze")
@click.option("--directory", "-d", type=click.Path(exists=True), help="Path to the directory to analyze")
@click.option("--pattern", "-p", help="Specific pattern to look for")
@click.option("--category", "-c", help="Specific category of patterns to look for")
@click.option("--output", "-o", type=click.Path(), help="Path to output file")
@click.option("--format", type=click.Choice(["json", "text", "html"]), default="json", help="Output format")
@click.option("--extensions", "-e", help="Comma-separated list of file extensions to analyze")
@click.option("--exclude", help="Comma-separated list of directories to exclude")
@click.option("--workers", type=int, default=4, help="Number of worker threads for directory analysis")
def analyze(file, directory, pattern, category, output, format, extensions, exclude, workers):
    """Analyze source code for patterns."""
    if not file and not directory:
        click.echo("Error: Either --file or --directory must be specified.")
        sys.exit(1)
        
    if file and directory:
        click.echo("Error: Cannot specify both --file and --directory.")
        sys.exit(1)
        
    if pattern and category:
        click.echo("Error: Cannot specify both --pattern and --category.")
        sys.exit(1)
        
    analyzer = CodeAnalyzer()
    
    try:
        # Parse extensions if provided
        file_extensions = None
        if extensions:
            file_extensions = [ext.strip() for ext in extensions.split(",")]
            # Ensure extensions start with a dot
            file_extensions = [(("." + ext) if not ext.startswith(".") else ext) for ext in file_extensions]
        
        # Parse exclude directories if provided
        exclude_dirs = None
        if exclude:
            exclude_dirs = [dir.strip() for dir in exclude.split(",")]
        
        # Run the analysis
        if file:
            results = [analyzer.analyze_file(file, pattern, category)]
        else:  # directory
            results = analyzer.analyze_directory(
                directory, 
                pattern_name=pattern,
                category=category,
                exclude_dirs=exclude_dirs,
                file_extensions=file_extensions,
                max_workers=workers
            )
        
        # Generate the report
        report = analyzer.generate_report(results, format)
        
        # Output the report
        if output:
            Path(output).write_text(report)
            click.echo(f"Report written to {output}")
        else:
            click.echo(report)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the command-line interface."""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        # Restore original implementation if patched
        if 'restore_original' in globals():
            restore_original()
    
    
if __name__ == "__main__":
    main()