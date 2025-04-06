"""
A mock implementation of the pattern detection functionality for demonstration purposes.
This simulates what would be done with actual tree-sitter in a real implementation.
"""

import re
from typing import Dict, List, Optional, Union
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MockTreeSitterTree:
    """A mock tree-sitter Tree object."""
    
    def __init__(self, content: str, language: str):
        self.content = content
        self.language = language


class MockParser:
    """A mock implementation of the parser."""
    
    def parse_file(self, file_path: Union[str, Path]) -> MockTreeSitterTree:
        """Parse a file and return a mock tree."""
        file_path = Path(file_path)
        content = file_path.read_text(encoding="utf-8")
        # Determine language based on file extension
        ext = os.path.splitext(str(file_path))[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.rb': 'ruby',
            '.go': 'go',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.rs': 'rust',
        }
        language = language_map.get(ext, 'unknown')
        
        return MockTreeSitterTree(content, language)


class MockFunctionPattern:
    """A mock implementation of function pattern detection."""
    
    def __init__(self):
        # Very simple regex-based function detection
        # In a real implementation, this would use tree-sitter queries
        self.patterns = {
            'python': r'def\s+(\w+)\s*\(',
            'javascript': r'function\s+(\w+)\s*\(',
            'typescript': r'function\s+(\w+)\s*\<|function\s+(\w+)\s*\(',
            'ruby': r'def\s+(\w+)',
            'go': r'func\s+(\w+)',
            'java': r'(?:public|private|protected|static)?\s+\w+\s+(\w+)\s*\(',
            'c': r'\w+\s+(\w+)\s*\(',
            'cpp': r'\w+\s+(\w+)\s*\(',
            'rust': r'fn\s+(\w+)',
        }
    
    def match(self, tree: MockTreeSitterTree) -> List[Dict]:
        """Find function definitions in the mock tree."""
        if tree.language not in self.patterns:
            return []
            
        pattern = self.patterns[tree.language]
        matches = []
        
        for line_num, line in enumerate(tree.content.splitlines(), 1):
            for match in re.finditer(pattern, line):
                func_name = match.group(1)
                if func_name:
                    matches.append({
                        'type': 'function',
                        'name': func_name,
                        'line': line_num,
                        'column': match.start(1),
                    })
        
        return matches


class MockClassPattern:
    """A mock implementation of class pattern detection."""
    
    def __init__(self):
        # Very simple regex-based class detection
        # In a real implementation, this would use tree-sitter queries
        self.patterns = {
            'python': r'class\s+(\w+)',
            'javascript': r'class\s+(\w+)',
            'typescript': r'class\s+(\w+)',
            'ruby': r'class\s+(\w+)',
            'java': r'class\s+(\w+)',
            'cpp': r'class\s+(\w+)',
            'rust': r'struct\s+(\w+)|enum\s+(\w+)',
        }
    
    def match(self, tree: MockTreeSitterTree) -> List[Dict]:
        """Find class definitions in the mock tree."""
        if tree.language not in self.patterns:
            return []
            
        pattern = self.patterns[tree.language]
        matches = []
        
        for line_num, line in enumerate(tree.content.splitlines(), 1):
            for match in re.finditer(pattern, line):
                class_name = match.group(1)
                if class_name:
                    matches.append({
                        'type': 'class',
                        'name': class_name,
                        'line': line_num,
                        'column': match.start(1),
                    })
        
        return matches


class MockSingletonPattern:
    """A mock implementation of Singleton pattern detection."""
    
    def __init__(self):
        # Simple regex-based Singleton detection
        self.python_patterns = [
            r'_instance\s*=\s*None', 
            r'instance\s*=\s*None',
            r'def\s+get_instance'
        ]
        self.js_pattern = r'static\s+(_instance|instance)\s*=\s*null'
    
    def match(self, tree: MockTreeSitterTree) -> List[Dict]:
        """Find Singleton patterns in the mock tree."""
        matches = []
        
        if tree.language == 'python':
            # Try each pattern
            for pattern in self.python_patterns:
                if re.search(pattern, tree.content):
                    # Find the class that contains the pattern
                    class_matches = re.finditer(r'class\s+(\w+)', tree.content)
                    for class_match in class_matches:
                        class_name = class_match.group(1)
                        class_start = class_match.start()
                        class_line = tree.content[:class_start].count('\n') + 1
                        
                        matches.append({
                            'type': 'design_pattern',
                            'pattern': 'singleton',
                            'name': class_name,
                            'line': class_line,
                            'column': 0,
                        })
                    break  # We found a singleton pattern, no need to check others
        
        elif tree.language in ('javascript', 'typescript') and re.search(self.js_pattern, tree.content):
            # Find the class that contains the instance
            class_matches = re.finditer(r'class\s+(\w+)', tree.content)
            for class_match in class_matches:
                class_name = class_match.group(1)
                class_start = class_match.start()
                class_line = tree.content[:class_start].count('\n') + 1
                
                matches.append({
                    'type': 'design_pattern',
                    'pattern': 'singleton',
                    'name': class_name,
                    'line': class_line,
                    'column': 0,
                })
        
        return matches


