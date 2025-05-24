#!/usr/bin/env python3

# This is a temporary fix script to correct syntax issues in refactoring_suggestion.py

import re

def fix_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Fix the problematic line
    content = content.replace(
        """            {"".join([f'<button onclick="filterByType(\\'{t}\\')">{t}</button>' for t in {s.refactoring_type.value for s in suggestions}])}""",
        """            {"".join(['<button onclick="filterByType(\\'{0}\\')"><{0}/button>'.format(t) for t in {s.refactoring_type.value for s in suggestions}])}"""
    )
    
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    file_path = "/root/claude-code-demo/code-pattern-analyzer/src/refactoring/refactoring_suggestion.py"
    fix_file(file_path)