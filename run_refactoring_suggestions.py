#!/usr/bin/env python3
"""
Code Pattern Analyzer - Refactoring Suggestions Runner

This script analyzes a codebase to generate refactoring suggestions based on
pattern detection, flow analysis, complexity metrics, and architectural analysis.
"""

import os
import sys
import argparse
import logging
from typing import List, Optional

# Add project src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.refactoring.refactoring_suggestion import (
    CompositeSuggestionGenerator,
    RefactoringSuggestion,
    generate_refactoring_report
)

def setup_logger() -> logging.Logger:
    """Set up and return a logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("refactoring_suggestions")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze codebase and generate refactoring suggestions."
    )
    
    parser.add_argument(
        "target",
        help="File or directory to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file for the report (default: refactoring_suggestions.html)",
        default="refactoring_suggestions.html"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["html", "json", "text"],
        default="html",
        help="Output format (default: html)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    return parser.parse_args()

def run_analysis(target: str, output_path: Optional[str] = None, format_type: str = "html") -> List[RefactoringSuggestion]:
    """Run the refactoring analysis and generate a report.
    
    Args:
        target: File or directory to analyze
        output_path: Path to save the report
        format_type: Format of the report
        
    Returns:
        List of refactoring suggestions
    """
    logger = setup_logger()
    
    if not os.path.exists(target):
        logger.error(f"Target does not exist: {target}")
        return []
    
    logger.info(f"Analyzing target: {target}")
    
    # Create the suggestion generator
    generator = CompositeSuggestionGenerator()
    
    # Generate suggestions
    logger.info("Generating refactoring suggestions...")
    suggestions = generator.generate_all_suggestions(target)
    
    logger.info(f"Generated {len(suggestions)} refactoring suggestions")
    
    # Generate the report if an output path is provided
    if output_path:
        logger.info(f"Generating {format_type} report at {output_path}")
        generate_refactoring_report(suggestions, output_path, format_type)
    
    return suggestions

def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Set the log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Run the analysis
    suggestions = run_analysis(args.target, args.output, args.format)
    
    # Print a summary to the console
    if suggestions:
        print(f"\nGenerated {len(suggestions)} refactoring suggestions")
        
        # Group by impact
        impact_counts = {}
        for s in suggestions:
            impact = s.impact.value
            if impact not in impact_counts:
                impact_counts[impact] = 0
            impact_counts[impact] += 1
        
        # Print impact summary
        for impact, count in impact_counts.items():
            print(f"- {impact.upper()}: {count}")
        
        print(f"\nReport saved to: {args.output}")
    else:
        print("No refactoring suggestions generated.")

if __name__ == "__main__":
    main()