"""
Subcommands for the CLI application.

This module contains the implementation of various CLI subcommands,
allowing users to analyze patterns in code and visualize results.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

import webbrowser
from ..analyzer import CodeAnalyzer

logger = logging.getLogger(__name__)

def pattern_command(args) -> int:
    """Find patterns in code.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    logger.info(f"Looking for {args.pattern or 'all'} patterns in {args.path}")
    
    try:
        # Initialize the analyzer
        analyzer = CodeAnalyzer(args.mock)
        
        # Analyze the path
        if os.path.isfile(args.path):
            results = [analyzer.analyze_file(args.path, args.pattern, args.category)]
        else:
            results = analyzer.analyze_directory(
                args.path, 
                args.pattern, 
                args.category,
                None,  # exclude_dirs
                args.extensions,
                args.workers
            )
        
        # Generate report
        report = analyzer.generate_report(results, args.format)
        
        # Write to output file or print to console
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            logger.info(f"Report written to {args.output}")
        else:
            print(report)
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


def visualize_command(args) -> int:
    """Generate visualizations for architectural patterns.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    logger.info(f"Generating visualization for {args.pattern} in {args.path}")
    
    try:
        # Initialize the analyzer
        analyzer = CodeAnalyzer(args.mock)
        
        # Analyze the path
        if os.path.isfile(args.path):
            logger.error("Visualization requires a directory, not a file")
            return 1
            
        # Analyze files first
        file_results = analyzer.analyze_directory(
            args.path, 
            None,  # pattern
            None,  # category
            None,  # exclude_dirs
            args.extensions,
            args.workers
        )
        
        # Analyze architectural patterns based on the requested pattern
        if args.pattern == "layered_architecture":
            from ..patterns.architectural_styles import LayeredArchitecturePattern
            pattern = LayeredArchitecturePattern()
            pattern.analyze_files(file_results, args.path)
            analysis_result = pattern._analyze_graph()
            
            # Create the visualizer
            from ..visualization import LayeredArchitectureVisualizer
            output_dir = args.output if args.output else "reports"
            visualizer = LayeredArchitectureVisualizer(output_dir)
            
            # Generate and save the visualization
            output_path = visualizer.visualize(analysis_result)
            
            logger.info(f"Visualization saved to: {output_path}")
            
            # Open in browser if requested
            if args.open:
                try:
                    webbrowser.open(f"file://{os.path.abspath(output_path)}")
                    logger.info("Opened visualization in browser")
                except Exception as e:
                    logger.error(f"Could not open browser: {str(e)}")
        else:
            logger.warning(f"Visualization for pattern '{args.pattern}' not yet implemented")
            logger.info("Currently supported: layered_architecture")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


def list_command(args) -> int:
    """List available patterns.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    logger.info("Listing available patterns")
    
    try:
        # Initialize the analyzer
        analyzer = CodeAnalyzer(args.mock)
        
        # Get available patterns
        if args.category:
            patterns = analyzer.get_patterns_by_category(args.category)
            print(f"Patterns in category '{args.category}':")
        else:
            patterns = analyzer.get_available_patterns()
            print("Available patterns:")
            
        for pattern in patterns:
            print(f"  - {pattern}")
            
        print()
        print("Available categories:")
        for category in analyzer.get_available_categories():
            print(f"  - {category}")
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


