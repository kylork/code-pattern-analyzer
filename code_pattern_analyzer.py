#!/usr/bin/env python3
"""
Code Pattern Analyzer - Main Entry Point

This is the unified entry point for the Code Pattern Analyzer tool, integrating
all components including pattern detection, flow analysis, complexity metrics,
and refactoring suggestions.
"""

import os
import sys
import argparse
import logging
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cli import main as cli_main
from src.analyzer import CodeAnalyzer
from src.flow.control_flow import ControlFlowAnalyzer
from src.flow.data_flow import DataFlowAnalyzer
from src.metrics.complexity.complexity_analyzer import ComplexityAnalyzer
from src.refactoring.refactoring_suggestion import (
    CompositeSuggestionGenerator,
    RefactoringSuggestion,
    generate_refactoring_report
)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up and return a logger.
    
    Args:
        log_level: Logging level to use
        
    Returns:
        Configured logger
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("code-pattern-analyzer")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Code Pattern Analyzer - A powerful tool for analyzing and identifying patterns in source code."
    )
    
    # Main command argument
    parser.add_argument(
        "command", 
        choices=["analyze", "gui", "tutorial", "examples", "dashboard", "help"],
        help="Command to execute"
    )
    
    # Target path
    parser.add_argument(
        "target", 
        nargs="?",
        help="Path to the file or directory to analyze"
    )
    
    # Options for all commands
    parser.add_argument(
        "--output", "-o",
        help="Output file or directory for the results"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["html", "json", "text", "markdown"],
        default="html",
        help="Output format"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    # Analysis types to include
    parser.add_argument(
        "--include", "-i",
        choices=["all", "patterns", "flow", "complexity", "refactoring", "architecture"],
        default="all",
        help="Analysis types to include"
    )
    
    # GUI options
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to run the GUI server on (for GUI command)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the GUI server on (for GUI command)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open a browser window (for GUI command)"
    )
    
    return parser.parse_args()


def run_integrated_analysis(
    target: str,
    include: str = "all",
    output: Optional[str] = None,
    format_type: str = "html"
) -> Dict[str, Any]:
    """Run an integrated analysis of the target.
    
    Args:
        target: Path to the file or directory to analyze
        include: Analysis types to include ("all" or specific types)
        output: Output file for the report
        format_type: Format of the report
        
    Returns:
        Dictionary containing all analysis results
    """
    logger = logging.getLogger("code-pattern-analyzer")
    logger.info(f"Running integrated analysis on {target}")
    
    results = {
        "target": target,
        "analysis_types": include,
        "timestamp": None  # Will be set in the results
    }
    
    try:
        # Check if target exists
        if not os.path.exists(target):
            logger.error(f"Target does not exist: {target}")
            return {"error": f"Target does not exist: {target}"}
        
        # Initialize analyzers
        code_analyzer = CodeAnalyzer(use_mock=False)
        
        # Determine which analyses to run
        run_patterns = include in ["all", "patterns"]
        run_flow = include in ["all", "flow"]
        run_complexity = include in ["all", "complexity"]
        run_refactoring = include in ["all", "refactoring"]
        run_architecture = include in ["all", "architecture"]
        
        # Run pattern analysis
        if run_patterns:
            logger.info("Running pattern analysis...")
            pattern_results = code_analyzer.analyze_directory(target)
            results["patterns"] = pattern_results
        
        # Run flow analysis
        if run_flow:
            logger.info("Running flow analysis...")
            
            # Control flow analysis
            cfg_analyzer = ControlFlowAnalyzer()
            cfg_results = cfg_analyzer.analyze(target)
            results["control_flow"] = cfg_results
            
            # Data flow analysis
            df_analyzer = DataFlowAnalyzer()
            df_results = df_analyzer.analyze(target)
            results["data_flow"] = df_results
        
        # Run complexity analysis
        if run_complexity:
            logger.info("Running complexity analysis...")
            complexity_analyzer = ComplexityAnalyzer()
            complexity_results = complexity_analyzer.analyze(target)
            results["complexity"] = complexity_results
        
        # Run refactoring suggestions
        if run_refactoring:
            logger.info("Generating refactoring suggestions...")
            refactoring_generator = CompositeSuggestionGenerator()
            refactoring_suggestions = refactoring_generator.generate_all_suggestions(target)
            results["refactoring_suggestions"] = [s.to_dict() for s in refactoring_suggestions]
            
            # Generate refactoring report if output is specified
            if output and refactoring_suggestions:
                if run_patterns and run_flow and run_complexity:
                    # Only generate a separate refactoring report if we're running all analyses
                    refactoring_output = f"{os.path.splitext(output)[0]}_refactoring.{format_type}"
                else:
                    refactoring_output = output
                
                generate_refactoring_report(refactoring_suggestions, refactoring_output, format_type)
                logger.info(f"Refactoring report generated at {refactoring_output}")
        
        # Run architecture analysis
        if run_architecture:
            logger.info("Running architecture analysis...")
            arch_results = code_analyzer.analyze_architecture(target)
            results["architecture"] = arch_results
        
        # Generate integrated report if output is specified
        if output:
            logger.info(f"Generating integrated report at {output}")
            # Call report generator based on format
            if format_type == "html":
                generate_html_report(results, output)
            elif format_type == "json":
                generate_json_report(results, output)
            elif format_type == "text":
                generate_text_report(results, output)
            elif format_type == "markdown":
                generate_markdown_report(results, output)
        
        return results
    
    except Exception as e:
        logger.exception(f"Error running integrated analysis: {e}")
        return {"error": str(e)}


