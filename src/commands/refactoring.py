"""
Command module for refactoring suggestions in the Code Pattern Analyzer.

This module provides commands for generating refactoring suggestions
based on pattern detection, flow analysis, complexity metrics, and architectural analysis.
"""

import click
import os
import logging
from typing import List

from src.refactoring.refactoring_suggestion import (
    CompositeSuggestionGenerator,
    PatternBasedSuggestionGenerator,
    ComplexityBasedSuggestionGenerator,
    FlowAnalysisSuggestionGenerator,
    ArchitecturalSuggestionGenerator,
    RefactoringSuggestion,
    generate_refactoring_report
)

@click.group()
def refactoring():
    """Commands for refactoring suggestion and pattern transformation."""
    pass

@refactoring.command()
@click.argument('target', type=click.Path(exists=True))
@click.option('--output', '-o', default='refactoring_suggestions.html',
              help='Output file for the report')
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'text']),
              default='html', help='Output format')
@click.option('--analysis-type', '-a', 
              type=click.Choice(['all', 'pattern', 'complexity', 'flow', 'architectural']),
              default='all', help='Type of analysis to perform')
@click.option('--min-impact', type=click.Choice(['low', 'medium', 'high', 'critical']),
              default='low', help='Minimum impact level to include')
def suggest(target, output, format, analysis_type, min_impact):
    """Generate refactoring suggestions for a file or directory."""
    logging.info(f"Analyzing {target} for refactoring suggestions")
    
    # Create appropriate generator based on analysis type
    if analysis_type == 'all':
        generator = CompositeSuggestionGenerator()
    elif analysis_type == 'pattern':
        generator = PatternBasedSuggestionGenerator()
    elif analysis_type == 'complexity':
        generator = ComplexityBasedSuggestionGenerator()
    elif analysis_type == 'flow':
        generator = FlowAnalysisSuggestionGenerator()
    elif analysis_type == 'architectural':
        generator = ArchitecturalSuggestionGenerator()
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    # Generate suggestions
    if analysis_type == 'all':
        suggestions = generator.generate_all_suggestions(target)
    else:
        suggestions = generator.generate_suggestions(target)
    
    # Filter by impact
    impact_levels = ['low', 'medium', 'high', 'critical']
    min_impact_index = impact_levels.index(min_impact)
    filtered_suggestions = [
        s for s in suggestions 
        if impact_levels.index(s.impact.value) >= min_impact_index
    ]
    
    # Generate report
    if filtered_suggestions:
        generate_refactoring_report(filtered_suggestions, output, format)
        
        # Output summary
        click.echo(f"Generated {len(filtered_suggestions)} refactoring suggestions")
        click.echo(f"Report saved to: {os.path.abspath(output)}")
    else:
        click.echo("No refactoring suggestions generated that meet the criteria.")

@refactoring.command()
@click.argument('target', type=click.Path(exists=True))
@click.option('--suggested-only/--all-files', default=True,
              help='Only analyze files with refactoring suggestions')
@click.option('--interactive/--view-only', default=False,
              help='Enable interactive mode to apply refactorings')
