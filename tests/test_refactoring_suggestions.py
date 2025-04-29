"""
Tests for the refactoring suggestion module.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json
from pathlib import Path

# Add the src directory to the path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.refactoring.refactoring_suggestion import (
    RefactoringType,
    SuggestionImpact,
    RefactoringSuggestion,
    PatternBasedSuggestionGenerator,
    ComplexityBasedSuggestionGenerator,
    FlowAnalysisSuggestionGenerator,
    ArchitecturalSuggestionGenerator,
    CompositeSuggestionGenerator,
    generate_refactoring_report
)

class TestRefactoringSuggestion(unittest.TestCase):
    """Tests for the RefactoringSuggestion class."""

    def test_refactoring_suggestion_creation(self):
        """Test that a RefactoringSuggestion can be created with all attributes."""
        suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            description="Extract this code into a separate method",
            file_path="/path/to/file.py",
            line_range=(10, 20),
            impact=SuggestionImpact.MEDIUM,
            source="complexity",
            details={"complexity": 15},
            before_code="def foo():\n    # Complex code...",
            after_code="def foo():\n    bar()\n\ndef bar():\n    # Complex code...",
            benefits=["Improves readability", "Reduces complexity"],
            effort=3,
            affected_components=["module1", "module2"]
        )
        
        self.assertEqual(suggestion.refactoring_type, RefactoringType.EXTRACT_METHOD)
        self.assertEqual(suggestion.description, "Extract this code into a separate method")
        self.assertEqual(suggestion.file_path, "/path/to/file.py")
        self.assertEqual(suggestion.line_range, (10, 20))
        self.assertEqual(suggestion.impact, SuggestionImpact.MEDIUM)
        self.assertEqual(suggestion.source, "complexity")
        self.assertEqual(suggestion.details, {"complexity": 15})
        self.assertEqual(suggestion.before_code, "def foo():\n    # Complex code...")
        self.assertEqual(suggestion.after_code, "def foo():\n    bar()\n\ndef bar():\n    # Complex code...")
        self.assertEqual(suggestion.benefits, ["Improves readability", "Reduces complexity"])
        self.assertEqual(suggestion.effort, 3)
        self.assertEqual(suggestion.affected_components, ["module1", "module2"])
    
    def test_to_dict(self):
        """Test that a RefactoringSuggestion can be converted to a dictionary."""
        suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            description="Extract this code into a separate method",
            file_path="/path/to/file.py",
            line_range=(10, 20),
            impact=SuggestionImpact.MEDIUM,
            source="complexity"
        )
        
        suggestion_dict = suggestion.to_dict()
        self.assertEqual(suggestion_dict["refactoring_type"], "EXTRACT_METHOD")
        self.assertEqual(suggestion_dict["description"], "Extract this code into a separate method")
        self.assertEqual(suggestion_dict["file_path"], "/path/to/file.py")
        self.assertEqual(suggestion_dict["line_range"], [10, 20])
        self.assertEqual(suggestion_dict["impact"], "medium")
        self.assertEqual(suggestion_dict["source"], "complexity")

class TestSuggestionGenerators(unittest.TestCase):
    """Tests for the suggestion generator classes."""
    
    @patch("src.refactoring.refactoring_suggestion.PatternBasedSuggestionGenerator._analyze_patterns")
    def test_pattern_based_generator(self, mock_analyze):
        """Test that PatternBasedSuggestionGenerator generates suggestions."""
        # Set up mock to return a sample suggestion
        suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.APPLY_FACTORY_PATTERN,
            description="Apply Factory Pattern here",
            file_path="/path/to/file.py",
            line_range=(10, 20),
            impact=SuggestionImpact.HIGH,
            source="pattern"
        )
        mock_analyze.return_value = [suggestion]
        
        # Create generator and call generate_suggestions
        generator = PatternBasedSuggestionGenerator()
        suggestions = generator.generate_suggestions("/path/to/target")
        
        # Verify the suggestions
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].refactoring_type, RefactoringType.APPLY_FACTORY_PATTERN)
        self.assertEqual(suggestions[0].source, "pattern")
        
        # Verify the mock was called
        mock_analyze.assert_called_once_with("/path/to/target")

    @patch("src.refactoring.refactoring_suggestion.CompositeSuggestionGenerator._get_generator_instances")
    def test_composite_generator(self, mock_get_generators):
        """Test that CompositeSuggestionGenerator aggregates suggestions from all generators."""
        # Create mock generators
        pattern_suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.APPLY_FACTORY_PATTERN,
            description="Apply Factory Pattern",
            file_path="/path/to/file1.py",
            line_range=(10, 20),
            impact=SuggestionImpact.HIGH,
            source="pattern"
        )
        
        complexity_suggestion = RefactoringSuggestion(
            refactoring_type=RefactoringType.EXTRACT_METHOD,
            description="Extract method",
            file_path="/path/to/file2.py",
            line_range=(30, 40),
            impact=SuggestionImpact.MEDIUM,
            source="complexity"
        )
        
        # Create mock generators
        pattern_generator = MagicMock()
        pattern_generator.generate_suggestions.return_value = [pattern_suggestion]
        
        complexity_generator = MagicMock()
        complexity_generator.generate_suggestions.return_value = [complexity_suggestion]
        
        # Set up mock to return our mock generators
        mock_get_generators.return_value = [pattern_generator, complexity_generator]
        
        # Create composite generator and call generate_all_suggestions
        generator = CompositeSuggestionGenerator()
        suggestions = generator.generate_all_suggestions("/path/to/target")
        
        # Verify the suggestions
        self.assertEqual(len(suggestions), 2)
        self.assertIn(pattern_suggestion, suggestions)
        self.assertIn(complexity_suggestion, suggestions)
        
        # Verify the mocks were called
        pattern_generator.generate_suggestions.assert_called_once_with("/path/to/target")
        complexity_generator.generate_suggestions.assert_called_once_with("/path/to/target")

class TestReportGeneration(unittest.TestCase):
    """Tests for the report generation functions."""
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        # Create sample suggestions
        suggestions = [
            RefactoringSuggestion(
                refactoring_type=RefactoringType.EXTRACT_METHOD,
                description="Extract method",
                file_path="/path/to/file.py",
                line_range=(10, 20),
                impact=SuggestionImpact.MEDIUM,
                source="complexity"
            ),
            RefactoringSuggestion(
                refactoring_type=RefactoringType.APPLY_FACTORY_PATTERN,
                description="Apply Factory Pattern",
                file_path="/path/to/file2.py",
                line_range=(30, 40),
                impact=SuggestionImpact.HIGH,
                source="pattern"
            )
        ]
        
        # Create a temporary file for the report
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate the report
            generate_refactoring_report(suggestions, temp_path, "json")
            
            # Read the report
            with open(temp_path, "r") as f:
                report_data = json.load(f)
            
            # Verify the report
            self.assertEqual(len(report_data), 2)
            self.assertEqual(report_data[0]["refactoring_type"], "EXTRACT_METHOD")
            self.assertEqual(report_data[1]["refactoring_type"], "APPLY_FACTORY_PATTERN")
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_generate_text_report(self):
        """Test text report generation."""
        # Create sample suggestions
        suggestions = [
            RefactoringSuggestion(
                refactoring_type=RefactoringType.EXTRACT_METHOD,
                description="Extract method",
                file_path="/path/to/file.py",
                line_range=(10, 20),
                impact=SuggestionImpact.MEDIUM,
                source="complexity"
            )
        ]
        
        # Create a temporary file for the report
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate the report
            generate_refactoring_report(suggestions, temp_path, "text")
            
            # Read the report
            with open(temp_path, "r") as f:
                report_text = f.read()
            
            # Verify the report contains expected content
            self.assertIn("EXTRACT_METHOD", report_text)
            self.assertIn("Extract method", report_text)
            self.assertIn("/path/to/file.py", report_text)
            self.assertIn("10-20", report_text)
            self.assertIn("MEDIUM", report_text)
        finally:
            # Clean up
            os.unlink(temp_path)

if __name__ == "__main__":
    unittest.main()