def generate_html_report(results: Dict[str, Any], output_path: str) -> None:
    """Generate an HTML report for the integrated analysis results.
    
    Args:
        results: The analysis results
        output_path: Path to save the report
    """
    # Import here to avoid circular imports
    from src.visualization import generate_integrated_html_report
    
    try:
        generate_integrated_html_report(results, output_path)
    except Exception as e:
        logging.exception(f"Error generating HTML report: {e}")
        # Fallback to JSON if HTML generation fails
        generate_json_report(results, output_path.replace(".html", ".json"))


def generate_json_report(results: Dict[str, Any], output_path: str) -> None:
    """Generate a JSON report for the integrated analysis results.
    
    Args:
        results: The analysis results
        output_path: Path to save the report
    """
    import json
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)


def generate_text_report(results: Dict[str, Any], output_path: str) -> None:
    """Generate a text report for the integrated analysis results.
    
    Args:
        results: The analysis results
        output_path: Path to save the report
    """
    with open(output_path, "w") as f:
        f.write("=== Code Pattern Analyzer Report ===\n\n")
        f.write(f"Target: {results['target']}\n")
        f.write(f"Analysis Types: {results['analysis_types']}\n\n")
        
        if "patterns" in results:
            f.write("=== Pattern Analysis ===\n")
            patterns = results["patterns"]
            f.write(f"Found {len(patterns)} pattern instances\n\n")
            for i, pattern in enumerate(patterns, 1):
                f.write(f"{i}. {pattern['pattern_name']} in {pattern['file_path']}\n")
                f.write(f"   Lines: {pattern['start_line']}-{pattern['end_line']}\n")
            f.write("\n")
        
        if "control_flow" in results:
            f.write("=== Control Flow Analysis ===\n")
            cf = results["control_flow"]
            if "dead_code" in cf:
                f.write(f"Dead Code Instances: {len(cf['dead_code'])}\n")
            if "infinite_loops" in cf:
                f.write(f"Potential Infinite Loops: {len(cf['infinite_loops'])}\n")
            f.write("\n")
        
        if "data_flow" in results:
            f.write("=== Data Flow Analysis ===\n")
            df = results["data_flow"]
            if "unused_variables" in df:
                f.write(f"Unused Variables: {len(df['unused_variables'])}\n")
            if "undefined_variables" in df:
                f.write(f"Potentially Undefined Variables: {len(df['undefined_variables'])}\n")
            f.write("\n")
        
        if "complexity" in results:
            f.write("=== Complexity Analysis ===\n")
            complexity = results["complexity"]
            if "cyclomatic_complexity" in complexity:
                cc = complexity["cyclomatic_complexity"]
                f.write(f"Files analyzed: {len(cc)}\n")
                high_complexity = sum(1 for file_data in cc.values() 
                                     for func_data in file_data.values() 
                                     if func_data.get("complexity", 0) > 10)
                f.write(f"Functions with high complexity (>10): {high_complexity}\n")
            f.write("\n")
        
        if "refactoring_suggestions" in results:
            f.write("=== Refactoring Suggestions ===\n")
            suggestions = results["refactoring_suggestions"]
            f.write(f"Total suggestions: {len(suggestions)}\n")
            
            # Count by impact
            impact_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for s in suggestions:
                impact = s["impact"]
                impact_counts[impact] += 1
            
            for impact, count in impact_counts.items():
                if count > 0:
                    f.write(f"{impact.upper()}: {count}\n")
            f.write("\n")
        
        if "architecture" in results:
            f.write("=== Architecture Analysis ===\n")
            arch = results["architecture"]
            if "styles" in arch:
                f.write("Detected Architectural Styles:\n")
                for style in arch["styles"]:
                    f.write(f"- {style['name']} ({style['confidence']}%)\n")
            if "anti_patterns" in arch:
                f.write("\nDetected Architectural Anti-patterns:\n")
                for anti in arch["anti_patterns"]:
                    f.write(f"- {anti['name']}\n")
            f.write("\n")


