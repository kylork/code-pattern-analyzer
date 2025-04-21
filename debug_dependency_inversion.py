#!/usr/bin/env python3
"""
Debug script for testing the Dependency Inversion pattern detector.

This script is used to directly test the DependencyInversionIntent pattern
detector against example code.
"""

import os
import sys
import json
from pprint import pprint
from typing import Dict, List, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.patterns.architectural_intents.dependency_inversion import DependencyInversionIntent
from src.mock_implementation import MockTreeSitterTree, patch_analyzer

# Create a patch to use mock implementations
restore_func = patch_analyzer()

def process_file(pattern, file_path: str, language: str = "python") -> Dict:
    """Process a single file with the pattern detector.
    
    Args:
        pattern: The pattern detector
        file_path: Path to the file to analyze
        language: Programming language
        
    Returns:
        Pattern detection results
    """
    print(f"\nProcessing file: {file_path}")
    
    # Read the file
    with open(file_path, 'r') as f:
        code = f.read()
    
    # Create a mock tree
    tree = MockTreeSitterTree(code, language)
    
    # Match the pattern
    results = pattern.match(tree, code, language, file_path)
    
    # Print results
    print(f"Found {len(results)} matches")
    
    for result in results:
        print("\nDIP Score:", result.get('dip_score', 0.0))
        
        # Print abstraction metrics
        abstractions = result.get('abstractions', {})
        print("\nAbstractions:")
        print(f"  Defines interface: {abstractions.get('defines_interface', False)}")
        print(f"  Implements interface: {abstractions.get('implements_interface', False)}")
        print(f"  Interface count: {abstractions.get('interface_count', 0)}")
        print(f"  Abstract method count: {abstractions.get('abstract_method_count', 0)}")
        print(f"  Depends on interfaces: {abstractions.get('depends_on_interfaces', False)}")
        print(f"  Interface dependency count: {abstractions.get('interface_dependency_count', 0)}")
        
        # Print dependency injection metrics
        di_metrics = result.get('dependency_injection', {})
        print("\nDependency Injection:")
        print(f"  Uses DI: {di_metrics.get('uses_di', False)}")
        print(f"  DI instance count: {di_metrics.get('di_instance_count', 0)}")
        print(f"  Constructor injection: {di_metrics.get('constructor_injection', False)}")
        print(f"  DI framework usage: {di_metrics.get('di_framework_usage', False)}")
        
        # Print factory pattern metrics
        factory_metrics = result.get('factory_patterns', {})
        print("\nFactory Patterns:")
        print(f"  Uses factories: {factory_metrics.get('uses_factories', False)}")
        print(f"  Factory method count: {factory_metrics.get('factory_method_count', 0)}")
        print(f"  Factory class count: {factory_metrics.get('factory_class_count', 0)}")
        print(f"  Instance creation points: {factory_metrics.get('instance_creation_points', 0)}")

def main():
    """Main entry point."""
    try:
        # Create a fresh pattern detector
        pattern = DependencyInversionIntent()
        
        # Directory to analyze
        example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "examples", "dependency_inversion")
    
        if not os.path.exists(example_dir):
            print(f"Error: Example directory not found: {example_dir}")
            return
        
        # Analyze each Python file in the directory
        all_results = []
        for filename in os.listdir(example_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(example_dir, filename)
                result = process_file(pattern, file_path)
                if result:  # Make sure result is not None
                    all_results.extend(result)
        
        # Build a fake component graph for analysis
        for result in all_results:
            pattern._process_pattern_matches(pattern.name, [result], result.get('path', ''))
        
        # Analyze the architecture
        arch_analysis = pattern._analyze_graph()
        
        print("\n" + "="*50)
        print("ARCHITECTURAL ANALYSIS")
        print("="*50)
        print(f"Confidence: {arch_analysis.get('confidence', 0.0):.2f}")
        print(f"Components analyzed: {arch_analysis.get('components_analyzed', 0)}")
        
        # Print metrics
        metrics = arch_analysis.get('metrics', {})
        print("\nMetrics:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Print description
        print("\nDescription:")
        print(arch_analysis.get('description', ''))
        
        # Print recommendations
        recommendations = arch_analysis.get('recommendations', [])
        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"  - {rec}")
    
    finally:
        # Restore original implementations
        if restore_func:
            restore_func()

if __name__ == "__main__":
    main()