"""
Interactive refactoring module for the Code Pattern Analyzer.

This module provides an interactive interface for applying refactoring
suggestions, allowing users to review, modify and apply changes with
in-context help and guidance.
"""

import os
import sys
import tempfile
import difflib
import subprocess
from typing import List, Dict, Any, Tuple, Optional, Union

from src.refactoring.refactoring_suggestion import RefactoringSuggestion
from src.refactoring.code_transformer import CodeTransformer, TransformerFactory


class InteractiveRefactoringSession:
    """Interactive session for reviewing and applying refactorings."""
    
    def __init__(self, suggestions: List[RefactoringSuggestion]):
        self.suggestions = suggestions
        self.current_index = 0
        self.modified_suggestions = []
        self.applied_suggestions = []
        self.skipped_suggestions = []
    
    def start(self) -> Dict[str, Any]:
        """Start the interactive refactoring session.
        
        Returns:
            Dictionary containing session results
        """
        if not self.suggestions:
            print("No refactoring suggestions to review.")
            return {
                "applied": [],
                "skipped": [],
                "total": 0
            }
        
        print(f"\nStarting interactive refactoring session with {len(self.suggestions)} suggestions.")
        print("Commands: (a)pply, (s)kip, (e)dit, (d)iff, (q)uit, (h)elp")
        
        while self.current_index < len(self.suggestions):
            suggestion = self.suggestions[self.current_index]
            
            # Display the current suggestion
            self._display_suggestion(suggestion)
            
            # Get user command
            command = input("\nCommand (a/s/e/d/q/h): ").strip().lower()
            
            if command == 'a':
                self._apply_suggestion(suggestion)
            elif command == 's':
                self._skip_suggestion(suggestion)
            elif command == 'e':
                self._edit_suggestion(suggestion)
            elif command == 'd':
                self._show_diff(suggestion)
            elif command == 'q':
                print("\nExiting interactive session.")
                break
            elif command == 'h':
                self._show_help()
            else:
                print("Unknown command. Type 'h' for help.")
        
        # Summarize results
        self._show_summary()
        
        return {
            "applied": [s.to_dict() for s in self.applied_suggestions],
            "skipped": [s.to_dict() for s in self.skipped_suggestions],
            "total": len(self.suggestions)
        }
    
    def _display_suggestion(self, suggestion: RefactoringSuggestion) -> None:
        """Display a refactoring suggestion.
        
        Args:
            suggestion: The suggestion to display
        """
        print("\n" + "=" * 80)
        print(f"Suggestion {self.current_index + 1}/{len(self.suggestions)}")
        print("=" * 80)
        
        print(f"\nDescription: {suggestion.description}")
        print(f"Type: {suggestion.refactoring_type.value}")
        print(f"Impact: {suggestion.impact.value.upper()}")
        print(f"File: {suggestion.file_path}")
        print(f"Lines: {suggestion.line_range[0]}-{suggestion.line_range[1]}")
        
        if suggestion.benefits:
            print("\nBenefits:")
            for benefit in suggestion.benefits:
                print(f"- {benefit}")
        
        if suggestion.before_code and suggestion.after_code:
            print("\nCurrent Code:")
            print("-" * 40)
            print(suggestion.before_code)
            print("-" * 40)
            
            print("\nSuggested Code:")
            print("-" * 40)
            print(suggestion.after_code)
            print("-" * 40)
    
    def _apply_suggestion(self, suggestion: RefactoringSuggestion) -> None:
        """Apply a refactoring suggestion.
        
        Args:
            suggestion: The suggestion to apply
        """
        try:
            # Get the appropriate transformer
            transformer = TransformerFactory.create_transformer(suggestion.refactoring_type)
            
            # Apply the transformation
            success, message = transformer.transform(suggestion)
            
            if success:
                print(f"\nSuccess: {message}")
                self.applied_suggestions.append(suggestion)
            else:
                print(f"\nFailed: {message}")
                print("Skipping this suggestion.")
                self.skipped_suggestions.append(suggestion)
        
        except ValueError as e:
            print(f"\nError: {str(e)}")
            print("Skipping this suggestion.")
            self.skipped_suggestions.append(suggestion)
        
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            print("Skipping this suggestion.")
            self.skipped_suggestions.append(suggestion)
        
        self.current_index += 1
    
    def _skip_suggestion(self, suggestion: RefactoringSuggestion) -> None:
        """Skip a refactoring suggestion.
        
        Args:
            suggestion: The suggestion to skip
        """
        print("\nSkipping this suggestion.")
        self.skipped_suggestions.append(suggestion)
        self.current_index += 1
    
    def _edit_suggestion(self, suggestion: RefactoringSuggestion) -> None:
        """Edit a refactoring suggestion's code before applying.
        
        Args:
            suggestion: The suggestion to edit
        """
        if not suggestion.after_code:
            print("\nNo transformed code to edit.")
            return
        
        # Create a temporary file with the transformed code
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp_file:
            temp_file.write(suggestion.after_code)
            temp_path = temp_file.name
        
        try:
            # Determine the editor to use
            editor = os.environ.get("EDITOR", "nano")
            
            # Open the editor
            print(f"\nOpening {editor} to edit the transformed code...")
            subprocess.call([editor, temp_path])
            
            # Read the edited code
            with open(temp_path, "r") as f:
                edited_code = f.read()
            
            # Update the suggestion with the edited code
            if edited_code != suggestion.after_code:
                suggestion = RefactoringSuggestion(
                    refactoring_type=suggestion.refactoring_type,
                    description=suggestion.description,
                    file_path=suggestion.file_path,
                    line_range=suggestion.line_range,
                    impact=suggestion.impact,
                    source=suggestion.source,
                    details=suggestion.details,
                    before_code=suggestion.before_code,
                    after_code=edited_code,
                    benefits=suggestion.benefits,
                    effort=suggestion.effort,
                    affected_components=suggestion.affected_components
                )
                
                self.suggestions[self.current_index] = suggestion
                self.modified_suggestions.append(suggestion)
                
                print("\nTransformed code updated.")
            else:
                print("\nNo changes made to the transformed code.")
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _show_diff(self, suggestion: RefactoringSuggestion) -> None:
        """Show a unified diff of the before and after code.
        
        Args:
            suggestion: The suggestion to show diff for
        """
        if not suggestion.before_code or not suggestion.after_code:
            print("\nNo code to diff.")
            return
        
        # Generate the diff
        before_lines = suggestion.before_code.splitlines()
        after_lines = suggestion.after_code.splitlines()
        
        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile="before",
            tofile="after",
            lineterm="",
            n=3
        )
        
        # Display the diff
        print("\nDiff:")
        print("-" * 40)
        for line in diff:
            if line.startswith("+"):
                print(f"\033[92m{line}\033[0m")  # Green for additions
            elif line.startswith("-"):
                print(f"\033[91m{line}\033[0m")  # Red for deletions
            elif line.startswith("@@"):
                print(f"\033[94m{line}\033[0m")  # Blue for line information
            else:
                print(line)
        print("-" * 40)
    
    def _show_help(self) -> None:
        """Show help information for the interactive session."""
        print("\nInteractive Refactoring Commands:")
        print("  a - Apply the current suggestion")
        print("  s - Skip the current suggestion")
        print("  e - Edit the transformed code before applying")
        print("  d - Show a unified diff of the before and after code")
        print("  q - Quit the interactive session")
        print("  h - Show this help message")
    
    def _show_summary(self) -> None:
        """Show a summary of the session results."""
        print("\n" + "=" * 80)
        print("Interactive Refactoring Session Summary")
        print("=" * 80)
        
        print(f"\nTotal suggestions: {len(self.suggestions)}")
        print(f"Applied: {len(self.applied_suggestions)}")
        print(f"Skipped: {len(self.skipped_suggestions)}")
        print(f"Modified before applying: {len(self.modified_suggestions)}")
        
        if self.applied_suggestions:
            print("\nApplied suggestions:")
            for i, suggestion in enumerate(self.applied_suggestions, 1):
                print(f"{i}. {suggestion.description} in {os.path.basename(suggestion.file_path)}")