def analyze(target, suggested_only, interactive):
    """Interactive analysis of files for refactoring opportunities."""
    # Generate suggestions
    generator = CompositeSuggestionGenerator()
    suggestions = generator.generate_all_suggestions(target)
    
    if not suggestions:
        click.echo("No refactoring suggestions found.")
        return
    
    # Get unique files
    files_with_suggestions = sorted({s.file_path for s in suggestions})
    
    if suggested_only:
        files_to_analyze = files_with_suggestions
    else:
        # TODO: Get all files in target if not suggested_only
        files_to_analyze = files_with_suggestions
    
    click.echo(f"Found {len(suggestions)} refactoring suggestions in {len(files_with_suggestions)} files.")
    
    if interactive:
        selected_suggestions = []
        click.echo("\nSelect suggestions to apply:")
    
    # Interactive file selection
    for i, file_path in enumerate(files_to_analyze):
        # Get suggestions for this file
        file_suggestions = [s for s in suggestions if s.file_path == file_path]
        
        click.echo(f"\n{i+1}. {file_path} ({len(file_suggestions)} suggestions)")
        
        # Group by impact for summary
        impact_counts = {}
        for s in file_suggestions:
            impact = s.impact.value
            if impact not in impact_counts:
                impact_counts[impact] = 0
            impact_counts[impact] += 1
        
        # Show impact summary
        for impact, count in impact_counts.items():
            click.echo(f"   - {impact.upper()}: {count}")
        
        # Ask if user wants to see suggestions for this file
        if click.confirm("   View suggestions for this file?", default=False):
            for j, suggestion in enumerate(file_suggestions):
                click.echo(f"\n   [{j+1}/{len(file_suggestions)}] {suggestion.refactoring_type.value}")
                click.echo(f"   Impact: {suggestion.impact.value.upper()}")
                click.echo(f"   Lines: {suggestion.line_range[0]}-{suggestion.line_range[1]}")
                click.echo(f"   Description: {suggestion.description}")
                
                if suggestion.benefits:
                    click.echo(f"   Benefits:")
                    for benefit in suggestion.benefits:
                        click.echo(f"     - {benefit}")
                
                # If before/after code is available, show a preview
                if suggestion.before_code and suggestion.after_code:
                    show_code = click.confirm("   Show code preview?", default=False)
                    if show_code:
                        click.echo("\n   Current code:")
                        click.echo(f"   ```\n{suggestion.before_code}\n   ```")
                        click.echo("\n   Suggested code:")
                        click.echo(f"   ```\n{suggestion.after_code}\n   ```")
                
                # In interactive mode, ask if user wants to apply this suggestion
                if interactive:
                    apply = click.confirm("   Apply this suggestion?", default=False)
                    if apply:
                        selected_suggestions.append(suggestion)
                
                # Continue to next suggestion or file
                if j < len(file_suggestions) - 1:
                    if not click.confirm("   Next suggestion?", default=True):
                        break
        
        # Check if user wants to continue to the next file
        if i < len(files_to_analyze) - 1:
            if not click.confirm("Continue to next file?", default=True):
                break
    
    # In interactive mode, apply selected suggestions
    if interactive and selected_suggestions:
        from src.refactoring.interactive_refactoring import InteractiveRefactoringSession
        
        click.echo(f"\nStarting interactive refactoring session with {len(selected_suggestions)} suggestions.")
        session = InteractiveRefactoringSession(selected_suggestions)
        results = session.start()
        
        click.echo(f"\nRefactoring session complete: {len(results['applied'])} applied, {len(results['skipped'])} skipped.")
    
    click.echo("\nAnalysis complete.")


@refactoring.command()
@click.argument('target', type=click.Path(exists=True))
@click.option('--interactive/--batch', default=True,
              help='Use interactive mode or batch mode')
def interactive(target, interactive):
    """Start an interactive refactoring session."""
    from src.refactoring.interactive_refactoring import InteractiveRefactoringSession, InteractiveCodeEditor
    
    # Generate suggestions
    click.echo(f"Analyzing {target} for refactoring opportunities...")
    generator = CompositeSuggestionGenerator()
    all_suggestions = generator.generate_all_suggestions(target)
    
    if not all_suggestions:
        click.echo("No refactoring suggestions found.")
        return
    
    click.echo(f"Found {len(all_suggestions)} refactoring suggestions.")
    
    # Group by impact for summary
    impact_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for s in all_suggestions:
        impact_counts[s.impact.value] += 1
    
    # Show impact summary
    click.echo("\nImpact summary:")
    for impact, count in impact_counts.items():
        if count > 0:
            click.echo(f"- {impact.upper()}: {count}")
    
    # Filter suggestions by impact if requested
    min_impact = click.prompt(
        "\nMinimum impact level to include",
        type=click.Choice(['low', 'medium', 'high', 'critical']),
        default='medium'
    )
    
    impact_levels = ['low', 'medium', 'high', 'critical']
    min_impact_index = impact_levels.index(min_impact)
    filtered_suggestions = [
        s for s in all_suggestions 
        if impact_levels.index(s.impact.value) >= min_impact_index
    ]
    
    if not filtered_suggestions:
        click.echo(f"No suggestions meet the minimum impact level of {min_impact}.")
        return
    
    click.echo(f"\n{len(filtered_suggestions)} suggestions meet the minimum impact level.")
    
    # Start the interactive session
    if interactive:
        session = InteractiveRefactoringSession(filtered_suggestions)
        results = session.start()
        
        click.echo(f"\nRefactoring session complete: {len(results['applied'])} applied, {len(results['skipped'])} skipped.")
    else:
        # Batch mode - apply all suggestions without interaction
        from src.refactoring.code_transformer import BatchTransformer
        
        click.echo(f"\nApplying {len(filtered_suggestions)} refactoring suggestions in batch mode...")
        transformer = BatchTransformer()
        results = transformer.apply_suggestions(filtered_suggestions)
        
        success_count = len(results["success"])
        failure_count = len(results["failure"])
        
        click.echo(f"\nBatch transformation complete: {success_count} succeeded, {failure_count} failed.")
        
        if failure_count > 0:
            click.echo("\nFailed transformations:")
            for failure in results["failure"]:
                suggestion = failure["suggestion"]
                click.echo(f"- {suggestion['description']}: {failure['message']}")