def generate_markdown_report(results: Dict[str, Any], output_path: str) -> None:
    """Generate a Markdown report for the integrated analysis results.
    
    Args:
        results: The analysis results
        output_path: Path to save the report
    """
    with open(output_path, "w") as f:
        f.write("# Code Pattern Analyzer Report\n\n")
        f.write(f"**Target:** {results['target']}\n")
        f.write(f"**Analysis Types:** {results['analysis_types']}\n\n")
        
        if "patterns" in results:
            f.write("## Pattern Analysis\n\n")
            patterns = results["patterns"]
            f.write(f"Found {len(patterns)} pattern instances\n\n")
            for i, pattern in enumerate(patterns, 1):
                f.write(f"### {i}. {pattern['pattern_name']}\n")
                f.write(f"- **File:** {pattern['file_path']}\n")
                f.write(f"- **Lines:** {pattern['start_line']}-{pattern['end_line']}\n\n")
        
        if "control_flow" in results:
            f.write("## Control Flow Analysis\n\n")
            cf = results["control_flow"]
            if "dead_code" in cf:
                f.write(f"**Dead Code Instances:** {len(cf['dead_code'])}\n\n")
                if cf['dead_code']:
                    f.write("| File | Function | Lines | Type |\n")
                    f.write("|------|----------|-------|------|\n")
                    for item in cf['dead_code']:
                        f.write(f"| {item['file_path']} | {item['function_name']} | {item['start_line']}-{item['end_line']} | {item['type']} |\n")
                    f.write("\n")
            
            if "infinite_loops" in cf:
                f.write(f"**Potential Infinite Loops:** {len(cf['infinite_loops'])}\n\n")
                if cf['infinite_loops']:
                    f.write("| File | Function | Lines |\n")
                    f.write("|------|----------|-------|\n")
                    for item in cf['infinite_loops']:
                        f.write(f"| {item['file_path']} | {item['function_name']} | {item['start_line']}-{item['end_line']} |\n")
                    f.write("\n")
        
        if "data_flow" in results:
            f.write("## Data Flow Analysis\n\n")
            df = results["data_flow"]
            if "unused_variables" in df:
                f.write(f"**Unused Variables:** {len(df['unused_variables'])}\n\n")
                if df['unused_variables']:
                    f.write("| File | Function | Variable | Line |\n")
                    f.write("|------|----------|----------|------|\n")
                    for item in df['unused_variables']:
                        f.write(f"| {item['file_path']} | {item['function_name']} | {item['variable_name']} | {item['line']} |\n")
                    f.write("\n")
            
            if "undefined_variables" in df:
                f.write(f"**Potentially Undefined Variables:** {len(df['undefined_variables'])}\n\n")
                if df['undefined_variables']:
                    f.write("| File | Function | Variable | Line |\n")
                    f.write("|------|----------|----------|------|\n")
                    for item in df['undefined_variables']:
                        f.write(f"| {item['file_path']} | {item['function_name']} | {item['variable_name']} | {item['line']} |\n")
                    f.write("\n")
        
        if "complexity" in results:
            f.write("## Complexity Analysis\n\n")
            complexity = results["complexity"]
            if "cyclomatic_complexity" in complexity:
                cc = complexity["cyclomatic_complexity"]
                f.write(f"**Files analyzed:** {len(cc)}\n\n")
                
                # Find functions with high complexity
                high_complexity_funcs = []
                for file_path, file_data in cc.items():
                    for func_name, func_data in file_data.items():
                        complexity_value = func_data.get("complexity", 0)
                        if complexity_value > 10:
                            high_complexity_funcs.append({
                                "file": file_path,
                                "function": func_name,
                                "complexity": complexity_value
                            })
                
                if high_complexity_funcs:
                    f.write("### Functions with High Complexity (>10)\n\n")
                    f.write("| File | Function | Complexity |\n")
                    f.write("|------|----------|------------|\n")
                    for func in sorted(high_complexity_funcs, key=lambda x: x["complexity"], reverse=True):
                        f.write(f"| {func['file']} | {func['function']} | {func['complexity']} |\n")
                    f.write("\n")
        
        if "refactoring_suggestions" in results:
            f.write("## Refactoring Suggestions\n\n")
            suggestions = results["refactoring_suggestions"]
            f.write(f"**Total suggestions:** {len(suggestions)}\n\n")
            
            # Count by impact
            impact_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for s in suggestions:
                impact = s["impact"]
                impact_counts[impact] += 1
            
            f.write("### Impact Summary\n\n")
            for impact, count in impact_counts.items():
                if count > 0:
                    f.write(f"- **{impact.upper()}:** {count}\n")
            f.write("\n")
            
            # Show high and critical suggestions
            high_priority = [s for s in suggestions if s["impact"] in ["critical", "high"]]
            if high_priority:
                f.write("### High Priority Suggestions\n\n")
                for i, s in enumerate(high_priority, 1):
                    f.write(f"#### {i}. {s['description']}\n")
                    f.write(f"- **Type:** {s['refactoring_type']}\n")
                    f.write(f"- **Impact:** {s['impact'].upper()}\n")
                    f.write(f"- **File:** {s['file_path']}\n")
                    f.write(f"- **Lines:** {s['line_range'][0]}-{s['line_range'][1]}\n")
                    
                    if s.get("benefits"):
                        f.write("\n**Benefits:**\n")
                        for benefit in s["benefits"]:
                            f.write(f"- {benefit}\n")
                    f.write("\n")
        
        if "architecture" in results:
            f.write("## Architecture Analysis\n\n")
            arch = results["architecture"]
            if "styles" in arch:
                f.write("### Detected Architectural Styles\n\n")
                for style in arch["styles"]:
                    f.write(f"- **{style['name']}** (Confidence: {style['confidence']}%)\n")
                f.write("\n")
            
            if "anti_patterns" in arch:
                f.write("### Detected Architectural Anti-patterns\n\n")
                for anti in arch["anti_patterns"]:
                    f.write(f"- **{anti['name']}**\n")
                    if "description" in anti:
                        f.write(f"  {anti['description']}\n")
                f.write("\n")