class InteractiveCodeEditor:
    """Interactive editor for modifying code with refactoring guidance."""
    
    def __init__(self, file_path: str, suggestion: RefactoringSuggestion):
        self.file_path = file_path
        self.suggestion = suggestion
        self.original_content = None
        self.modified_content = None
    
    def edit(self) -> bool:
        """Open an interactive editing session with refactoring guidance.
        
        Returns:
            True if the file was modified, False otherwise
        """
        # Read the original file
        try:
            with open(self.file_path, "r") as f:
                self.original_content = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return False
        
        # Create a temporary file with the original content
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w+", delete=False) as temp_file:
            # Add a comment header with refactoring guidance
            header = f"""# REFACTORING GUIDANCE
# 
# Description: {self.suggestion.description}
# Type: {self.suggestion.refactoring_type.value}
# Lines: {self.suggestion.line_range[0]}-{self.suggestion.line_range[1]}
#
# Benefits:
"""
            for benefit in self.suggestion.benefits or []:
                header += f"# - {benefit}\n"
            
            header += "#\n# Make your changes below this line.\n# The original code follows:\n\n"
            
            temp_file.write(header + self.original_content)
            temp_path = temp_file.name
        
        try:
            # Determine the editor to use
            editor = os.environ.get("EDITOR", "nano")
            
            # Open the editor
            print(f"\nOpening {editor} to edit the file with refactoring guidance...")
            subprocess.call([editor, temp_path])
            
            # Read the edited content
            with open(temp_path, "r") as f:
                edited_content = f.read()
            
            # Remove the header
            header_end = edited_content.find("# The original code follows:")
            if header_end != -1:
                self.modified_content = edited_content[header_end + len("# The original code follows:") + 2:]
            else:
                self.modified_content = edited_content
            
            # Check if the content was modified
            if self.modified_content != self.original_content:
                # Write the modified content back to the original file
                with open(self.file_path, "w") as f:
                    f.write(self.modified_content)
                
                print("\nFile updated successfully.")
                return True
            else:
                print("\nNo changes made to the file.")
                return False
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return False