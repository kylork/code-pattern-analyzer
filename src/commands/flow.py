"""
Command-line interface for flow analysis.

This module provides CLI commands for running control flow and data flow analysis.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import click

from src.analyzer import CodeAnalyzer
from src.flow.control_flow import ControlFlowAnalyzer, ControlFlowGraph
from src.flow.data_flow import DataFlowAnalyzer, LiveVariableAnalyzer, AvailableExpressionAnalyzer

logger = logging.getLogger(__name__)

@click.group(name="flow")
def flow_command():
    """Commands for code flow analysis."""
    pass

@flow_command.command(name="control-flow")
@click.argument("path", type=click.Path(exists=True))
@click.option("--function", "-f", help="Analyze a specific function by name")
@click.option("--output", "-o", help="Output file for the report")
@click.option("--output-format", "-of", type=click.Choice(["json", "text", "html"]), default="html", 
              help="Output format (default: html)")
@click.option("--visualize/--no-visualize", default=True, help="Generate a visualization of the CFG")
@click.option("--viz-output", help="Output file for the visualization")
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
@click.pass_context
def control_flow_command(ctx, path, function, output, output_format, visualize, viz_output, debug):
    """Analyze control flow in source code.
    
    PATH can be a file or directory.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Set up default output paths
    if not output:
        if os.path.isfile(path):
            output_name = f"{Path(path).stem}_control_flow"
        else:
            output_name = f"{os.path.basename(os.path.abspath(path))}_control_flow"
        
        if output_format == "html":
            output = f"reports/{output_name}.html"
        elif output_format == "json":
            output = f"reports/{output_name}.json"
        else:
            output = f"reports/{output_name}.txt"
    
    if visualize and not viz_output:
        viz_output = f"reports/{Path(output).stem}_visualization.png"
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # Initialize analyzers
    analyzer = CodeAnalyzer()
    cf_analyzer = ControlFlowAnalyzer()
    
    # Analyze the code
    if os.path.isfile(path):
        # Analyze a single file
        file_result = analyzer.analyze_file(path)
        
        if "error" in file_result:
            click.echo(f"Error analyzing file: {file_result['error']}")
            return
        
        analysis_results = analyze_control_flow(
            file_result, cf_analyzer, function, visualize, viz_output
        )
    else:
        # Analyze a directory
        file_results = analyzer.analyze_directory(path)
        
        # Combine results from all files
        analysis_results = {
            "control_flow_graphs": {},
            "issues": {},
            "summary": {
                "total_files": len(file_results),
                "total_functions": 0,
                "total_issues": 0
            }
        }
        
        for file_result in file_results:
            if "error" in file_result:
                continue
                
            file_analysis = analyze_control_flow(
                file_result, cf_analyzer, function, visualize, viz_output
            )
            
            # Update combined results
            analysis_results["control_flow_graphs"].update(file_analysis["control_flow_graphs"])
            analysis_results["issues"].update(file_analysis["issues"])
            analysis_results["summary"]["total_functions"] += file_analysis["summary"]["total_functions"]
            analysis_results["summary"]["total_issues"] += file_analysis["summary"]["total_issues"]
    
    # Generate the report
    if output_format == "json":
        report = generate_json_report(analysis_results)
    elif output_format == "html":
        report = generate_html_report(analysis_results, path)
    else:
        report = generate_text_report(analysis_results, path)
    
    # Write the report
    with open(output, "w") as f:
        f.write(report)
    
    click.echo(f"Control flow analysis report written to {output}")
    if visualize and viz_output:
        click.echo(f"Control flow visualization written to {viz_output}")

@flow_command.command(name="data-flow")
@click.argument("path", type=click.Path(exists=True))
@click.option("--function", "-f", help="Analyze a specific function by name")
@click.option("--output", "-o", help="Output file for the report")
@click.option("--output-format", "-of", type=click.Choice(["json", "text", "html"]), default="html", 
              help="Output format (default: html)")