def start_gui(host: str = "localhost", port: int = 8080, open_browser: bool = True) -> None:
    """Start the Code Pattern Analyzer GUI.
    
    Args:
        host: Host to run the server on
        port: Port to run the server on
        open_browser: Whether to open a browser window
    """
    from src.web.app import create_app
    
    app = create_app()
    
    # Open browser
    if open_browser:
        url = f"http://{host}:{port}"
        webbrowser.open(url)
    
    # Start server
    app.run(host=host, port=port)


def show_tutorial() -> None:
    """Show a tutorial for the Code Pattern Analyzer."""
    print("=== Code Pattern Analyzer Tutorial ===\n")
    print("Welcome to the Code Pattern Analyzer tutorial!\n")
    
    print("The Code Pattern Analyzer is a powerful tool for analyzing and identifying patterns in source code.")
    print("It can help you understand existing codebases, identify refactoring opportunities, and enforce coding standards.\n")
    
    print("== Basic Usage ==\n")
    print("1. Run an integrated analysis:")
    print("   code_pattern_analyzer.py analyze /path/to/project -o report.html\n")
    
    print("2. Start the GUI:")
    print("   code_pattern_analyzer.py gui\n")
    
    print("3. Generate refactoring suggestions:")
    print("   code_pattern_analyzer.py analyze /path/to/project --include refactoring -o refactoring.html\n")
    
    print("4. See example analyses:")
    print("   code_pattern_analyzer.py examples\n")
    
    print("5. Start the dashboard:")
    print("   code_pattern_analyzer.py dashboard\n")
    
    print("For more information, run:")
    print("   code_pattern_analyzer.py help\n")


