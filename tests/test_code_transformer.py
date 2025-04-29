"""
Tests for the code transformer module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.refactoring.code_transformer import (
    CodeTransformer,
    ExtractMethodTransformer,
    FactoryPatternTransformer,
    StrategyPatternTransformer,
    ObserverPatternTransformer,
    TransformerFactory,
    BatchTransformer
)
from src.refactoring.refactoring_suggestion import (
    RefactoringType,
    SuggestionImpact,
    RefactoringSuggestion
)


class TestCodeTransformer(unittest.TestCase):
    """Tests for the CodeTransformer base class."""
    
    def test_base_transformer(self):
        """Test that the base transformer works as expected."""
        transformer = CodeTransformer()
        self.assertRaises(NotImplementedError, transformer.transform, None)
    
    def test_validate_file(self):
        """Test file validation."""
        transformer = CodeTransformer()
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_path = temp_file.name
        
        try:
            # File should exist and be readable
            self.assertTrue(transformer._validate_file(temp_path))
            
            # Non-existent file should fail validation
            self.assertFalse(transformer._validate_file("/nonexistent/file.txt"))
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        transformer = CodeTransformer()
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write("Original content")
            temp_path = temp_file.name
        
        try:
            # Create backup
            backup_path = transformer.backup_file(temp_path)
            
            # Check that backup was created and has the same content
            self.assertTrue(os.path.exists(backup_path))
            with open(backup_path, 'r') as f:
                self.assertEqual(f.read(), "Original content")
            
            # Modify the original file
            with open(temp_path, 'w') as f:
                f.write("Modified content")
            
            # Restore from backup
            transformer.restore_backup(backup_path)
            
            # Check that original file was restored
            with open(temp_path, 'r') as f:
                self.assertEqual(f.read(), "Original content")
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if os.path.exists(backup_path):
                os.unlink(backup_path)


class TestExtractMethodTransformer(unittest.TestCase):
    """Tests for the ExtractMethodTransformer."""
    
    def setUp(self):
        self.transformer = ExtractMethodTransformer()
        
        # Create a sample suggestion
        self.suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            description="Extract method from complex function",
            file_path="/path/to/file.py",
            line_range=(10, 15),
            impact=SuggestionImpact.MEDIUM,
            source="complexity",
            before_code="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value",
            after_code="def complex_function():\n    value = simple_calculation()\n    print(value)\n    return value\n\ndef simple_calculation():\n    # Complex code\n    return 1 + 2"
        )
    
    @patch('builtins.open', new_callable=mock_open, read_data="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value")
    @patch('os.path.isfile')
    @patch('os.access')
    @patch('shutil.copy2')
    @patch('os.remove')
    @patch('ast.parse')
    def test_extract_method_transform(self, mock_ast_parse, mock_remove, mock_copy, mock_access, mock_isfile, mock_file):
        """Test extracting a method."""
        # Set up mocks
        mock_isfile.return_value = True
        mock_access.return_value = True
        
        # Call the transformer
        success, message = self.transformer.transform(self.suggestion)
        
        # Check the result
        self.assertTrue(success)
        self.assertEqual(message, "Extract Method refactoring applied successfully")
        
        # Verify mocks were called
        mock_isfile.assert_called_once()
        mock_access.assert_called_once()
        mock_copy.assert_called_once()
        mock_file.assert_called()
        mock_ast_parse.assert_called_once()
        mock_remove.assert_called_once()
    
    def test_wrong_refactoring_type(self):
        """Test handling of wrong refactoring type."""
        suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.APPLY_FACTORY_PATTERN,
            description="Apply Factory Pattern",
            file_path="/path/to/file.py",
            line_range=(10, 15),
            impact=SuggestionImpact.MEDIUM,
            source="pattern"
        )
        
        success, message = self.transformer.transform(suggestion)
        self.assertFalse(success)
        self.assertIn("Expected EXTRACT_METHOD suggestion", message)
    
    @patch('os.path.isfile')
    @patch('os.access')
    def test_invalid_file(self, mock_access, mock_isfile):
        """Test handling of invalid file."""
        mock_isfile.return_value = False
        mock_access.return_value = False
        
        success, message = self.transformer.transform(self.suggestion)
        self.assertFalse(success)
        self.assertIn("does not exist or is not readable/writable", message)
    
    def test_missing_after_code(self):
        """Test handling of missing after_code."""
        suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            description="Extract method from complex function",
            file_path="/path/to/file.py",
            line_range=(10, 15),
            impact=SuggestionImpact.MEDIUM,
            source="complexity",
            before_code="def complex_function():\n    # Complex code\n    value = 1 + 2\n    print(value)\n    return value"
        )
        
        success, message = self.transformer.transform(suggestion)
        self.assertFalse(success)
        self.assertEqual("No transformed code provided in the suggestion", message)


class TestTransformerFactory(unittest.TestCase):
    """Tests for the TransformerFactory."""
    
    def test_create_transformer(self):
        """Test creating transformers for different refactoring types."""
        factory = TransformerFactory()
        
        # Test extract method transformer
        transformer = factory.create_transformer(RefactoringType.EXTRACT_METHOD)
        self.assertIsInstance(transformer, ExtractMethodTransformer)
        
        # Test factory pattern transformer
        transformer = factory.create_transformer(RefactoringType.APPLY_FACTORY_PATTERN)
        self.assertIsInstance(transformer, FactoryPatternTransformer)
        
        # Test strategy pattern transformer
        transformer = factory.create_transformer(RefactoringType.APPLY_STRATEGY_PATTERN)
        self.assertIsInstance(transformer, StrategyPatternTransformer)
        
        # Test observer pattern transformer
        transformer = factory.create_transformer(RefactoringType.APPLY_OBSERVER_PATTERN)
        self.assertIsInstance(transformer, ObserverPatternTransformer)
    
    def test_unsupported_refactoring_type(self):
        """Test handling of unsupported refactoring type."""
        factory = TransformerFactory()
        
        # This should raise a ValueError
        with self.assertRaises(ValueError):
            factory.create_transformer(RefactoringType.RENAME)


class TestBatchTransformer(unittest.TestCase):
    """Tests for the BatchTransformer."""
    
    def setUp(self):
        self.batch_transformer = BatchTransformer()
        
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
                after_code="def func1(): helper()\n\ndef helper(): pass"
            ),
            RefactoringSuggestion(
                refactoring_type=RefactoringType.EXTRACT_METHOD,
                description="Extract method 2",
                file_path="/path/to/file2.py",
                line_range=(20, 25),
                impact=SuggestionImpact.HIGH,
                source="complexity",
                before_code="def func2(): pass",
                after_code="def func2(): helper2()\n\ndef helper2(): pass"
            )
        ]
    
    @patch('src.refactoring.code_transformer.TransformerFactory.create_transformer')
    def test_apply_suggestions(self, mock_create_transformer):
        """Test applying multiple suggestions."""
        # Set up mock transformer
        mock_transformer = MagicMock()
        mock_transformer.transform.side_effect = [
            (True, "Success 1"),
            (False, "Failure reason")
        ]
        mock_create_transformer.return_value = mock_transformer
        
        # Apply the suggestions
        results = self.batch_transformer.apply_suggestions(self.suggestions)
        
        # Check the results
        self.assertEqual(len(results["success"]), 1)
        self.assertEqual(len(results["failure"]), 1)
        self.assertEqual(results["success"][0]["message"], "Success 1")
        self.assertEqual(results["failure"][0]["message"], "Failure reason")
        
        # Verify the transformer was called for each suggestion
        self.assertEqual(mock_create_transformer.call_count, 2)
        self.assertEqual(mock_transformer.transform.call_count, 2)
    
    @patch('src.refactoring.code_transformer.TransformerFactory.create_transformer')
    def test_transformer_error(self, mock_create_transformer):
        """Test handling of transformer errors."""
        # Set up mock to raise an exception
        mock_create_transformer.side_effect = ValueError("Unsupported refactoring type")
        
        # Apply the suggestions
        results = self.batch_transformer.apply_suggestions(self.suggestions)
        
        # Check the results
        self.assertEqual(len(results["success"]), 0)
        self.assertEqual(len(results["failure"]), 2)
        self.assertIn("Unsupported refactoring type", results["failure"][0]["message"])


if __name__ == '__main__':
    unittest.main()