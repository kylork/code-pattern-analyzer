"""
Debug script specifically for testing the Information Hiding pattern detector.
"""

import logging
import os
import sys
from pathlib import Path

# Configure root logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Add the project root to sys.path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import required modules
from src.analyzer import CodeAnalyzer
from src.patterns.architectural_intents import InformationHidingIntent

def main():
    """Directly test the Information Hiding pattern detector."""
    # Create the pattern detector
    info_hiding_detector = InformationHidingIntent()
    
    # Path to example directory
    example_dir = project_root / "examples" / "information_hiding"
    
    # List of Python files to analyze
    python_files = []
    for root, _, files in os.walk(example_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(python_files)} Python files to analyze")
    
    # Results for each file
    file_results = []
    
    # Create a mock tree-sitter parser to use
    from src.mock_implementation import MockTreeSitterTree, MockParser
    mock_parser = MockParser()
    
    # Analyze each file directly
    for file_path in python_files:
        logger.info(f"Analyzing {file_path}")
        
        # Parse the file
        tree = mock_parser.parse_file(file_path)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Match the pattern
        matches = info_hiding_detector.match(tree, code, 'python', file_path)
        logger.info(f"Found {len(matches)} information hiding matches in {file_path}")
        
        if matches:
            for match in matches:
                info_hiding_score = match.get('info_hiding_score', 0.0)
                logger.info(f"Information hiding score: {info_hiding_score}")
                
                # Log encapsulation metrics
                enc_metrics = match.get('encapsulation', {})
                logger.info(f"Encapsulation metrics: {enc_metrics}")
                
                # Log interface metrics
                if_metrics = match.get('interfaces', {})
                logger.info(f"Interface metrics: {if_metrics}")
                
                # Log module metrics
                mod_metrics = match.get('module_boundaries', {})
                logger.info(f"Module metrics: {mod_metrics}")
        
        # Store the results
        file_results.append({
            'file': file_path,
            'patterns': {'information_hiding': matches}
        })
    
    # Analyze the collective results
    architecture_results = info_hiding_detector.analyze_architecture(file_results)
    
    # Print final analysis
    logger.info("Overall Information Hiding Analysis:")
    logger.info(f"Confidence: {architecture_results.get('confidence', 0.0)}")
    logger.info(f"Components Analyzed: {architecture_results.get('components_analyzed', 0)}")
    logger.info(f"Description: {architecture_results.get('description', 'No description')}")
    
    # Print metrics
    if 'metrics' in architecture_results:
        logger.info("Metrics:")
        for key, value in architecture_results['metrics'].items():
            logger.info(f"  {key}: {value}")
    
    # Print recommendations
    if 'recommendations' in architecture_results:
        logger.info("Recommendations:")
        for rec in architecture_results['recommendations']:
            logger.info(f"  - {rec}")

if __name__ == "__main__":
    main()