def visualize_command(args) -> int:
    """Generate visualizations for architectural patterns.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    logger.info(f"Generating visualization for {args.pattern} in {args.path}")
    
    try:
        # Initialize the analyzer
        analyzer = CodeAnalyzer(args.mock)
        
        # Analyze the path
        if os.path.isfile(args.path):
            logger.error("Visualization requires a directory, not a file")
            return 1
            
        # Analyze files first
        file_results = analyzer.analyze_directory(
            args.path, 
            None,  # pattern
            None,  # category
            None,  # exclude_dirs
            args.extensions,
            args.workers
        )
        
        # Analyze architectural patterns based on the requested pattern
        if args.pattern == "layered_architecture":
            from ..patterns.architectural_styles import LayeredArchitecturePattern
            pattern = LayeredArchitecturePattern()
            pattern.analyze_files(file_results, args.path)
            analysis_result = pattern._analyze_graph()
            
            # Create the visualizer
            from ..visualization import LayeredArchitectureVisualizer
            output_dir = args.output if args.output else "reports"
            visualizer = LayeredArchitectureVisualizer(output_dir)
            
            # Generate and save the visualization
            output_path = visualizer.visualize(analysis_result)
            
            logger.info(f"Visualization saved to: {output_path}")
            
            # Open in browser if requested
            if args.open:
                try:
                    webbrowser.open(f"file://{os.path.abspath(output_path)}")
                    logger.info("Opened visualization in browser")
                except Exception as e:
                    logger.error(f"Could not open browser: {str(e)}")
        else:
            logger.warning(f"Visualization for pattern '{args.pattern}' not yet implemented")
            logger.info("Currently supported: layered_architecture")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


def architecture_command(args) -> int:
    """Analyze software architecture.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    logger.info(f"Analyzing architecture of {args.path}")
    
    try:
        # Initialize the analyzer
        analyzer = CodeAnalyzer(args.mock)
        
        # Analyze the path
        if os.path.isfile(args.path):
            logger.error("Architecture analysis requires a directory, not a file")
            return 1
            
        # Analyze files first
        file_results = analyzer.analyze_directory(
            args.path, 
            None,  # pattern
            "architectural_intents" if not args.style else None,  # category
            None,  # exclude_dirs
            args.extensions,
            args.workers
        )
        
        # Analyze architectural intents
        architectural_intents = {}
        if not args.style:
            from ..patterns.architectural_intents import ArchitecturalIntentDetector
            intent_detector = ArchitecturalIntentDetector()
            architectural_intents = intent_detector.analyze_codebase(file_results, args.path)
        
        # Analyze architectural styles if requested
        architectural_styles = {}
        if args.style:
            from ..patterns.architectural_styles import ArchitecturalStyleDetector
            style_detector = ArchitecturalStyleDetector()
            architectural_styles = style_detector.analyze_codebase(file_results, architectural_intents, args.path)
        
        # Prepare the final result
        if args.style:
            result = architectural_styles
        else:
            result = architectural_intents
            
        # Generate visualization if requested
        if args.visualize and args.style:
            from ..visualization import LayeredArchitectureVisualizer, ArchitectureVisualizer
            output_dir = args.output if args.output else "reports"
            
            # Create outputs directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate visualization based on detected architectural style
            if 'layered_architecture' in result:
                layered_data = result.get('layered_architecture', {})
                visualizer = LayeredArchitectureVisualizer(output_dir)
                vis_path = visualizer.visualize(layered_data)
                logger.info(f"Layered architecture visualization saved to: {vis_path}")
            else:
                logger.warning("No supported architectural style detected for visualization")
            
        # Output format
        if args.format == 'json':
            output = json.dumps(result, indent=2)
        else:
            # Text format - just use the summary
            if args.style:
                output = result.get('summary', 'No architectural style detected')
            else:
                output = result.get('summary', 'No architectural intent detected')
            
        # Write to output file or print to console
        if args.output and not args.visualize:
            with open(args.output, 'w') as f:
                f.write(output)
            logger.info(f"Report written to {args.output}")
        else:
            print(output)
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


def visualize_command(args) -> int:
    """Generate visualizations for architectural patterns.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    logger.info(f"Generating visualization for {args.pattern} in {args.path}")
    
    try:
        # Initialize the analyzer
        analyzer = CodeAnalyzer(args.mock)
        
        # Analyze the path
        if os.path.isfile(args.path):
            logger.error("Visualization requires a directory, not a file")
            return 1
            
        # Analyze files first
        file_results = analyzer.analyze_directory(
            args.path, 
            None,  # pattern
            None,  # category
            None,  # exclude_dirs
            args.extensions,
            args.workers
        )
        
        # Analyze architectural patterns based on the requested pattern
        if args.pattern == "layered_architecture":
            from ..patterns.architectural_styles import LayeredArchitecturePattern
            pattern = LayeredArchitecturePattern()
            pattern.analyze_files(file_results, args.path)
            analysis_result = pattern._analyze_graph()
            
            # Create the visualizer
            from ..visualization import LayeredArchitectureVisualizer
            output_dir = args.output if args.output else "reports"
            visualizer = LayeredArchitectureVisualizer(output_dir)
            
            # Generate and save the visualization
            output_path = visualizer.visualize(analysis_result)
            
            logger.info(f"Visualization saved to: {output_path}")
            
            # Open in browser if requested
            if args.open:
                try:
                    webbrowser.open(f"file://{os.path.abspath(output_path)}")
                    logger.info("Opened visualization in browser")
                except Exception as e:
                    logger.error(f"Could not open browser: {str(e)}")
        else:
            logger.warning(f"Visualization for pattern '{args.pattern}' not yet implemented")
            logger.info("Currently supported: layered_architecture")
            return 1
            
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1