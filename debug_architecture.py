"""
Debug script for testing architectural intent recognition directly.
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
from src.patterns.architectural_intents import ArchitecturalIntentDetector
from src.patterns.architectural_intents.separation_of_concerns import SeparationOfConcernsIntent

def main():
    """Main function for debugging the architectural intent recognition."""
    # Set up mock analyzer
    analyzer = CodeAnalyzer(use_mock=True)
    
    # Path to example directory
    example_dir = project_root / "examples" / "layered_architecture"
    
    # List of Python files to analyze
    python_files = []
    for root, _, files in os.walk(example_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(python_files)} Python files to analyze")
    
    # Create pattern detector directly
    pattern = SeparationOfConcernsIntent()
    
    # Manually process each file
    results = []
    for file_path in python_files:
        logger.info(f"Manually analyzing {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Try to match the pattern directly
        matches = []
        try:
            # Mock a tree for the file
            from src.mock_implementation import MockTreeSitterTree
            tree = MockTreeSitterTree(code, 'python')
            
            # Apply the pattern directly
            matches = pattern.match(tree, code, 'python', file_path)
            logger.info(f"Found {len(matches)} matches for {file_path}")
            
            # Create a result dictionary
            result = {
                'file': file_path,
                'language': 'python',
                'patterns': {'separation_of_concerns': matches},
                'summary': {
                    'total_patterns': len(matches),
                    'pattern_counts': {'separation_of_concerns': len(matches)},
                    'type_counts': {'component': len(matches)}
                }
            }
        except Exception as e:
            logger.error(f"Error matching pattern: {e}")
            import traceback
            logger.error(traceback.format_exc())
            result = {'error': str(e), 'file': file_path}
        
        results.append(result)
        logger.debug(f"Result: {result}")
    
    # Create detector
    detector = ArchitecturalIntentDetector()
    
    # Analyze codebase
    logger.info("Analyzing the entire codebase")
    architecture_analysis = detector.analyze_codebase(results, codebase_root=str(example_dir))
    
    # Print results
    logger.info(f"Architecture analysis: {architecture_analysis}")

if __name__ == "__main__":
    main()