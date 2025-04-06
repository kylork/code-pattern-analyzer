#!/usr/bin/env python3
"""
A demo script to test the Code Pattern Analyzer with sample files.
"""

import argparse
import json
import os
import logging
from pathlib import Path

# Make sure we can import from our package
import sys
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import after setting up path
from src.analyzer import CodeAnalyzer
from src.mock_implementation import patch_analyzer

# Ensure samples directory exists
samples_dir = os.path.join(project_dir, "samples")
if not os.path.exists(samples_dir):
    # If samples directory doesn't exist, check if files exist in root
    if os.path.exists(os.path.join(project_dir, "singleton_sample.py")):
        samples_dir = project_dir

# Default sample files
SAMPLES = {
    'python': {
        'singleton': os.path.join(samples_dir, "singleton_sample.py"),
        'factory': os.path.join(samples_dir, "factory_sample.py"),
        'code_smells': os.path.join(samples_dir, "code_smells.py"),
    },
    'javascript': {
        'patterns': os.path.join(samples_dir, "patterns.js"),
    }
}

def main():
    parser = argparse.ArgumentParser(description="Run a demo of the Code Pattern Analyzer")
    parser.add_argument("--file", "-f", help="File to analyze (defaults to sample files)")
    parser.add_argument("--pattern", "-p", help="Pattern to look for (defaults to all)")
    parser.add_argument("--category", "-c", help="Category to look for (defaults to all)")
    parser.add_argument("--format", choices=["json", "text", "html"], default="text", 
                      help="Output format (default: text)")
    parser.add_argument("--language", choices=["python", "javascript"], help="Language to analyze")
    parser.add_argument("--sample", choices=["singleton", "factory", "code_smells", "patterns"],
                      help="Sample file to analyze")
    parser.add_argument("--mock", action="store_true", help="Use mock implementation")
    parser.add_argument("--real", action="store_true", help="Use real tree-sitter implementation")
    args = parser.parse_args()
    
    # Determine if we should use mock implementation
    use_mock = True
    if args.real:
        use_mock = False
    elif args.mock:
        use_mock = True
    else:
        # Default based on environment
        use_mock = os.environ.get('CODE_PATTERN_USE_MOCK', 'True').lower() in ('true', '1', 'yes')
    
    # Use the selected implementation
    if use_mock:
        logging.info("Using mock implementation")
        restore_original = patch_analyzer()
    else:
        logging.info("Using tree-sitter implementation")
        restore_original = lambda: None
    
    try:
        # Determine the file to analyze
        if args.file:
            file_path = args.file
        elif args.sample and args.language:
            # Use a specific sample
            file_path = SAMPLES[args.language].get(args.sample)
            if not file_path:
                print(f"No sample file found for {args.language}/{args.sample}")
                return
        elif args.sample:
            # Find the sample in any language
            for language, samples in SAMPLES.items():
                if args.sample in samples:
                    file_path = samples[args.sample]
                    break
            else:
                print(f"No sample file found for {args.sample}")
                return
        elif args.language:
            # Use the first sample for the language
            if args.language in SAMPLES and SAMPLES[args.language]:
                file_path = next(iter(SAMPLES[args.language].values()))
            else:
                print(f"No sample files found for {args.language}")
                return
        else:
            # Default to the Python singleton sample
            file_path = SAMPLES['python']['singleton']
        
        # Create an analyzer
        analyzer = CodeAnalyzer()
        
        # Analyze the file
        results = analyzer.analyze_file(file_path, args.pattern, args.category)
        
        # Generate a report
        report = analyzer.generate_report([results], args.format)
        
        # Print the report
        print(f"\nAnalyzing: {file_path}")
        print("=" * 80)
        if args.pattern:
            print(f"Looking for pattern: {args.pattern}")
        elif args.category:
            print(f"Looking for category: {args.category}")
        else:
            print("Looking for all patterns")
        print("=" * 80)
        print(report)
        
    finally:
        # Restore the original implementation
        restore_original()

if __name__ == "__main__":
    main()