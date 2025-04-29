"""
Code transformer module for the Code Pattern Analyzer.

This module provides functionality for automatically transforming code
based on refactoring suggestions, including applying design patterns
and performing common refactorings.
"""

import os
import sys
import ast
import logging
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional, Any, Set, Union

from src.refactoring.refactoring_suggestion import RefactoringSuggestion, RefactoringType


class CodeTransformer:
    """Base class for code transformers."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def transform(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Transform code based on the suggestion.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def backup_file(self, file_path: str) -> str:
        """Create a backup of the file before transformation.
        
        Args:
            file_path: Path to the file to back up
            
        Returns:
            Path to the backup file
        """
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def restore_backup(self, backup_path: str) -> None:
        """Restore file from backup if transformation fails.
        
        Args:
            backup_path: Path to the backup file
        """
        original_path = backup_path[:-4]  # Remove .bak extension
        shutil.copy2(backup_path, original_path)
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate that the file exists and is readable.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file is valid, False otherwise
        """
        return os.path.isfile(file_path) and os.access(file_path, os.R_OK | os.W_OK)


class ExtractMethodTransformer(CodeTransformer):
    """Transformer for Extract Method refactoring."""
    
    def transform(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Apply Extract Method refactoring.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        if suggestion.refactoring_type != RefactoringType.EXTRACT_METHOD:
            return False, f"Expected EXTRACT_METHOD suggestion, got {suggestion.refactoring_type.value}"
        
        if not self._validate_file(suggestion.file_path):
            return False, f"File {suggestion.file_path} does not exist or is not readable/writable"
        
        if suggestion.after_code is None:
            return False, "No transformed code provided in the suggestion"
        
        try:
            # Create backup
            backup_path = self.backup_file(suggestion.file_path)
            
            # Read the file
            with open(suggestion.file_path, 'r') as f:
                file_content = f.read()
            
            # Extract the code to replace
            start_line, end_line = suggestion.line_range
            lines = file_content.split('\n')
            before_code = '\n'.join(lines[start_line-1:end_line])
            
            if before_code.strip() != suggestion.before_code.strip():
                self.logger.warning("Source code has changed since the suggestion was generated")
            
            # Replace the code
            new_content = file_content.replace(before_code, suggestion.after_code)
            
            # Write the transformed code
            with open(suggestion.file_path, 'w') as f:
                f.write(new_content)
            
            # Validate syntax
            try:
                with open(suggestion.file_path, 'r') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                self.restore_backup(backup_path)
                return False, f"Syntax error in transformed code: {str(e)}"
            
            # Remove backup if successful
            os.remove(backup_path)
            
            return True, "Extract Method refactoring applied successfully"
        
        except Exception as e:
            # Restore backup if exists
            if 'backup_path' in locals():
                self.restore_backup(backup_path)
            
            return False, f"Error applying Extract Method refactoring: {str(e)}"


class FactoryPatternTransformer(CodeTransformer):
    """Transformer for Factory Pattern refactoring."""
    
    def transform(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Apply Factory Pattern refactoring.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        if suggestion.refactoring_type != RefactoringType.APPLY_FACTORY_PATTERN:
            return False, f"Expected FACTORY_METHOD suggestion, got {suggestion.refactoring_type.value}"
        
        if not self._validate_file(suggestion.file_path):
            return False, f"File {suggestion.file_path} does not exist or is not readable/writable"
        
        if suggestion.after_code is None:
            # Need to generate the factory pattern code
            return self._generate_factory_pattern(suggestion)
        else:
            # Use the provided after_code
            return self._apply_transformed_code(suggestion)
    
    def _generate_factory_pattern(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Generate Factory Pattern code.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        # This would contain logic to generate a factory pattern implementation
        # based on the details in the suggestion
        
        try:
            from src.pattern_transformer import PatternTransformer
            
            # Create a pattern transformer
            transformer = PatternTransformer()
            
            # Generate the factory pattern
            result = transformer.apply_factory_pattern(
                suggestion.file_path, 
                suggestion.details.get("class_name", ""),
                suggestion.line_range[0],
                suggestion.line_range[1]
            )
            
            if result.get("success", False):
                return True, "Factory Pattern refactoring applied successfully"
            else:
                return False, result.get("message", "Failed to apply Factory Pattern refactoring")
        
        except ImportError:
            return False, "PatternTransformer not available"
        except Exception as e:
            return False, f"Error applying Factory Pattern refactoring: {str(e)}"
    
    def _apply_transformed_code(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Apply the transformed code from the suggestion.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create backup
            backup_path = self.backup_file(suggestion.file_path)
            
            # Read the file
            with open(suggestion.file_path, 'r') as f:
                file_content = f.read()
            
            # Extract the code to replace
            start_line, end_line = suggestion.line_range
            lines = file_content.split('\n')
            before_code = '\n'.join(lines[start_line-1:end_line])
            
            if before_code.strip() != suggestion.before_code.strip():
                self.logger.warning("Source code has changed since the suggestion was generated")
            
            # Replace the code
            new_content = file_content.replace(before_code, suggestion.after_code)
            
            # Write the transformed code
            with open(suggestion.file_path, 'w') as f:
                f.write(new_content)
            
            # Validate syntax
            try:
                with open(suggestion.file_path, 'r') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                self.restore_backup(backup_path)
                return False, f"Syntax error in transformed code: {str(e)}"
            
            # Remove backup if successful
            os.remove(backup_path)
            
            return True, "Factory Pattern refactoring applied successfully"
        
        except Exception as e:
            # Restore backup if exists
            if 'backup_path' in locals():
                self.restore_backup(backup_path)
            
            return False, f"Error applying Factory Pattern refactoring: {str(e)}"


class StrategyPatternTransformer(CodeTransformer):
    """Transformer for Strategy Pattern refactoring."""
    
    def transform(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Apply Strategy Pattern refactoring.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        if suggestion.refactoring_type != RefactoringType.APPLY_STRATEGY_PATTERN:
            return False, f"Expected STRATEGY suggestion, got {suggestion.refactoring_type.value}"
        
        if not self._validate_file(suggestion.file_path):
            return False, f"File {suggestion.file_path} does not exist or is not readable/writable"
        
        try:
            from src.pattern_transformer import PatternTransformer
            
            # Create a pattern transformer
            transformer = PatternTransformer()
            
            # Generate the strategy pattern
            result = transformer.apply_strategy_pattern(
                suggestion.file_path, 
                suggestion.details.get("method_name", ""),
                suggestion.line_range[0],
                suggestion.line_range[1]
            )
            
            if result.get("success", False):
                return True, "Strategy Pattern refactoring applied successfully"
            else:
                return False, result.get("message", "Failed to apply Strategy Pattern refactoring")
        
        except ImportError:
            return False, "PatternTransformer not available"
        except Exception as e:
            return False, f"Error applying Strategy Pattern refactoring: {str(e)}"


class ObserverPatternTransformer(CodeTransformer):
    """Transformer for Observer Pattern refactoring."""
    
    def transform(self, suggestion: RefactoringSuggestion) -> Tuple[bool, str]:
        """Apply Observer Pattern refactoring.
        
        Args:
            suggestion: The refactoring suggestion to apply
            
        Returns:
            Tuple of (success, message)
        """
        if suggestion.refactoring_type != RefactoringType.APPLY_OBSERVER_PATTERN:
            return False, f"Expected OBSERVER suggestion, got {suggestion.refactoring_type.value}"
        
        if not self._validate_file(suggestion.file_path):
            return False, f"File {suggestion.file_path} does not exist or is not readable/writable"
        
        try:
            from src.pattern_transformer import PatternTransformer
            
            # Create a pattern transformer
            transformer = PatternTransformer()
            
            # Generate the observer pattern
            result = transformer.apply_observer_pattern(
                suggestion.file_path, 
                suggestion.details.get("subject_name", ""),
                suggestion.line_range[0],
                suggestion.line_range[1]
            )
            
            if result.get("success", False):
                return True, "Observer Pattern refactoring applied successfully"
            else:
                return False, result.get("message", "Failed to apply Observer Pattern refactoring")
        
        except ImportError:
            return False, "PatternTransformer not available"
        except Exception as e:
            return False, f"Error applying Observer Pattern refactoring: {str(e)}"


class TransformerFactory:
    """Factory for creating code transformers based on refactoring type."""
    
    @staticmethod
    def create_transformer(refactoring_type: RefactoringType) -> CodeTransformer:
        """Create a transformer for the given refactoring type.
        
        Args:
            refactoring_type: The type of refactoring
            
        Returns:
            A CodeTransformer instance
            
        Raises:
            ValueError: If no transformer is available for the given refactoring type
        """
        if refactoring_type == RefactoringType.EXTRACT_METHOD:
            return ExtractMethodTransformer()
        elif refactoring_type == RefactoringType.APPLY_FACTORY_PATTERN:
            return FactoryPatternTransformer()
        elif refactoring_type == RefactoringType.APPLY_STRATEGY_PATTERN:
            return StrategyPatternTransformer()
        elif refactoring_type == RefactoringType.APPLY_OBSERVER_PATTERN:
            return ObserverPatternTransformer()
        else:
            raise ValueError(f"No transformer available for refactoring type {refactoring_type.value}")


class BatchTransformer:
    """Applies multiple refactoring suggestions in a batch."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def apply_suggestions(self, suggestions: List[RefactoringSuggestion]) -> Dict[str, List[Dict[str, Any]]]:
        """Apply multiple refactoring suggestions.
        
        Args:
            suggestions: List of refactoring suggestions to apply
            
        Returns:
            Dictionary with keys "success" and "failure", each containing lists of 
            dictionaries with "suggestion" and "message" keys
        """
        results = {
            "success": [],
            "failure": []
        }
        
        # Group suggestions by file to minimize the number of file operations
        files_to_suggestions = {}
        for suggestion in suggestions:
            if suggestion.file_path not in files_to_suggestions:
                files_to_suggestions[suggestion.file_path] = []
            files_to_suggestions[suggestion.file_path].append(suggestion)
        
        # Apply suggestions for each file
        for file_path, file_suggestions in files_to_suggestions.items():
            # Sort suggestions by line number in descending order to avoid offset issues
            file_suggestions.sort(key=lambda s: s.line_range[0], reverse=True)
            
            for suggestion in file_suggestions:
                try:
                    # Get the appropriate transformer
                    transformer = TransformerFactory.create_transformer(suggestion.refactoring_type)
                    
                    # Apply the transformation
                    success, message = transformer.transform(suggestion)
                    
                    if success:
                        results["success"].append({
                            "suggestion": suggestion.to_dict(),
                            "message": message
                        })
                    else:
                        results["failure"].append({
                            "suggestion": suggestion.to_dict(),
                            "message": message
                        })
                
                except ValueError as e:
                    results["failure"].append({
                        "suggestion": suggestion.to_dict(),
                        "message": str(e)
                    })
                except Exception as e:
                    self.logger.exception(f"Error applying suggestion for {file_path}")
                    results["failure"].append({
                        "suggestion": suggestion.to_dict(),
                        "message": f"Unexpected error: {str(e)}"
                    })
        
        return results