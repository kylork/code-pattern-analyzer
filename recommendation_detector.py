#!/usr/bin/env python3
"""
Pattern Recommendation Detector - Simplified CLI Version

This script identifies opportunities for refactoring code using design patterns
and provides simple guidance with code examples.

Usage:
    python recommendation_detector.py path/to/file_or_directory
"""

import os
import sys
import re
from pathlib import Path
import json

# Define our pattern detectors
DETECTORS = {
    "Factory Method": {
        "patterns": [
            r'if\s+.*?:\s*\n\s+return\s+(\w+)\(\)',
            r'if\s+.*?:\s*\n\s+return\s+(\w+)\(\).*?elif\s+.*?:\s*\n\s+return\s+(\w+)\(\)',
            r'switch\s*\([^)]+\)\s*{\s*case[^}]+new\s+\w+\([^)]*\)[^}]+}',
            r'if\s*\([^)]+\)\s*{\s*return\s*new\s+\w+\([^)]*\);\s*}\s*else'
        ],
        "description": "Object creation logic using conditional statements could be replaced with the Factory Method pattern",
        "benefits": [
            "Removes direct dependencies on concrete product classes",
            "Centralizes object creation logic",
            "Makes adding new product types easier without modifying existing code",
            "Promotes the Open/Closed Principle"
        ]
    },
    "Strategy": {
        "patterns": [
            r'if\s+.*?:\s*\n\s+.*?\n\s+.*?\n\s+elif\s+.*?:\s*\n\s+.*?\n\s+.*?\n\s+else',
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+if\s+.*?:\s*\n\s+.*?\n){2,}',
            r'switch\s*\([^)]+\)\s*{\s*case[^:]+:[^;]+;[^}]+case[^:]+:[^;]+;[^}]+}',
            r'if\s*\([^)]+\)\s*{\s*[^}]+\s*}\s*else\s+if\s*\([^)]+\)\s*{\s*[^}]+\s*}\s*else\s*{'
        ],
        "description": "Conditional logic selecting different behaviors could be replaced with the Strategy pattern",
        "benefits": [
            "Encapsulates algorithms in separate classes",
            "Allows easy switching between algorithms at runtime",
            "Avoids conditional logic in the context class",
            "Makes adding new strategies possible without changing existing code"
        ]
    },
    "Observer": {
        "patterns": [
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+.*?update\(.*?\)\s*\n)+',
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+.*?notify\(.*?\)\s*\n)+',
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+.*?on_change\(.*?\)\s*\n)+',
            r'for\s+\w+\s+in\s+\w+:\s*\n\s+\w+\.(?:update|notify|on_change)\(',
            r'function\s+\w+\([^)]*\)\s*{\s*(?:.*?\.update\(.*?\);)+',
            r'(?:this|self)\.(?:observers|listeners)\.forEach\(',
            r'for\s*\([^)]+\s+\w+\s*:\s*\w+\)\s*{\s*\w+\.(?:update|notify|onChange)\('
        ],
        "description": "Code that notifies multiple objects of changes could be refactored using the Observer pattern",
        "benefits": [
            "Establishes a clear one-to-many dependency between objects",
            "Supports loose coupling between the subject and observers",
            "Enables dynamic attachment and detachment of observers at runtime",
            "Encapsulates the notification mechanism"
        ]
    }
}

def detect_pattern_opportunities(file_path):
    """Detect pattern opportunities in a single file."""
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return []
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    opportunities = []
    
    # Run all detectors
    for pattern_name, detector in DETECTORS.items():
        for pattern in detector["patterns"]:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                start_line = code[:match.start()].count('\n') + 1
                end_line = start_line + code[match.start():match.end()].count('\n')
                
                # Extract the code snippet
                lines = code.splitlines()
                snippet = '\n'.join(lines[start_line-1:end_line])
                
                # Create the opportunity
                opportunity = {
                    "pattern_name": pattern_name,
                    "confidence": 0.8,  # Simplistic confidence value
                    "file_path": file_path,
                    "line_range": (start_line, end_line),
                    "description": detector["description"],
                    "benefits": detector["benefits"],
                    "code_snippet": snippet
                }
                opportunities.append(opportunity)
    
    # Add specific detector for the observer pattern with listeners
    if "self.listeners" in code and "for listener in self.listeners:" in code:
        # Find where listeners are being iterated over
        for match in re.finditer(r'for\s+listener\s+in\s+self\.listeners:\s*\n\s+listener\.(\w+)\(', code, re.DOTALL):
            start_line = code[:match.start()].count('\n') + 1
            end_line = start_line + code[match.start():match.end()].count('\n')
            
            # Extract the code snippet
            lines = code.splitlines()
            snippet = '\n'.join(lines[start_line-1:end_line])
            
            # Create the opportunity
            opportunity = {
                "pattern_name": "Observer",
                "confidence": 0.9,  # Higher confidence for this specific pattern
                "file_path": file_path,
                "line_range": (start_line, end_line),
                "description": "Code is already using a basic Observer pattern with listeners, but could be improved with a formal Observer interface",
                "benefits": DETECTORS["Observer"]["benefits"],
                "code_snippet": snippet
            }
            opportunities.append(opportunity)
    
    return opportunities

def analyze_directory(directory_path):
    """Analyze a directory for pattern opportunities."""
    results = {}
    
    # Walk through directory
    for root, dirs, files in os.walk(directory_path):
        # Skip common directories to ignore
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__']]
        
        for file in files:
            # Skip non-source files
            if not file.endswith(('.py', '.js', '.ts', '.java')):
                continue
                
            file_path = os.path.join(root, file)
            opportunities = detect_pattern_opportunities(file_path)
            
            if opportunities:
                results[file_path] = opportunities
    
    return results

def print_results(opportunities):
    """Print pattern opportunities in a readable format."""
    print("\n===== DESIGN PATTERN OPPORTUNITIES =====\n")
    
    if not opportunities:
        print("No pattern opportunities found.")
        return
    
    pattern_counts = {}
    for file_path, file_opps in opportunities.items():
        for opp in file_opps:
            pattern_counts[opp["pattern_name"]] = pattern_counts.get(opp["pattern_name"], 0) + 1
    
    total = sum(pattern_counts.values())
    print(f"Found {total} potential pattern applications across {len(opportunities)} files:\n")
    
    for pattern, count in pattern_counts.items():
        print(f"- {pattern}: {count}")
    
    print("\n--- Detailed Recommendations ---\n")
    
    for file_path, file_opps in opportunities.items():
        print(f"File: {file_path}")
        
        for opp in file_opps:
            print(f"  {opp['pattern_name']} Pattern (lines {opp['line_range'][0]}-{opp['line_range'][1]})")
            print(f"  Description: {opp['description']}")
            print("  Benefits:")
            for benefit in opp["benefits"]:
                print(f"    - {benefit}")
            print(f"  Code snippet:")
            for line in opp["code_snippet"].splitlines():
                print(f"    {line}")
            print()
        print("-" * 40)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python recommendation_detector.py <file_or_directory>")
        return 1
    
    target = sys.argv[1]
    
    try:
        # Check if target exists
        if not os.path.exists(target):
            print(f"Target does not exist: {target}")
            return 1
        
        # Analyze target
        if os.path.isfile(target):
            opportunities = {target: detect_pattern_opportunities(target)}
        else:
            opportunities = analyze_directory(target)
        
        # Print results
        print_results(opportunities)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())