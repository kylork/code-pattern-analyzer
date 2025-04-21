#!/usr/bin/env python3
"""
Example command for the Code Pattern Analyzer to test our new pattern detectors.
"""

import os
import sys
import json
from pprint import pprint
from pathlib import Path

# Add the project root to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Import the analyzer
from src.analyzer import CodeAnalyzer
from src.mock_implementation import patch_analyzer

# Patch the analyzer with mock implementations
restore_func = patch_analyzer()
try:
    # Create the analyzer with mock implementation
    analyzer = CodeAnalyzer(use_mock=True)
    
    # Run the analyzer on the dependency inversion examples
    example_dir = os.path.join(script_dir, "dependency_inversion")

    # Analyze the directory
    results = analyzer.analyze_directory(example_dir, category="architectural_intents")
    
    # Generate the report
    report = analyzer.generate_report(results, "text")
    
    # Print report
    print(report)
    
    # Analyze architectural intents
    print("\n\nARCHITECTURAL INTENT ANALYSIS")
    print("="*50)
    
    # Get components from results
    components = []
    for result in results:
        if "patterns" in result:
            for pattern_name, matches in result["patterns"].items():
                if pattern_name in ["dependency_inversion", "architectural_intent"]:
                    components.extend(matches)
    
    # Print the number of components found
    print(f"Found {len(components)} components with architectural intent")
    
    # Extract high-level metrics
    for component in components:
        if "dip_score" in component:
            print(f"\nComponent: {component.get('name', 'Unknown')}")
            print(f"DIP Score: {component.get('dip_score', 0.0):.2f}")
            
            if component.get("abstractions", {}).get("defines_interface", False):
                print("Defines interfaces/abstractions")
            
            if component.get("abstractions", {}).get("implements_interface", False):
                print("Implements interfaces/abstractions")
                
            if component.get("dependency_injection", {}).get("uses_di", False):
                print("Uses dependency injection")
                
            if component.get("factory_patterns", {}).get("uses_factories", False):
                print("Uses factory patterns")

finally:
    # Restore original implementation
    restore_func()