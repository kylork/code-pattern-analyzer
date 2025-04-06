import unittest
from pathlib import Path
import tempfile

from src.parser import CodeParser

class TestCodeParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = CodeParser()
        
    def test_get_language_by_extension(self):
        # Test Python detection
        self.assertEqual(self.parser._get_language_by_extension('test.py'), 'python')
        
        # Test JavaScript detection
        self.assertEqual(self.parser._get_language_by_extension('test.js'), 'javascript')
        
        # Test TypeScript detection
        self.assertEqual(self.parser._get_language_by_extension('test.ts'), 'typescript')
        
        # Test unknown extension
        self.assertIsNone(self.parser._get_language_by_extension('test.unknown'))
        
    def test_parse_file_nonexistent(self):
        # Test that parsing a nonexistent file raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file('/nonexistent/file.py')
            
    def test_parse_file_unsupported(self):
        # Create a temporary file with an unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.xyz') as tmp:
            # Test that parsing an unsupported file type raises ValueError
            with self.assertRaises(ValueError):
                self.parser.parse_file(tmp.name)
                
    def test_parse_code_unsupported_language(self):
        # Test that parsing with an unsupported language raises ValueError
        with self.assertRaises(ValueError):
            self.parser.parse_code('print("hello")', 'unsupported')

if __name__ == '__main__':
    unittest.main()
