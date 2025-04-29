"""
Command to generate comprehensive reports on a codebase.
"""

import click
import os
import logging
from pathlib import Path
import datetime
import sys

from ..analyzer import CodeAnalyzer
from ..utils import BatchAnalyzer, ReportGenerator

logger = logging.getLogger(__name__)

@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='Directory to save reports')
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'text']), default='html', help='Report format')
@click.option('--title', '-t', help='Report title')
@click.option('--exclude', help='Comma-separated list of directories to exclude')
@click.option('--extensions', '-e', help='Comma-separated list of file extensions to analyze')
@click.option('--category', '-c', help='Specific category of patterns to look for')
@click.option('--patterns', '-p', help='Comma-separated list of patterns to look for')
@click.option('--workers', type=int, default=4, help='Number of worker threads')
@click.option('--report-name', help='Filename for the report')
@click.option('--open', 'open_report', is_flag=True, help='Open the report after generation')
def report(directory, output_dir, format, title, exclude, extensions, 
           category, patterns, workers, report_name, open_report):
    """Generate a comprehensive report on a codebase.
    
    DIRECTORY is the path to the codebase to analyze.
    """
    try:
        # Process input options
        directory = Path(directory)
        
        # Default title if not provided
        if not title:
            title = f"Code Pattern Analysis: {directory.name}"
        
        # Parse exclude directories if provided
        exclude_dirs = None
        if exclude:
            exclude_dirs = [dir.strip() for dir in exclude.split(",")]
        
        # Parse file extensions if provided
        file_extensions = None
        if extensions:
            file_extensions = [ext.strip() for ext in extensions.split(",")]
            # Ensure extensions start with a dot
            file_extensions = [(("." + ext) if not ext.startswith(".") else ext) for ext in file_extensions]
        
        # Parse patterns if provided
        pattern_list = None
        if patterns:
            pattern_list = [p.strip() for p in patterns.split(",")]
        
        # Create the analyzer and report generator
        analyzer = CodeAnalyzer()
        batch_analyzer = BatchAnalyzer(analyzer, max_workers=workers)
        
        # Generate default report name if not provided
        if not report_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            report_name = f"{directory.name}-analysis-{timestamp}.{format}"
        
        # Create output directory if not exists
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = os.getcwd()
        
        # Show analysis parameters
        click.echo(f"Analyzing directory: {directory}")
        if category:
            click.echo(f"Category: {category}")
        if pattern_list:
            click.echo(f"Patterns: {', '.join(pattern_list)}")
        if exclude_dirs:
            click.echo(f"Excluding directories: {', '.join(exclude_dirs)}")
        if file_extensions:
            click.echo(f"File extensions: {', '.join(file_extensions)}")
        
        click.echo("Starting analysis...")
        
        # Check if we should analyze multiple patterns or a single pattern
        if pattern_list:
            # Analyze each pattern separately and combine results
            all_results = []
            
            with click.progressbar(pattern_list, label='Analyzing patterns') as patterns_bar:
                for pattern in patterns_bar:
                    # Analyze the directory for this pattern
                    results = analyzer.analyze_directory(
                        directory,
                        pattern_name=pattern,
                        exclude_dirs=exclude_dirs,
                        file_extensions=file_extensions,
                        max_workers=workers
                    )
                    
                    # Add these results to the combined set
                    all_results.extend(results)
        else:
            # Analyze with a category or all patterns
            all_results = analyzer.analyze_directory(
                directory,
                pattern_name=None,
                category=category,
                exclude_dirs=exclude_dirs,
                file_extensions=file_extensions,
                max_workers=workers
            )
        
        # Generate the report
        report_generator = ReportGenerator(analyzer, output_dir=output_dir)
        output_path = report_generator.generate_report(
            all_results,
            output_format=format,
            title=title,
            filename=report_name
        )
        
        click.echo(f"Report generated: {output_path}")
        
        # Open the report if requested
        if open_report:
            if format == 'html':
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(output_path)}")
            elif format == 'text':
                os.system(f"cat {output_path}")
            elif format == 'json':
                os.system(f"cat {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)