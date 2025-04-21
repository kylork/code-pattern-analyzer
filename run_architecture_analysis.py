"""
Helper script to run architectural intent analysis on a directory.
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
from src.patterns.architectural_intents import ArchitecturalIntentDetector
from src.patterns.architectural_intents.separation_of_concerns import SeparationOfConcernsIntent
from src.commands.architecture import generate_text_report, generate_html_report

def analyze_architecture(directory_path, output_format='text'):
    """Run architectural intent analysis on a directory.
    
    Args:
        directory_path: Path to the directory to analyze
        output_format: Output format ('json', 'text', or 'html')
        
    Returns:
        Analysis results as a string in the specified format
    """
    directory_path = Path(directory_path)
    if not directory_path.is_dir():
        raise NotADirectoryError(f"{directory_path} is not a directory")
    
    # Create pattern detector
    pattern = SeparationOfConcernsIntent()
    
    # Find all Python files in the directory
    python_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(python_files)} Python files to analyze")
    
    # Manually process each file
    results = []
    for file_path in python_files:
        logger.info(f"Analyzing {file_path}")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Try to match the pattern directly
        try:
            # Mock a tree for the file
            from src.mock_implementation import MockTreeSitterTree
            tree = MockTreeSitterTree(code, 'python')
            
            # Apply the pattern directly
            matches = pattern.match(tree, code, 'python', file_path)
            
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
            logger.error(f"Error analyzing {file_path}: {e}")
            result = {'error': str(e), 'file': file_path}
        
        results.append(result)
    
    # Create detector
    detector = ArchitecturalIntentDetector()
    
    # Analyze codebase
    logger.info("Analyzing architectural intents")
    architecture_analysis = detector.analyze_codebase(results, codebase_root=str(directory_path))
    
    # Generate output in the specified format
    if output_format == 'json':
        return json.dumps(architecture_analysis, indent=2)
    elif output_format == 'text':
        return generate_text_report(architecture_analysis, str(directory_path))
    elif output_format == 'html':
        return generate_html_report(architecture_analysis, str(directory_path))
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_architecture_analysis.py <directory> [output_format]")
        sys.exit(1)
    
    directory = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'text'
    
    try:
        result = analyze_architecture(directory, output_format)
        print(result)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)