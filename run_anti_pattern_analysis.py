#!/usr/bin/env python
"""
Helper script to run architectural anti-pattern analysis on a directory.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure root logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Add the project root to sys.path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import required modules
from src.analyzer import CodeAnalyzer
from src.patterns.architectural_styles import ArchitecturalStyleDetector
from src.patterns.architectural_anti_patterns import ArchitecturalAntiPatternDetector
from src.commands.anti_patterns import generate_text_report, generate_html_report

def analyze_anti_patterns(directory_path, output_format='text'):
    """Run architectural anti-pattern analysis on a directory.
    
    Args:
        directory_path: Path to the directory to analyze
        output_format: Output format ('json', 'text', or 'html')
        
    Returns:
        Analysis results as a string in the specified format
    """
    directory_path = Path(directory_path)
    if not directory_path.is_dir():
        raise NotADirectoryError(f"{directory_path} is not a directory")
    
    # Create analyzer
    analyzer = CodeAnalyzer(use_mock=True)  # Using mock implementation for simplicity
    
    logger.info(f"Analyzing files in {directory_path}")
    
    # Analyze all files in the directory
    results = analyzer.analyze_directory(str(directory_path))
    
    # First, detect architectural styles (needed for anti-pattern detection)
    logger.info("Analyzing architectural styles")
    style_detector = ArchitecturalStyleDetector()
    architectural_styles = style_detector.analyze_codebase(
        results,
        {},  # No architectural intents needed for this analysis
        codebase_root=str(directory_path)
    )
    
    # Now detect anti-patterns using the architectural style information
    logger.info("Analyzing architectural anti-patterns")
    anti_pattern_detector = ArchitecturalAntiPatternDetector()
    anti_pattern_analysis = anti_pattern_detector.analyze_codebase(
        results,
        architectural_styles,
        codebase_root=str(directory_path)
    )
    
    # Generate output in the specified format
    if output_format == 'json':
        return json.dumps(anti_pattern_analysis, indent=2)
    elif output_format == 'text':
        return generate_text_report(anti_pattern_analysis, str(directory_path))
    elif output_format == 'html':
        return generate_html_report(anti_pattern_analysis, str(directory_path))
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_anti_pattern_analysis.py <directory> [output_format]")
        sys.exit(1)
    
    directory = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'text'
    
    try:
        result = analyze_anti_patterns(directory, output_format)
        print(result)
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)