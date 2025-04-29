#!/usr/bin/env python3
"""
A simplified wrapper to analyze code complexity.

This script provides a standalone interface for running code complexity
analysis without click command dependencies.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analyzer import CodeAnalyzer
from src.metrics.complexity import ComplexityAnalyzer

def analyze_file_complexity(file_result, include_metrics=None):
    """Analyze the complexity of a single file."""
    try:
        # Check if the file was successfully parsed
        if "error" in file_result:
            print(f"Skipping file with error: {file_result.get('file', 'unknown')}")
            return None
        
        # Extract file info
        file_path = file_result.get("file")
        language = file_result.get("language")
        ast = file_result.get("ast")
        code = file_result.get("code")
        
        if not ast or not code or not language:
            print(f"Missing required data for file: {file_path}")
            return None
        
        # Create complexity analyzer
        complexity_analyzer = ComplexityAnalyzer()
        
        # Analyze complexity
        complexity_result = complexity_analyzer.analyze(
            ast, code, language, file_path, include_metrics
        )
        
        return complexity_result
        
    except Exception as e:
        print(f"Error analyzing file complexity: {e}")
        return None

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
    
    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # Parse exclude and extensions
    exclude_dirs = None 
    if args.exclude:
        exclude_dirs = [dir.strip() for dir in args.exclude.split(',')]
    
    file_extensions = None 
    if args.extensions:
        file_extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    # Parse metrics to include
    include_metrics = None
    if args.metrics:
        metric_map = {
            'cyclomatic': 'cyclomatic_complexity',
            'cognitive': 'cognitive_complexity',
            'maintainability': 'maintainability_index'
        }
        include_metrics = [metric_map.get(m.strip(), m.strip()) for m in args.metrics.split(',')]
    
    print(f"Analyzing complexity of {args.path}...")
    
    # Initialize analyzer
    analyzer = CodeAnalyzer(use_mock=args.mock)
    
    # Analyze the path
    complexity_results = []
    
    try:
        if os.path.isfile(args.path):
            # Single file analysis
            file_results = analyzer.analyze_file(args.path)
            complexity_result = analyze_file_complexity(file_results, include_metrics)
            if complexity_result:
                complexity_results.append(complexity_result)
        else:
            # Directory analysis
            file_results = analyzer.analyze_directory(
                args.path,
                exclude_dirs=exclude_dirs,
                file_extensions=file_extensions
            )
            
            for result in file_results:
                complexity_result = analyze_file_complexity(result, include_metrics)
                if complexity_result:
                    complexity_results.append(complexity_result)
        
        # Generate the report
        if args.format == 'json':
            report = json.dumps(complexity_results, indent=2)
        elif args.format == 'html':
            from src.commands.complexity import generate_html_report
            report = generate_html_report(complexity_results, args.path, args.threshold)
        else:  # text format
            from src.commands.complexity import generate_text_report
            report = generate_text_report(complexity_results, args.path, args.threshold)
        
        # Write to output file or print to console
        if args.output:
            Path(args.output).write_text(report)
            print(f"Complexity analysis written to {args.output}")
            print(f"Open the file in your browser to view the report: file://{os.path.abspath(args.output)}")
        else:
            print(report)
            
    except Exception as e:
        print(f"Error analyzing complexity: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())