@click.option("--visualize/--no-visualize", default=True, help="Generate a visualization of the data flow")
@click.option("--viz-output", help="Output file for the visualization")
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
@click.pass_context
def data_flow_command(ctx, path, function, output, output_format, visualize, viz_output, debug):
    """Analyze data flow in source code.
    
    PATH can be a file or directory.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Set up default output paths
    if not output:
        if os.path.isfile(path):
            output_name = f"{Path(path).stem}_data_flow"
        else:
            output_name = f"{os.path.basename(os.path.abspath(path))}_data_flow"
        
        if output_format == "html":
            output = f"reports/{output_name}.html"
        elif output_format == "json":
            output = f"reports/{output_name}.json"
        else:
            output = f"reports/{output_name}.txt"
    
    if visualize and not viz_output:
        viz_output = f"reports/{Path(output).stem}_visualization.png"
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # Initialize analyzers
    analyzer = CodeAnalyzer()
    cf_analyzer = ControlFlowAnalyzer()
    df_analyzer = DataFlowAnalyzer()
    
    # Analyze the code
    if os.path.isfile(path):
        # Analyze a single file
        file_result = analyzer.analyze_file(path)
        
        if "error" in file_result:
            click.echo(f"Error analyzing file: {file_result['error']}")
            return
        
        analysis_results = analyze_data_flow(
            file_result, cf_analyzer, df_analyzer, function, visualize, viz_output
        )
    else:
        # Analyze a directory
        file_results = analyzer.analyze_directory(path)
        
        # Combine results from all files
        analysis_results = {
            "data_flow_results": {},
            "issues": {},
            "summary": {
                "total_files": len(file_results),
                "total_functions": 0,
                "total_variables": 0,
                "total_issues": 0
            }
        }
        
        for file_result in file_results:
            if "error" in file_result:
                continue
                
            file_analysis = analyze_data_flow(
                file_result, cf_analyzer, df_analyzer, function, visualize, viz_output
            )
            
            # Update combined results
            analysis_results["data_flow_results"].update(file_analysis["data_flow_results"])
            analysis_results["issues"].update(file_analysis["issues"])
            analysis_results["summary"]["total_functions"] += file_analysis["summary"]["total_functions"]
            analysis_results["summary"]["total_variables"] += file_analysis["summary"]["total_variables"]
            analysis_results["summary"]["total_issues"] += file_analysis["summary"]["total_issues"]
    
    # Generate the report
    if output_format == "json":
        report = generate_json_report(analysis_results)
    elif output_format == "html":
        report = generate_html_report_data_flow(analysis_results, path)
    else:
        report = generate_text_report_data_flow(analysis_results, path)
    
    # Write the report
    with open(output, "w") as f:
        f.write(report)
    
    click.echo(f"Data flow analysis report written to {output}")
    if visualize and viz_output:
        click.echo(f"Data flow visualization written to {viz_output}")

def analyze_control_flow(file_result, cf_analyzer, function_name, visualize, viz_output):
    """Analyze control flow for a file.
    
    Args:
        file_result: Result from CodeAnalyzer.analyze_file
        cf_analyzer: ControlFlowAnalyzer instance
        function_name: Optional name of function to analyze
        visualize: Whether to generate a visualization
        viz_output: Path for the visualization output
        
    Returns:
        Dictionary containing analysis results
    """
    tree = file_result["ast"]
    code = file_result["code"]
    language = file_result["language"]
    file_path = file_result["file"]
    
    # Check if the language is supported
    if not cf_analyzer.supports_language(language):
        return {
            "control_flow_graphs": {},
            "issues": {},
            "summary": {
                "total_functions": 0,
                "total_issues": 0,
                "error": f"Language {language} not supported for control flow analysis"
            }
        }
    
    # Generate control flow graphs
    cfgs = cf_analyzer.create_cfg_from_tree(tree, code, language, function_name)
    
    # If no CFGs were created, return early
    if not cfgs:
        return {
            "control_flow_graphs": {},
            "issues": {},
            "summary": {
                "total_functions": 0,
                "total_issues": 0,
                "error": "No functions found or unable to create control flow graphs"
            }
        }
    
    # Analyze each CFG
    analysis_results = {
        "control_flow_graphs": {},
        "issues": {},
        "summary": {
            "total_functions": len(cfgs),
            "total_issues": 0
        }
    }
    
    for func_name, cfg in cfgs.items():
        # Convert the CFG to a dictionary for the report
        analysis_results["control_flow_graphs"][func_name] = cfg.to_dict()
        
        # Find control flow issues
        dead_code = cf_analyzer.find_dead_code(cfg)
        infinite_loops = cf_analyzer.detect_possible_infinite_loops(cfg)
        
        # Analyze function complexity
        complexity = cf_analyzer.analyze_function_complexity(cfg)
        
        # Find exit paths
        exit_paths = cf_analyzer.get_function_exit_paths(cfg)
        
        # Store issues
        func_issues = {
            "dead_code": dead_code,
            "infinite_loops": infinite_loops,
            "complexity": complexity,
            "exit_paths": exit_paths
        }
        
        analysis_results["issues"][func_name] = func_issues
        
        # Update total issues count
        analysis_results["summary"]["total_issues"] += len(dead_code) + len(infinite_loops)
        
        # Generate visualization if requested
        if visualize and viz_output and (function_name is None or function_name == func_name):
            # If we're visualizing multiple functions, create separate files
            if len(cfgs) > 1 and function_name is None:
                viz_path = f"{os.path.splitext(viz_output)[0]}_{func_name}{os.path.splitext(viz_output)[1]}"
            else:
                viz_path = viz_output
                
            cfg.visualize(viz_path)
    
    return analysis_results

def analyze_data_flow(file_result, cf_analyzer, df_analyzer, function_name, visualize, viz_output):
    """Analyze data flow for a file.
    
    Args:
        file_result: Result from CodeAnalyzer.analyze_file
        cf_analyzer: ControlFlowAnalyzer instance
        df_analyzer: DataFlowAnalyzer instance
        function_name: Optional name of function to analyze
        visualize: Whether to generate a visualization
        viz_output: Path for the visualization output
        
    Returns:
        Dictionary containing analysis results
    """
    tree = file_result["ast"]
    code = file_result["code"]
    language = file_result["language"]
    file_path = file_result["file"]
    
    # Check if the language is supported
    if not df_analyzer.supports_language(language):
        return {
            "data_flow_results": {},
            "issues": {},
            "summary": {
                "total_functions": 0,
                "total_variables": 0,
                "total_issues": 0,
                "error": f"Language {language} not supported for data flow analysis"
            }
        }
    
    # Generate control flow graphs (needed for data flow analysis)
    cfgs = cf_analyzer.create_cfg_from_tree(tree, code, language, function_name)
    
    # If no CFGs were created, return early
    if not cfgs:
        return {
            "data_flow_results": {},
            "issues": {},
            "summary": {
                "total_functions": 0,
                "total_variables": 0,
                "total_issues": 0,
                "error": "No functions found or unable to create control flow graphs"
            }
        }
    
    # Analyze data flow for each CFG
    analysis_results = {
        "data_flow_results": {},
        "issues": {},
        "summary": {
            "total_functions": len(cfgs),
            "total_variables": 0,
            "total_issues": 0
        }
    }
    
    for func_name, cfg in cfgs.items():
        # Analyze data flow
        df_result = df_analyzer.analyze_data_flow(cfg, tree, code, language)
        
        # Store data flow results
        analysis_results["data_flow_results"][func_name] = df_result
        
        # Track issues
        if "issues" in df_result:
            issues = df_result["issues"]
            analysis_results["issues"][func_name] = issues
            
            # Count issues
            issue_count = sum(len(issue_list) for issue_list in issues.values())
            analysis_results["summary"]["total_issues"] += issue_count
        
        # Update variable count
        if "variables" in df_result:
            analysis_results["summary"]["total_variables"] += len(df_result["variables"])
        
        # Generate visualization if requested
        if visualize and viz_output and (function_name is None or function_name == func_name):
            # If we're visualizing multiple functions, create separate files
            if len(cfgs) > 1 and function_name is None:
                viz_path = f"{os.path.splitext(viz_output)[0]}_{func_name}{os.path.splitext(viz_output)[1]}"
            else:
                viz_path = viz_output
                
            df_analyzer.visualize_data_flow(cfg, df_result, viz_path)
    
    return analysis_results

def generate_json_report(analysis_results):
    """Generate a JSON report of the flow analysis results.
    
    Args:
        analysis_results: Results from analyze_control_flow or analyze_data_flow
        
    Returns:
        JSON string containing the report
    """
    # Convert any non-serializable objects
    def json_default(obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    return json.dumps(analysis_results, indent=2, default=json_default)

def generate_text_report(analysis_results, path):
    """Generate a text report of the control flow analysis results.
    
    Args:
        analysis_results: Results from analyze_control_flow
        path: Path that was analyzed
        
    Returns:
        String containing the text report
    """
    report = []
    report.append(f"Control Flow Analysis Report - {path}")
    report.append("=" * 80)
    
    # Summary section
    summary = analysis_results["summary"]
    report.append("\nSummary:")
    report.append(f"  Functions analyzed: {summary['total_functions']}")
    report.append(f"  Total issues found: {summary['total_issues']}")
    
    if "error" in summary:
        report.append(f"\nError: {summary['error']}")
        return "\n".join(report)
    
    # Issues section
    report.append("\nIssues by function:")
    
    for func_name, func_issues in analysis_results["issues"].items():
        report.append(f"\n  Function: {func_name}")
        
        # Dead code
        dead_code = func_issues.get("dead_code", [])
        if dead_code:
            report.append(f"    Dead code: {len(dead_code)} instances")
            for code in dead_code[:3]:  # Show only first 3 instances
                report.append(f"      - {code.get('code', 'Unknown code')}")
            if len(dead_code) > 3:
                report.append(f"      ... and {len(dead_code) - 3} more")
        else:
            report.append("    Dead code: None")
        
        # Potential infinite loops
        infinite_loops = func_issues.get("infinite_loops", [])
        if infinite_loops:
            report.append(f"    Potential infinite loops: {len(infinite_loops)} instances")
        else:
            report.append("    Potential infinite loops: None")
        
        # Complexity
        complexity = func_issues.get("complexity", {})
        if complexity:
            report.append(f"    Cyclomatic complexity: {complexity.get('cyclomatic_complexity', 'N/A')}")
            report.append(f"    Nesting depth: {complexity.get('nesting_depth', 'N/A')}")
        
        # Exit paths
        exit_paths = func_issues.get("exit_paths", {})
        if exit_paths:
            normal_exits = len(exit_paths.get("normal", []))
            exception_exits = len(exit_paths.get("exception", []))
            report.append(f"    Exit paths: {normal_exits} normal, {exception_exits} via exception")
    
    return "\n".join(report)

def generate_html_report(analysis_results, path):
    """Generate an HTML report of the control flow analysis results.
    
    Args:
        analysis_results: Results from analyze_control_flow
        path: Path that was analyzed
        
    Returns:
        String containing the HTML report
    """
    # Start with the HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Flow Analysis - {os.path.basename(path)}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            margin-bottom: 30px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .issue {{
            background-color: #fff3f3;
            border-left: 5px solid #e74c3c;
            padding: 10px;
            margin-bottom: 10px;
        }}
        .info {{
            background-color: #f8f9fa;
            border-left: 5px solid #3498db;
            padding: 10px;
            margin-bottom: 10px;
        }}
        .graph-container {{
            max-width: 100%;
            overflow-x: auto;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .metric {{
            display: inline-block;
            padding: 5px 10px;
            margin: 5px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Control Flow Analysis Report</h1>
        <p>Path: {path}</p>
    </div>
    
    <div class="card">
        <h2>Summary</h2>
        <div class="info">
            <p>Functions analyzed: {analysis_results['summary']['total_functions']}</p>
            <p>Total issues found: {analysis_results['summary']['total_issues']}</p>
"""
    
    # Add error message if present
    if "error" in analysis_results["summary"]:
        html += f"""
            <p class="issue">Error: {analysis_results['summary']['error']}</p>
"""
    
    html += """
        </div>
    </div>
"""
    
    # Function details
    for func_name, func_issues in analysis_results["issues"].items():
        html += f"""
    <div class="card">
        <h2>Function: {func_name}</h2>
        
        <div class="section">
            <h3>Complexity Metrics</h3>
"""
        # Complexity section
        complexity = func_issues.get("complexity", {})
        if complexity:
            html += f"""
            <div class="metric">Cyclomatic Complexity: <strong>{complexity.get('cyclomatic_complexity', 'N/A')}</strong></div>
            <div class="metric">Nesting Depth: <strong>{complexity.get('nesting_depth', 'N/A')}</strong></div>
            <div class="metric">Unreachable Code Blocks: <strong>{complexity.get('unreachable_code_blocks', 'N/A')}</strong></div>
            <div class="metric">Potential Infinite Loops: <strong>{complexity.get('potential_infinite_loops', 'N/A')}</strong></div>
"""
        
        # Dead code section
        html += """
        </div>
        
        <div class="section">
            <h3>Dead Code</h3>
"""
        
        dead_code = func_issues.get("dead_code", [])
        if dead_code:
            html += f"""
            <p>{len(dead_code)} unreachable code blocks found:</p>
"""
            for code in dead_code:
                code_str = code.get('code', 'Unknown code')
                html += f"""
            <div class="issue">
                <code>{code_str}</code>
            </div>
"""
        else:
            html += """
            <p>No unreachable code detected.</p>
"""
        
        # Infinite loops section
        html += """
        </div>
        
        <div class="section">
            <h3>Potential Infinite Loops</h3>
"""
        
        infinite_loops = func_issues.get("infinite_loops", [])
        if infinite_loops:
            html += f"""
            <p>{len(infinite_loops)} potential infinite loops found.</p>
"""
            for i, loop in enumerate(infinite_loops):
                html += f"""
            <div class="issue">
                <p>Loop {i+1}: {', '.join(str(node) for node in loop)}</p>
            </div>
"""
        else:
            html += """
            <p>No potential infinite loops detected.</p>
"""
        
        # Exit paths section
        html += """
        </div>
        
        <div class="section">
            <h3>Exit Paths</h3>
"""
        
        exit_paths = func_issues.get("exit_paths", {})
        normal_exits = len(exit_paths.get("normal", []))
        exception_exits = len(exit_paths.get("exception", []))
        
        html += f"""
            <div class="info">
                <p>Normal exits: {normal_exits}</p>
                <p>Exception exits: {exception_exits}</p>
            </div>
        </div>
    </div>
"""
    
    # End HTML
    html += """
</body>
</html>
"""
    
    return html