def show_examples() -> None:
    """Show examples for the Code Pattern Analyzer."""
    print("=== Code Pattern Analyzer Examples ===\n")
    
    examples = [
        {
            "title": "Basic Analysis",
            "description": "Run a basic analysis on a project",
            "command": "code_pattern_analyzer.py analyze /path/to/project -o report.html"
        },
        {
            "title": "Refactoring Analysis",
            "description": "Generate refactoring suggestions for a project",
            "command": "code_pattern_analyzer.py analyze /path/to/project --include refactoring -o refactoring.html"
        },
        {
            "title": "Flow Analysis",
            "description": "Run flow analysis to find dead code and undefined variables",
            "command": "code_pattern_analyzer.py analyze /path/to/project --include flow -o flow.html"
        },
        {
            "title": "Complexity Analysis",
            "description": "Analyze code complexity metrics",
            "command": "code_pattern_analyzer.py analyze /path/to/project --include complexity -o complexity.html"
        },
        {
            "title": "Generate JSON Output",
            "description": "Generate analysis results in JSON format",
            "command": "code_pattern_analyzer.py analyze /path/to/project -o results.json -f json"
        },
        {
            "title": "Start GUI",
            "description": "Start the GUI on a specific host and port",
            "command": "code_pattern_analyzer.py gui --host 0.0.0.0 --port 8888"
        },
        {
            "title": "Interactive Dashboard",
            "description": "Start the interactive dashboard",
            "command": "code_pattern_analyzer.py dashboard"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
        print(f"   {example['description']}")
        print(f"   $ {example['command']}")
        print()


def show_help() -> None:
    """Show help information for the Code Pattern Analyzer."""
    print("=== Code Pattern Analyzer Help ===\n")
    print("The Code Pattern Analyzer is a powerful tool for analyzing and identifying patterns in source code.\n")
    
    print("== Commands ==\n")
    print("1. analyze [target] - Run an integrated analysis on a file or directory")
    print("2. gui - Start the Code Pattern Analyzer GUI")
    print("3. tutorial - Show a tutorial for the Code Pattern Analyzer")
    print("4. examples - Show examples for the Code Pattern Analyzer")
    print("5. dashboard - Start the interactive dashboard")
    print("6. help - Show this help information\n")
    
    print("== Options ==\n")
    print("--output, -o [file] - Output file or directory for the results")
    print("--format, -f [format] - Output format (html, json, text, markdown)")
    print("--include, -i [type] - Analysis types to include (all, patterns, flow, complexity, refactoring, architecture)")
    print("--log-level [level] - Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    print("--host [host] - Host to run the GUI server on (for GUI command)")
    print("--port [port] - Port to run the GUI server on (for GUI command)")
    print("--no-browser - Don't automatically open a browser window (for GUI command)\n")
    
    print("For more information, run:")
    print("   code_pattern_analyzer.py tutorial\n")


def start_dashboard() -> None:
    """Start the Code Pattern Analyzer dashboard."""
    try:
        from src.web.dashboard import run_dashboard
        
        run_dashboard()
    except ImportError:
        print("Error: Dashboard module not found. Please install the required dependencies.")
        print("pip install dash plotly pandas")


def main() -> None:
    """Main entry point for the Code Pattern Analyzer."""
    args = parse_args()
    
    # Set up logging
    logger = setup_logging(args.log_level)
    
    # Execute the requested command
    if args.command == "analyze":
        if not args.target:
            logger.error("No target specified. Use -h for help.")
            return
        
        results = run_integrated_analysis(
            args.target,
            args.include,
            args.output,
            args.format
        )
        
        if "error" in results:
            logger.error(results["error"])
        elif not args.output:
            # If no output file specified, print a summary
            print("\n=== Analysis Summary ===\n")
            print(f"Target: {args.target}")
            print(f"Analysis Types: {args.include}")
            
            if "patterns" in results:
                print(f"Patterns: {len(results['patterns'])}")
            
            if "control_flow" in results:
                cf = results["control_flow"]
                print("Control Flow Issues:", end=" ")
                issues = []
                if "dead_code" in cf:
                    issues.append(f"{len(cf['dead_code'])} dead code")
                if "infinite_loops" in cf:
                    issues.append(f"{len(cf['infinite_loops'])} potential infinite loops")
                print(", ".join(issues) if issues else "None")
            
            if "data_flow" in results:
                df = results["data_flow"]
                print("Data Flow Issues:", end=" ")
                issues = []
                if "unused_variables" in df:
                    issues.append(f"{len(df['unused_variables'])} unused variables")
                if "undefined_variables" in df:
                    issues.append(f"{len(df['undefined_variables'])} undefined variables")
                print(", ".join(issues) if issues else "None")
            
            if "complexity" in results:
                complexity = results["complexity"]
                if "cyclomatic_complexity" in complexity:
                    cc = complexity["cyclomatic_complexity"]
                    high_complexity = sum(1 for file_data in cc.values() 
                                         for func_data in file_data.values() 
                                         if func_data.get("complexity", 0) > 10)
                    print(f"Functions with high complexity: {high_complexity}")
            
            if "refactoring_suggestions" in results:
                suggestions = results["refactoring_suggestions"]
                print(f"Refactoring Suggestions: {len(suggestions)}")
                
                # Count by impact
                impact_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
                for s in suggestions:
                    impact = s["impact"]
                    impact_counts[impact] += 1
                
                impacts = []
                for impact, count in impact_counts.items():
                    if count > 0:
                        impacts.append(f"{count} {impact}")
                print(f"  Impact levels: {', '.join(impacts)}")
            
            if "architecture" in results:
                arch = results["architecture"]
                if "styles" in arch:
                    styles = [f"{style['name']} ({style['confidence']}%)" for style in arch["styles"]]
                    print(f"Architectural Styles: {', '.join(styles)}")
                if "anti_patterns" in arch:
                    anti_patterns = [anti['name'] for anti in arch["anti_patterns"]]
                    print(f"Architectural Anti-patterns: {', '.join(anti_patterns)}")
    
    elif args.command == "gui":
        start_gui(args.host, args.port, not args.no_browser)
    
    elif args.command == "tutorial":
        show_tutorial()
    
    elif args.command == "examples":
        show_examples()
    
    elif args.command == "dashboard":
        start_dashboard()
    
    elif args.command == "help":
        show_help()


if __name__ == "__main__":
    main()