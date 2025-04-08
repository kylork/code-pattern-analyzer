#!/usr/bin/env python3
"""
Test script to verify that both the mock and real tree-sitter implementations work.
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.analyzer import CodeAnalyzer

def main():
    """Test both implementations on a sample file."""
    # Get sample file
    sample_file = Path('samples/patterns.js')
    if not sample_file.exists():
        logger.error(f"Sample file {sample_file} not found")
        return
    
    # Test mock implementation
    logger.info("Testing mock implementation...")
    mock_analyzer = CodeAnalyzer(use_mock=True)
    mock_results = mock_analyzer.analyze_file(sample_file)
    
    print("\n=== MOCK IMPLEMENTATION RESULTS ===")
    print(f"File: {mock_results.get('file')}")
    print(f"Language: {mock_results.get('language')}")
    
    if 'patterns' in mock_results:
        for pattern_name, matches in mock_results['patterns'].items():
            print(f"\nPattern: {pattern_name} ({len(matches)} matches)")
            for match in matches[:5]:  # Show up to 5 matches
                print(f"  - {match.get('name')} at line {match.get('line')}")
            if len(matches) > 5:
                print(f"  ... and {len(matches) - 5} more matches.")
    
    # Test real implementation
    logger.info("Testing real tree-sitter implementation...")
    real_analyzer = CodeAnalyzer(use_mock=False)
    
    try:
        real_results = real_analyzer.analyze_file(sample_file)
        
        print("\n=== REAL TREE-SITTER IMPLEMENTATION RESULTS ===")
        print(f"File: {real_results.get('file')}")
        print(f"Language: {real_results.get('language')}")
        
        if 'patterns' in real_results:
            for pattern_name, matches in real_results['patterns'].items():
                print(f"\nPattern: {pattern_name} ({len(matches)} matches)")
                for match in matches[:5]:  # Show up to 5 matches
                    print(f"  - {match.get('name')} at line {match.get('line')}")
                if len(matches) > 5:
                    print(f"  ... and {len(matches) - 5} more matches.")
        
    except Exception as e:
        logger.error(f"Error testing real implementation: {e}")
        print("\n=== REAL TREE-SITTER IMPLEMENTATION ERROR ===")
        print(f"Error: {e}")
        print("Note: You may need to install the required language grammars.")
        print("The tree-sitter manager will attempt to download and build them when needed.")

if __name__ == "__main__":
    main()