def generate_text_report_data_flow(analysis_results, path):
    """Generate a text report of the data flow analysis results.
    
    Args:
        analysis_results: Results from analyze_data_flow
        path: Path that was analyzed
        
    Returns:
        String containing the text report
    """
    report = []
    report.append(f"Data Flow Analysis Report - {path}")
    report.append("=" * 80)
    
    # Summary section
    summary = analysis_results["summary"]
    report.append("\nSummary:")
    report.append(f"  Functions analyzed: {summary['total_functions']}")
    report.append(f"  Variables tracked: {summary['total_variables']}")
    report.append(f"  Total issues found: {summary['total_issues']}")
    
    if "error" in summary:
        report.append(f"\nError: {summary['error']}")
        return "\n".join(report)
    
    # Results by function
    report.append("\nResults by function:")
    
    for func_name, df_result in analysis_results["data_flow_results"].items():
        report.append(f"\n  Function: {func_name}")
        
        # Variables
        variables = df_result.get("variables", [])
        report.append(f"    Variables ({len(variables)}):")
        if variables:
            var_str = ", ".join(variables[:10])
            if len(variables) > 10:
                var_str += f", ... ({len(variables) - 10} more)"
            report.append(f"      {var_str}")
        
        # Issues
        issues = analysis_results["issues"].get(func_name, {})
        
        # Undefined variables
        undefined = issues.get("undefined_variables", [])
        if undefined:
            report.append(f"    Undefined variables: {', '.join(undefined)}")
        
        # Unused variables
        unused = issues.get("unused_variables", [])
        if unused:
            report.append(f"    Unused variables: {', '.join(unused)}")
        
        # Uninitialized variables
        uninitialized = issues.get("uninitialized_variables", [])
        if uninitialized:
            report.append(f"    Potentially uninitialized variables: {len(uninitialized)} instances")
            for var_info in uninitialized[:3]:  # Show only first 3
                report.append(f"      - {var_info.get('variable', 'Unknown variable')}")
            if len(uninitialized) > 3:
                report.append(f"      ... and {len(uninitialized) - 3} more")
        
        # Def-Use chains
        chains = df_result.get("def_use_chains", {})
        if chains:
            report.append(f"    Definition-Use chains: {sum(len(c) for c in chains.values())} total")
    
    return "\n".join(report)

