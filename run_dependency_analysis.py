#!/usr/bin/env python3
"""
Run dependency analysis on a codebase.

This script analyzes dependencies between modules in a project, generating reports
and visualizations that highlight the dependency structure.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_dependency_graph import DependencyAnalyzer, generate_html_report, generate_text_report

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Analyze dependencies between modules in a project."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for the report or visualization"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "html", "png", "svg", "pdf"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directories to exclude (e.g. 'tests,docs')"
    )
    parser.add_argument(
        "--visualization-only",
        action="store_true",
        help="Only generate visualization, not full report"
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=100,
        help="Maximum number of nodes to display in the visualization"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set default output file if not specified
    if not args.output:
        output_name = f"{os.path.basename(args.path)}_dependencies"
        
        if args.format == "html":
            args.output = f"reports/{output_name}.html"
        elif args.format == "json":
            args.output = f"reports/{output_name}.json"
        elif args.format == "text":
            args.output = f"reports/{output_name}.txt"
        else:  # Image formats
            args.output = f"reports/{output_name}.{args.format}"
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # Parse exclude directories
    exclude_dirs = None 
    if args.exclude:
        exclude_dirs = [dir.strip() for dir in args.exclude.split(',')]
    
    print(f"Analyzing dependencies in {args.path}...")
    
    # Initialize and run the analyzer
    analyzer = DependencyAnalyzer()
    
    if os.path.isdir(args.path):
        results = analyzer.analyze_directory(args.path, exclude_dirs)
    else:
        print("Single file analysis not supported. Please provide a directory.")
        return 1
    
    # Generate output
    if args.visualization_only or args.format in ['png', 'svg', 'pdf']:
        # Just generate visualization
        viz_format = args.format if args.format in ['png', 'svg', 'pdf'] else 'html'
        output_file = analyzer.visualize_dependencies(
            args.output,
            title=f"Dependency Graph: {os.path.basename(args.path)}",
            max_nodes=args.max_nodes,
            format=viz_format
        )
        print(f"Dependency visualization written to {output_file}")
        if viz_format == 'html':
            print(f"Open in your browser: file://{os.path.abspath(output_file)}")
    else:
        # Generate full report
        import json
        if args.format == 'json':
            report = json.dumps(results, indent=2, default=list)
        elif args.format == 'html':
            report = generate_html_report(results, args.path)
        else:  # text format
            report = generate_text_report(results, args.path)
        
        # Write to output file
        Path(args.output).write_text(report)
        print(f"Dependency analysis written to {args.output}")
        print(f"Open the file to view the report: file://{os.path.abspath(args.output)}")
        
        # Also generate a visualization if HTML report
        if args.format == 'html' and not args.visualization_only:
            viz_output = args.output.replace('.html', '_graph.html')
            analyzer.visualize_dependencies(
                viz_output,
                title=f"Dependency Graph: {os.path.basename(args.path)}",
                max_nodes=args.max_nodes,
                format='html'
            )
            print(f"Dependency visualization written to {viz_output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())