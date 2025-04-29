"""
Tests for the interactive refactoring module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import os
import tempfile
import subprocess
from io import StringIO

# Add the src directory to the path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.refactoring.interactive_refactoring import (
    InteractiveRefactoringSession,
    InteractiveCodeEditor
)
from src.refactoring.refactoring_suggestion import (
    RefactoringType,
    SuggestionImpact,
    RefactoringSuggestion
)


class TestInteractiveRefactoringSession(unittest.TestCase):
    """Tests for the InteractiveRefactoringSession class."""
    
    def setUp(self):
        # Create sample suggestions
        self.suggestions = [
            RefactoringSuggestion(
                refactoring_type=RefactoringType.EXTRACT_METHOD,
                description="Extract method 1",
                file_path="/path/to/file1.py",
                line_range=(10, 15),
                impact=SuggestionImpact.MEDIUM,
                source="complexity",
                before_code="def func1(): pass",
                after_code="def func1(): helper()\n\ndef helper(): pass",
                benefits=["Benefit 1", "Benefit 2"]
            ),
            RefactoringSuggestion(
                refactoring_type=RefactoringType.APPLY_FACTORY_PATTERN,
                description="Apply Factory Pattern",
                file_path="/path/to/file2.py",
                line_range=(20, 25),
                impact=SuggestionImpact.HIGH,
                source="pattern",
                before_code="def create_obj(): return Object()",
                after_code="class Factory:\n    def create_obj(self): return Object()",
                benefits=["Benefit 3"]
            )
        ]
        
        # Create the session
        self.session = InteractiveRefactoringSession(self.suggestions)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('src.refactoring.interactive_refactoring.TransformerFactory.create_transformer')
    def test_start_apply_all(self, mock_create_transformer, mock_print, mock_input):
        """Test starting an interactive session and applying all suggestions."""
        # Set up the mock transformer
        mock_transformer = MagicMock()
        mock_transformer.transform.return_value = (True, "Success")
        mock_create_transformer.return_value = mock_transformer
        
        # Set up the mock input to apply all suggestions
        mock_input.side_effect = ['a', 'a', 'a']  # Apply, Apply, Quit
        
        # Start the session
        results = self.session.start()
        
        # Check the results
        self.assertEqual(len(results["applied"]), 2)
        self.assertEqual(len(results["skipped"]), 0)
        self.assertEqual(results["total"], 2)
        
        # Verify the transformer was called for each suggestion
        self.assertEqual(mock_create_transformer.call_count, 2)
        self.assertEqual(mock_transformer.transform.call_count, 2)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_start_skip_all(self, mock_print, mock_input):
        """Test starting an interactive session and skipping all suggestions."""
        # Set up the mock input to skip all suggestions
        mock_input.side_effect = ['s', 's', 'q']  # Skip, Skip, Quit
        
        # Start the session
        results = self.session.start()
        
        # Check the results
        self.assertEqual(len(results["applied"]), 0)
        self.assertEqual(len(results["skipped"]), 2)
        self.assertEqual(results["total"], 2)
    
    @patch('builtins.input')
    @patch('builtins.print')
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    @patch('os.path.exists')
    @patch('os.unlink')
    def test_edit_suggestion(self, mock_unlink, mock_exists, mock_subprocess, mock_temp_file, mock_print, mock_input):
        """Test editing a suggestion before applying it."""
        # Set up temporary file mock
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/tempfile'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        
        # Set up file read mock
        with patch('builtins.open', mock_open(read_data="def func1(): edited()\n\ndef edited(): pass")):
            # Set up environment variable mock
            with patch.dict('os.environ', {'EDITOR': 'nano'}):
                # Set up the mock input to edit and then skip
                mock_input.side_effect = ['e', 's', 'q']  # Edit, Skip, Quit
                mock_exists.return_value = True
                
                # Start the session
                results = self.session.start()
                
                # Check the results
                self.assertEqual(len(results["applied"]), 0)
                self.assertEqual(len(results["skipped"]), 1)
                self.assertEqual(results["total"], 2)
                
                # Verify the subprocess was called to open the editor
                mock_subprocess.assert_called_once_with(['nano', '/tmp/tempfile'])
                
                # Verify the temporary file was cleaned up
                mock_unlink.assert_called_once()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_diff(self, mock_print, mock_input):
        """Test showing a diff of the before and after code."""
        # Set up the mock input to show diff and then skip
        mock_input.side_effect = ['d', 's', 'q']  # Diff, Skip, Quit
        
        # Start the session
        results = self.session.start()
        
        # Check the results
        self.assertEqual(len(results["applied"]), 0)
        self.assertEqual(len(results["skipped"]), 1)
        self.assertEqual(results["total"], 2)
        
        # Verify print was called multiple times for the diff
        self.assertTrue(mock_print.call_count > 10)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_show_help(self, mock_print, mock_input):
        """Test showing help information."""
        # Set up the mock input to show help and then quit
        mock_input.side_effect = ['h', 'q']  # Help, Quit
        
        # Start the session
        results = self.session.start()
        
        # Check the results
        self.assertEqual(len(results["applied"]), 0)
        self.assertEqual(len(results["skipped"]), 0)
        self.assertEqual(results["total"], 2)
        
        # Verify print was called multiple times for the help
        self.assertTrue(mock_print.call_count > 5)


class TestInteractiveCodeEditor(unittest.TestCase):
    """Tests for the InteractiveCodeEditor class."""
    
    def setUp(self):
        # Create a sample suggestion
        self.suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            description="Extract method from complex function",
            file_path="/path/to/file.py",
            line_range=(10, 15),
            impact=SuggestionImpact.MEDIUM,
            source="complexity",
            before_code="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value",
            after_code="def complex_function():\n    value = simple_calculation()\n    print(value)\n    return value\n\ndef simple_calculation():\n    # Complex code\n    return 1 + 2",
            benefits=["Improve readability", "Reduce complexity"]
        )
        
        # Create the editor
        self.editor = InteractiveCodeEditor("/path/to/file.py", self.suggestion)
    
    @patch('builtins.open', new_callable=mock_open, read_data="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value")
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    @patch('os.path.exists')
    @patch('os.unlink')
    def test_edit_with_changes(self, mock_unlink, mock_exists, mock_subprocess, mock_temp_file, mock_file):
        """Test editing a file with changes."""
        # Set up temporary file mock
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/tempfile'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        
        # Set up environment variable mock
        with patch.dict('os.environ', {'EDITOR': 'nano'}):
            # Set up the mock to return different content when reading the edited file
            edited_content = "def complex_function():\n    # Modified code\n    value = calculate()\n    print(value)\n    return value\n\ndef calculate():\n    return 1 + 2"
            mock_file.side_effect = [
                mock_open(read_data="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value").return_value,
                mock_open(read_data=edited_content).return_value,
                mock_open().return_value
            ]
            
            mock_exists.return_value = True
            
            # Edit the file
            result = self.editor.edit()
            
            # Check the result
            self.assertTrue(result)
            
            # Verify the subprocess was called to open the editor
            mock_subprocess.assert_called_once_with(['nano', '/tmp/tempfile'])
            
            # Verify the temporary file was cleaned up
            mock_unlink.assert_called_once()
            
            # Verify the file was written with the modified content
            mock_file.assert_called_with("/path/to/file.py", "w")
    
    @patch('builtins.open', new_callable=mock_open, read_data="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value")
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.call')
    @patch('os.path.exists')
    @patch('os.unlink')
    def test_edit_no_changes(self, mock_unlink, mock_exists, mock_subprocess, mock_temp_file, mock_file):
        """Test editing a file with no changes."""
        # Set up temporary file mock
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/tempfile'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        
        # Set up environment variable mock
        with patch.dict('os.environ', {'EDITOR': 'nano'}):
            # Set up the mock to return the same content when reading the edited file
            mock_file.side_effect = [
                mock_open(read_data="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value").return_value,
                mock_open(read_data="# REFACTORING GUIDANCE\n# \n# Description: Extract method from complex function\n# Type: EXTRACT_METHOD\n# Lines: 10-15\n#\n# Benefits:\n# - Improve readability\n# - Reduce complexity\n#\n# Make your changes below this line.\n# The original code follows:\n\ndef complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value").return_value
            ]
            
            mock_exists.return_value = True
            
            # Edit the file
            result = self.editor.edit()
            
            # Check the result
            self.assertFalse(result)
            
            # Verify the subprocess was called to open the editor
            mock_subprocess.assert_called_once_with(['nano', '/tmp/tempfile'])
            
            # Verify the temporary file was cleaned up
            mock_unlink.assert_called_once()
            
            # Verify the file was not written
            mock_file.assert_not_called()
    
    @patch('builtins.open')
    def test_edit_file_error(self, mock_open):
        """Test handling errors when editing a file."""
        # Set up the mock to raise an exception
        mock_open.side_effect = IOError("File not found")
        
        # Edit the file
        result = self.editor.edit()
        
        # Check the result
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()