def generate_html_report_data_flow(analysis_results, path):
    """Generate an HTML report of the data flow analysis results.
    
    Args:
        analysis_results: Results from analyze_data_flow
        path: Path that was analyzed
        
    Returns:
        String containing the HTML report
    """
    # Start with the HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Flow Analysis - {os.path.basename(path)}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            margin-bottom: 30px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .issue {{
            background-color: #fff3f3;
            border-left: 5px solid #e74c3c;
            padding: 10px;
            margin-bottom: 10px;
        }}
        .info {{
            background-color: #f8f9fa;
            border-left: 5px solid #3498db;
            padding: 10px;
            margin-bottom: 10px;
        }}
        .var-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .var-item {{
            background-color: #f8f9fa;
            padding: 5px 10px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .chain-container {{
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Data Flow Analysis Report</h1>
        <p>Path: {path}</p>
    </div>
    
    <div class="card">
        <h2>Summary</h2>
        <div class="info">
            <p>Functions analyzed: {analysis_results['summary']['total_functions']}</p>
            <p>Variables tracked: {analysis_results['summary']['total_variables']}</p>
            <p>Total issues found: {analysis_results['summary']['total_issues']}</p>
"""
    
    # Add error message if present
    if "error" in analysis_results["summary"]:
        html += f"""
            <p class="issue">Error: {analysis_results['summary']['error']}</p>
"""
    
    html += """
        </div>
    </div>
"""
    
    # Function details
    for func_name, df_result in analysis_results["data_flow_results"].items():
        html += f"""
    <div class="card">
        <h2>Function: {func_name}</h2>
        
        <div class="section">
            <h3>Variables</h3>
            <div class="var-list">
"""
        
        # Variables
        variables = df_result.get("variables", [])
        for var in variables:
            html += f"""
                <div class="var-item">{var}</div>
"""
        
        html += """
            </div>
        </div>
        
        <div class="section">
            <h3>Data Flow Issues</h3>
"""
        
        # Issues
        issues = analysis_results["issues"].get(func_name, {})
        
        # Undefined variables
        undefined = issues.get("undefined_variables", [])
        if undefined:
            html += """
            <h4>Undefined Variables</h4>
            <div class="issue">
"""
            for var in undefined:
                html += f"""
                <div class="var-item">{var}</div>
"""
            html += """
            </div>
"""
        
        # Unused variables
        unused = issues.get("unused_variables", [])
        if unused:
            html += """
            <h4>Unused Variables</h4>
            <div class="issue">
"""
            for var in unused:
                html += f"""
                <div class="var-item">{var}</div>
"""
            html += """
            </div>
"""
        
        # Uninitialized variables
        uninitialized = issues.get("uninitialized_variables", [])
        if uninitialized:
            html += f"""
            <h4>Potentially Uninitialized Variables</h4>
            <div class="issue">
                <p>{len(uninitialized)} instances found</p>
                <ul>
"""
            for var_info in uninitialized:
                html += f"""
                    <li>{var_info.get('variable', 'Unknown variable')}</li>
"""
            html += """
                </ul>
            </div>
"""
        
        # If no issues
        if not undefined and not unused and not uninitialized:
            html += """
            <p>No data flow issues detected.</p>
"""
        
        # Def-Use chains
        chains = df_result.get("def_use_chains", {})
        if chains:
            html += f"""
        </div>
        
        <div class="section">
            <h3>Definition-Use Chains</h3>
            <p>{sum(len(c) for c in chains.values())} chains found</p>
            <div class="chain-container">
                <ul>
"""
            
            for var, var_chains in chains.items():
                html += f"""
                    <li><strong>{var}</strong>: {len(var_chains)} chains</li>
"""
            
            html += """
                </ul>
            </div>
"""
        
        html += """
        </div>
    </div>
"""
    
    # End HTML
    html += """
</body>
</html>
"""
    
    return html