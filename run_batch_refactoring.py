#!/usr/bin/env python3
"""
Code Pattern Analyzer - Batch Refactoring Tool

This script applies multiple refactoring suggestions to a codebase in batch mode,
allowing for automated application of recommended changes.
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any

# Add project src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.refactoring.refactoring_suggestion import (
    CompositeSuggestionGenerator,
    RefactoringSuggestion,
    RefactoringType, 
    SuggestionImpact
)
from src.refactoring.code_transformer import BatchTransformer


def setup_logger() -> logging.Logger:
    """Set up and return a logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("batch_refactoring")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Apply multiple refactoring suggestions to a codebase in batch mode."
    )
    
    parser.add_argument(
        "target",
        help="File or directory to analyze and refactor"
    )
    
    parser.add_argument(
        "--suggestions-file", "-f",
        help="JSON file containing refactoring suggestions (if not provided, suggestions will be generated)"
    )
    
    parser.add_argument(
        "--output-report", "-o",
        help="Path to save the transformation report",
        default="refactoring_results.json"
    )
    
    parser.add_argument(
        "--analysis-type", "-a",
        choices=["all", "pattern", "complexity", "flow", "architectural"],
        default="all",
        help="Type of analysis to perform when generating suggestions"
    )
    
    parser.add_argument(
        "--min-impact", "-i",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Minimum impact level to include when generating suggestions"
    )
    
    parser.add_argument(
        "--refactoring-type", "-t",
        help="Specific refactoring type to filter for (e.g., EXTRACT_METHOD, FACTORY_METHOD)"
    )
    
    parser.add_argument(
        "--confirm/--no-confirm",
        default=True,
        help="Whether to ask for confirmation before applying transformations"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be transformed, without making changes"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    return parser.parse_args()


def load_suggestions_from_file(file_path: str) -> List[RefactoringSuggestion]:
    """Load refactoring suggestions from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing suggestions
        
    Returns:
        List of RefactoringSuggestion objects
    """
    logger = logging.getLogger("batch_refactoring")
    
    try:
        with open(file_path, "r") as f:
            suggestions_data = json.load(f)
        
        suggestions = []
        for data in suggestions_data:
            try:
                # Parse refactoring type
                try:
                    refactoring_type = RefactoringType(data["refactoring_type"])
                except ValueError:
                    logger.warning(f"Unknown refactoring type: {data['refactoring_type']}")
                    continue
                
                # Parse impact
                try:
                    impact = SuggestionImpact(data["impact"])
                except ValueError:
                    logger.warning(f"Unknown impact level: {data['impact']}")
                    continue
                
                # Create suggestion
                suggestion = RefactoringSuggestion(
                    refactoring_type=refactoring_type,
                    description=data["description"],
                    file_path=data["file_path"],
                    line_range=tuple(data["line_range"]),
                    impact=impact,
                    source=data["source"],
                    details=data.get("details"),
                    before_code=data.get("before_code"),
                    after_code=data.get("after_code"),
                    benefits=data.get("benefits"),
                    effort=data.get("effort", 3),
                    affected_components=data.get("affected_components")
                )
                
                suggestions.append(suggestion)
            
            except KeyError as e:
                logger.warning(f"Missing required field in suggestion: {e}")
                continue
        
        return suggestions
    
    except Exception as e:
        logger.error(f"Error loading suggestions from file: {e}")
        return []


def generate_suggestions(
    target: str, 
    analysis_type: str = "all", 
    min_impact: str = "medium", 
    refactoring_type: str = None
) -> List[RefactoringSuggestion]:
    """Generate refactoring suggestions for the target.
    
    Args:
        target: File or directory to analyze
        analysis_type: Type of analysis to perform
        min_impact: Minimum impact level to include
        refactoring_type: Specific refactoring type to filter for
        
    Returns:
        List of RefactoringSuggestion objects
    """
    logger = logging.getLogger("batch_refactoring")
    
    logger.info(f"Analyzing {target} for refactoring opportunities...")
    
    # Create the appropriate generator
    if analysis_type == "all":
        generator = CompositeSuggestionGenerator()
        suggestions = generator.generate_all_suggestions(target)
    else:
        from src.refactoring.refactoring_suggestion import (
            PatternBasedSuggestionGenerator,
            ComplexityBasedSuggestionGenerator,
            FlowAnalysisSuggestionGenerator,
            ArchitecturalSuggestionGenerator
        )
        
        if analysis_type == "pattern":
            generator = PatternBasedSuggestionGenerator()
        elif analysis_type == "complexity":
            generator = ComplexityBasedSuggestionGenerator()
        elif analysis_type == "flow":
            generator = FlowAnalysisSuggestionGenerator()
        elif analysis_type == "architectural":
            generator = ArchitecturalSuggestionGenerator()
        else:
            logger.error(f"Unknown analysis type: {analysis_type}")
            return []
        
        suggestions = generator.generate_suggestions(target)
    
    logger.info(f"Generated {len(suggestions)} initial suggestions")
    
    # Filter by impact
    impact_levels = ["low", "medium", "high", "critical"]
    min_impact_index = impact_levels.index(min_impact)
    suggestions = [
        s for s in suggestions 
        if impact_levels.index(s.impact.value) >= min_impact_index
    ]
    
    logger.info(f"{len(suggestions)} suggestions meet the minimum impact level of {min_impact}")
    
    # Filter by refactoring type if specified
    if refactoring_type:
        try:
            target_type = RefactoringType(refactoring_type)
            suggestions = [s for s in suggestions if s.refactoring_type == target_type]
            logger.info(f"{len(suggestions)} suggestions match refactoring type {refactoring_type}")
        except ValueError:
            logger.warning(f"Unknown refactoring type: {refactoring_type}")
    
    return suggestions


def display_suggestions(suggestions: List[RefactoringSuggestion]) -> None:
    """Display refactoring suggestions in a readable format.
    
    Args:
        suggestions: List of RefactoringSuggestion objects
    """
    if not suggestions:
        print("No refactoring suggestions to display.")
        return
    
    print(f"\nFound {len(suggestions)} refactoring suggestions:")
    
    # Group by impact for summary
    impact_counts = {impact.value: 0 for impact in SuggestionImpact}
    for s in suggestions:
        impact_counts[s.impact.value] += 1
    
    # Print impact summary
    print("\nImpact summary:")
    for impact in ["critical", "high", "medium", "low"]:
        if impact_counts[impact] > 0:
            print(f"- {impact.upper()}: {impact_counts[impact]}")
    
    # Group by type for summary
    type_counts = {}
    for s in suggestions:
        type_name = s.refactoring_type.value
        if type_name not in type_counts:
            type_counts[type_name] = 0
        type_counts[type_name] += 1
    
    # Print type summary
    print("\nRefactoring type summary:")
    for type_name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"- {type_name}: {count}")
    
    # Group by file for summary
    file_counts = {}
    for s in suggestions:
        if s.file_path not in file_counts:
            file_counts[s.file_path] = 0
        file_counts[s.file_path] += 1
    
    # Print file summary
    print(f"\nAffected files: {len(file_counts)}")
    
    # Ask if user wants to see detailed suggestions
    show_details = input("\nShow detailed suggestions? (y/n) ").lower().startswith('y')
    
    if show_details:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.description}")
            print(f"   Type: {suggestion.refactoring_type.value}")
            print(f"   Impact: {suggestion.impact.value.upper()}")
            print(f"   File: {suggestion.file_path}")
            print(f"   Lines: {suggestion.line_range[0]}-{suggestion.line_range[1]}")
            
            if suggestion.benefits:
                print("   Benefits:")
                for benefit in suggestion.benefits:
                    print(f"     - {benefit}")
            
            # Show code preview if available and requested
            if suggestion.before_code:
                show_code = input("   Show code preview? (y/n) ").lower().startswith('y')
                if show_code:
                    print("\n   Current code:")
                    print(f"   ```\n{suggestion.before_code}\n   ```")
                    
                    if suggestion.after_code:
                        print("\n   Transformed code:")
                        print(f"   ```\n{suggestion.after_code}\n   ```")
            
            # Check if user wants to continue to the next suggestion
            if i < len(suggestions):
                cont = input("\nShow next suggestion? (y/n) ").lower().startswith('y')
                if not cont:
                    break