@refactoring.command()
@click.argument('target', type=click.Path(exists=True))
@click.option('--pattern', '-p', 
              type=click.Choice(['factory', 'strategy', 'observer', 'decorator', 'composite']),
              required=True, help='Design pattern to apply')
@click.option('--dry-run/--apply', default=True, 
              help='Dry run (preview changes) or apply changes')
def transform(target, pattern, dry_run):
    """Transform code to implement a specific design pattern."""
    from src.refactoring.refactoring_suggestion import (
        PatternBasedSuggestionGenerator,
        RefactoringType,
        RefactoringSuggestion
    )
    from src.refactoring.code_transformer import (
        TransformerFactory,
        BatchTransformer
    )
    
    click.echo(f"Analyzing {target} for {pattern} pattern opportunities...")
    
    # Generate suggestions for the pattern
    generator = PatternBasedSuggestionGenerator()
    all_suggestions = generator.generate_suggestions(target)
    
    # Filter for the requested pattern
    pattern_map = {
        'factory': RefactoringType.APPLY_FACTORY_PATTERN,
        'strategy': RefactoringType.APPLY_STRATEGY_PATTERN,
        'observer': RefactoringType.APPLY_OBSERVER_PATTERN,
        'decorator': RefactoringType.APPLY_DECORATOR_PATTERN,
        'composite': RefactoringType.APPLY_COMPOSITE_PATTERN
    }
    
    target_type = pattern_map.get(pattern)
    if target_type is None:
        click.echo(f"Pattern {pattern} is not currently supported for transformation.")
        return
    
    matching_suggestions = [s for s in all_suggestions if s.refactoring_type == target_type]
    
    if not matching_suggestions:
        click.echo(f"No {pattern} pattern opportunities found in {target}.")
        return
    
    click.echo(f"Found {len(matching_suggestions)} {pattern} pattern opportunities:")
    
    # Display the opportunities
    for i, suggestion in enumerate(matching_suggestions):
        click.echo(f"\n{i+1}. {suggestion.description}")
        click.echo(f"   File: {suggestion.file_path}")
        click.echo(f"   Lines: {suggestion.line_range[0]}-{suggestion.line_range[1]}")
        click.echo(f"   Impact: {suggestion.impact.value.upper()}")
        
        if suggestion.benefits:
            click.echo("   Benefits:")
            for benefit in suggestion.benefits:
                click.echo(f"     - {benefit}")
        
        # Show code preview if available
        if suggestion.before_code:
            click.echo("\n   Current code:")
            click.echo(f"   ```\n{suggestion.before_code}\n   ```")
    
    # Ask which opportunities to apply
    indices = []
    if not dry_run:
        choices = click.prompt(
            "\nEnter the numbers of the opportunities to transform (comma-separated) or 'all'",
            default="", show_default=False
        )
        
        if choices.lower() == 'all':
            indices = list(range(len(matching_suggestions)))
        elif choices.strip():
            try:
                # Parse comma-separated indices
                indices = [int(idx.strip()) - 1 for idx in choices.split(',')]
                # Validate indices
                indices = [idx for idx in indices if 0 <= idx < len(matching_suggestions)]
            except ValueError:
                click.echo("Invalid input. No transformations will be applied.")
                return
    
    if dry_run:
        click.echo("\nDry run completed. Use --apply to apply transformations.")
        return
    
    if not indices:
        click.echo("No transformations selected.")
        return
    
    # Apply the selected transformations
    selected_suggestions = [matching_suggestions[idx] for idx in indices]
    
    click.echo(f"\nApplying {len(selected_suggestions)} transformations...")
    
    # Use the batch transformer to apply the suggestions
    transformer = BatchTransformer()
    results = transformer.apply_suggestions(selected_suggestions)
    
    # Report the results
    success_count = len(results["success"])
    failure_count = len(results["failure"])
    
    click.echo(f"\nTransformation complete: {success_count} succeeded, {failure_count} failed")
    
    if failure_count > 0:
        click.echo("\nFailed transformations:")
        for failure in results["failure"]:
            suggestion = failure["suggestion"]
            click.echo(f"- {suggestion['description']}: {failure['message']}")

def register_commands(cli):
    """Register all commands with the CLI."""
    cli.add_command(refactoring)