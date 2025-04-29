import unittest
from pathlib import Path
import tempfile
import os

from src.analyzer import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = CodeAnalyzer()
        
    def test_analyze_nonexistent_file(self):
        # Test analyzing a nonexistent file
        result = self.analyzer.analyze_file('/nonexistent/file.py')
        self.assertIn('error', result)
        
    def test_analyze_directory_not_dir(self):
        # Test that analyzing a non-directory raises NotADirectoryError
        with tempfile.NamedTemporaryFile() as tmp:
            with self.assertRaises(NotADirectoryError):
                self.analyzer.analyze_directory(tmp.name)
    
    def test_generate_report_json(self):
        # Test JSON report generation
        results = [{'file': 'test.py', 'patterns': {}}]
        report = self.analyzer.generate_report(results, 'json')
        self.assertIn('test.py', report)

if __name__ == '__main__':
    unittest.main()