def save_transformation_report(results: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Save the transformation results to a JSON file.
    
    Args:
        results: Dictionary containing transformation results
        output_path: Path to save the report
    """
    try:
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Transformation report saved to {output_path}")
    
    except Exception as e:
        print(f"Error saving transformation report: {e}")


def main() -> None:
    """Main entry point."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    logger = setup_logger()
    
    # Load or generate suggestions
    if args.suggestions_file:
        logger.info(f"Loading suggestions from {args.suggestions_file}")
        suggestions = load_suggestions_from_file(args.suggestions_file)
    else:
        suggestions = generate_suggestions(
            args.target,
            args.analysis_type,
            args.min_impact,
            args.refactoring_type
        )
    
    # Display suggestions
    display_suggestions(suggestions)
    
    if not suggestions:
        logger.info("No refactoring suggestions to apply.")
        return
    
    # Check if this is a dry run
    if args.dry_run:
        logger.info("Dry run completed. No transformations applied.")
        return
    
    # Ask for confirmation if required
    if args.confirm:
        confirm = input("\nApply these transformations? (yes/no) ")
        if not confirm.lower() == "yes":
            logger.info("Transformations cancelled.")
            return
    
    # Apply the transformations
    logger.info(f"Applying {len(suggestions)} transformations...")
    
    transformer = BatchTransformer()
    results = transformer.apply_suggestions(suggestions)
    
    # Report the results
    success_count = len(results["success"])
    failure_count = len(results["failure"])
    
    logger.info(f"Transformation complete: {success_count} succeeded, {failure_count} failed")
    
    if failure_count > 0:
        logger.warning("Failed transformations:")
        for failure in results["failure"]:
            suggestion = failure["suggestion"]
            logger.warning(f"- {suggestion['description']}: {failure['message']}")
    
    # Save the transformation report
    save_transformation_report(results, args.output_report)


if __name__ == "__main__":
    main()