"""
Command-line argument parser for the Code Pattern Analyzer.

This module sets up the argument parser for the command-line interface,
defining the various commands and options available to users.
"""

import argparse
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def setup_parser() -> argparse.ArgumentParser:
    """Set up the argument parser.
    
    Returns:
        The configured ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="Code Pattern Analyzer - Detect patterns in source code",
        epilog="For more information, see the documentation.",
    )
    
    # Global options
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementation instead of tree-sitter"
    )
    
    # Set up subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Pattern detection command
    pattern_parser = subparsers.add_parser(
        "pattern",
        help="Find patterns in code"
    )
    pattern_parser.add_argument(
        "path",
        help="Path to the file or directory to analyze"
    )
    pattern_parser.add_argument(
        "--pattern", "-p",
        help="Specific pattern to look for"
    )
    pattern_parser.add_argument(
        "--category", "-c",
        help="Category of patterns to look for"
    )
    pattern_parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "html"],
        default="text",
        help="Output format"
    )
    pattern_parser.add_argument(
        "--output", "-o",
        help="Output file (stdout if not specified)"
    )
    pattern_parser.add_argument(
        "--extensions", "-e",
        nargs="+",
        help="File extensions to analyze (e.g. .py .js)"
    )
    pattern_parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing"
    )
    
    # List available patterns command
    list_parser = subparsers.add_parser(
        "list",
        help="List available patterns"
    )
    list_parser.add_argument(
        "--category", "-c",
        help="List patterns in a specific category"
    )
    list_parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementation instead of tree-sitter"
    )
    
    # Architecture analysis command
    arch_parser = subparsers.add_parser(
        "architecture",
        help="Analyze software architecture"
    )
    arch_parser.add_argument(
        "path",
        help="Path to the directory to analyze"
    )
    arch_parser.add_argument(
        "--format", "-f",
        choices=["json", "text"],
        default="text",
        help="Output format"
    )
    arch_parser.add_argument(
        "--output", "-o",
        help="Output file (stdout if not specified)"
    )
    arch_parser.add_argument(
        "--extensions", "-e",
        nargs="+",
        help="File extensions to analyze (e.g. .py .js)"
    )
    arch_parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing"
    )
    arch_parser.add_argument(
        "--style",
        action="store_true",
        help="Analyze architectural style instead of intents"
    )
    arch_parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualization of the detected architecture"
    )
    arch_parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementation instead of tree-sitter"
    )
    
    # Visualization command
    vis_parser = subparsers.add_parser(
        "visualize",
        help="Generate visualizations for architectural patterns"
    )
    vis_parser.add_argument(
        "path",
        help="Path to the directory to analyze"
    )
    vis_parser.add_argument(
        "--pattern", "-p",
        choices=["layered_architecture", "hexagonal", "clean_architecture", 
                 "event_driven", "microservices"],
        default="layered_architecture",
        help="Architectural pattern to visualize"
    )
    vis_parser.add_argument(
        "--output", "-o",
        help="Output directory for visualization files (defaults to reports/)"
    )
    vis_parser.add_argument(
        "--extensions", "-e",
        nargs="+",
        help="File extensions to analyze (e.g. .py .js)"
    )
    vis_parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing"
    )
    vis_parser.add_argument(
        "--open",
        action="store_true",
        help="Automatically open the visualization in a browser"
    )
    vis_parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementation instead of tree-sitter"
    )
    
    return parser

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        The parsed arguments
    """
    parser = setup_parser()
    return parser.parse_args(args)