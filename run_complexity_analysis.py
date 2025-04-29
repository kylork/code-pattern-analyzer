#\!/usr/bin/env python3
"""
Run complexity analysis on a codebase.

This script analyzes code complexity in a project, generating reports that
highlight potential maintainability issues.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.commands.complexity import complexity_command

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Analyze code complexity metrics in a project."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the file or directory to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for the report"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "html"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directories to exclude (e.g. 'tests,docs')"
    )
    parser.add_argument(
        "--extensions", "-e",
        help="Comma-separated list of file extensions to analyze (e.g. '.py,.js')"
    )
    parser.add_argument(
        "--metrics", "-m",
        help="Comma-separated list of metrics to include (cyclomatic, cognitive, maintainability)"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        help="Complexity threshold to highlight (values above this are flagged)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementation instead of tree-sitter"
    )
    
    args = parser.parse_args()
    
    # Set default output file if not specified
    if not args.output:
        if os.path.isfile(args.path):
            output_name = f"{Path(args.path).stem}_complexity"
        else:
            output_name = f"{os.path.basename(args.path)}_complexity"
        
        if args.format == "html":
            args.output = f"reports/{output_name}.html"
        elif args.format == "json":
            args.output = f"reports/{output_name}.json"
        else:
            args.output = f"reports/{output_name}.txt"
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print(f"Analyzing complexity of {args.path}...")
    # Convert arguments to the format expected by the click command
    click_args = [args.path]
    click_kwargs = {
        'output': args.output,
        'output_format': args.format,
        'exclude': args.exclude,
        'extensions': args.extensions,
        'metrics': args.metrics,
        'threshold': args.threshold,
        'use_real': not args.mock,
        'debug': args.debug
    }
    complexity_command(obj=None, **click_kwargs, standalone_mode=False)
    print(f"Complexity analysis written to {args.output}")
    print(f"Open the file in your browser to view the report: file://{os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()
