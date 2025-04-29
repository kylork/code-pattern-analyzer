"""
Tests for enhanced pattern detection implementations.
"""

import os
import unittest
from pathlib import Path

from src.analyzer import CodeAnalyzer
from src.pattern_registry import registry
from src.patterns.enhanced.strategy_pattern_enhanced import (
    StrategyPatternPythonEnhanced,
    StrategyPatternEnhanced,
)


class TestEnhancedPatternDetection(unittest.TestCase):
    """Test cases for enhanced pattern detection."""

    def setUp(self):
        """Set up the test environment."""
        # Register the enhanced patterns for testing
        self.original_registry = registry.patterns.copy()
        registry.register(StrategyPatternPythonEnhanced(), ["design_patterns"])
        registry.register(StrategyPatternEnhanced(), ["design_patterns"])
        
        # Initialize analyzer
        self.analyzer = CodeAnalyzer()
        
        # Get the project root directory
        self.project_root = Path(__file__).parent.parent
        
        # Path to sample files
        self.samples_dir = self.project_root / "samples"
        
        # Use real implementation if available
        os.environ["CODE_PATTERN_USE_MOCK"] = "False"

    def tearDown(self):
        """Clean up after tests."""
        # Restore the original registry
        registry.patterns = self.original_registry

    def test_repository_based_strategy_detection(self):
        """Test detection of repository-based Strategy pattern."""
        file_path = self.samples_dir / "repository_strategy_sample.py"
        
        # Only run if tree-sitter is available
        try:
            results = self.analyzer.analyze_file(
                file_path=str(file_path),
                categories=["design_patterns"],
                pattern_names=["strategy_python_enhanced"]
            )
            
            # Check if we have pattern matches
            self.assertTrue(len(results) > 0, "No patterns detected")
            
            # Check for repository pattern components
            repository_found = False
            repository_context_found = False
            
            for match in results:
                if match.get("role") == "strategy_repository":
                    repository_found = True
                elif match.get("role") == "repository_context":
                    repository_context_found = True
            
            self.assertTrue(repository_found, "Repository pattern not detected")
            self.assertTrue(repository_context_found, "Repository context not detected")
            
            # Additional check for implementation type
            repository_implementation_found = False
            for match in results:
                if match.get("implementation") == "repository-based":
                    repository_implementation_found = True
                    break
            
            self.assertTrue(repository_implementation_found, 
                           "Repository-based implementation type not detected")
            
        except ImportError:
            self.skipTest("Tree-sitter not available")


if __name__ == "__main__":
    unittest.main()