class MockFactoryPattern:
    """A mock implementation of Factory pattern detection."""
    
    def __init__(self):
        # Simple regex-based Factory detection
        self.python_pattern = r'def\s+(create|make|build|get)_(\w+)'
        self.js_pattern = r'(create|make|build|get)(\w+)'
    
    def match(self, tree: MockTreeSitterTree) -> List[Dict]:
        """Find Factory patterns in the mock tree."""
        matches = []
        
        if tree.language == 'python':
            for match in re.finditer(self.python_pattern, tree.content):
                matches.append({
                    'type': 'design_pattern',
                    'pattern': 'factory_method',
                    'name': match.group(0),
                    'line': tree.content[:match.start()].count('\n') + 1,
                    'column': 0,
                })
        
        elif tree.language in ('javascript', 'typescript'):
            for match in re.finditer(self.js_pattern, tree.content):
                if 'function' in tree.content[max(0, match.start()-20):match.start()]:
                    matches.append({
                        'type': 'design_pattern',
                        'pattern': 'factory_method',
                        'name': match.group(0),
                        'line': tree.content[:match.start()].count('\n') + 1,
                        'column': 0,
                    })
        
        return matches


# Initialize the mock patterns
mock_function_pattern = MockFunctionPattern()
mock_class_pattern = MockClassPattern()
mock_singleton_pattern = MockSingletonPattern()
mock_factory_pattern = MockFactoryPattern()

def patch_analyzer():
    """Patch the analyzer with mock implementations."""
    from .parser import CodeParser
    from .pattern_registry import registry
    
    logger.info("Patching analyzer with mock implementations")
    
    # Override the parse_file method to use the mock parser
    original_parse_file = CodeParser.parse_file
    def mock_parse_file(self, file_path):
        logger.debug(f"Using mock parser for {file_path}")
        parser = MockParser()
        return parser.parse_file(file_path)
    CodeParser.parse_file = mock_parse_file
    
    # We need to patch the pattern.match methods
    # Get all patterns from the registry
    original_pattern_match = {}
    for pattern_name, pattern in registry.patterns.items():
        if hasattr(pattern, 'match'):
            original_pattern_match[pattern_name] = pattern.match
            
            # Define a closure to capture the pattern name
            def make_mock_match(pattern_name):
                def mock_match(self, tree, code, language, file_path=None):
                    logger.debug(f"Using mock match for {pattern_name}")
                    
                    # Create a mock tree if we got a string instead
                    if isinstance(tree, str):
                        tree = MockTreeSitterTree(code, language)
                    
                    # Match using the appropriate mock pattern
                    if pattern_name == 'function_definition' or pattern_name == 'all_functions':
                        return mock_function_pattern.match(tree)
                    elif pattern_name == 'class_definition' or pattern_name == 'all_classes':
                        return mock_class_pattern.match(tree)
                    elif pattern_name == 'singleton':
                        return mock_singleton_pattern.match(tree)
                    elif pattern_name == 'factory_method':
                        return mock_factory_pattern.match(tree)
                    
                    # Default: return empty list
                    return []
                
                return mock_match
            
            # Patch the method
            pattern.match = make_mock_match(pattern_name)
    
    # Return a function to restore the original methods
    def restore():
        logger.info("Restoring original analyzer implementation")
        CodeParser.parse_file = original_parse_file
        
        # Restore pattern.match methods
        for pattern_name, match_method in original_pattern_match.items():
            if pattern_name in registry.patterns:
                registry.patterns[pattern_name].match = match_method
    
    return restore