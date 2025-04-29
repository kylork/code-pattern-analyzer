#!/usr/bin/env python3
"""
Run flow analysis on a codebase.

This script analyzes control flow and data flow in a project, generating
reports that highlight potential issues and provide insights into code structure.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analyzer import CodeAnalyzer
from src.flow.control_flow import ControlFlowAnalyzer
from src.flow.data_flow import DataFlowAnalyzer

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Analyze code flow (control flow and data flow) in a project."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the file or directory to analyze"
    )
    parser.add_argument(
        "--analysis-type", "-a",
        choices=["control", "data", "both"],
        default="both",
        help="Type of flow analysis to perform (default: both)"
    )
    parser.add_argument(
        "--function", "-f",
        help="Analyze a specific function by name"
    )
    parser.add_argument(
        "--output-control", "-oc",
        help="Output file for the control flow report"
    )
    parser.add_argument(
        "--output-data", "-od",
        help="Output file for the data flow report"
    )
    parser.add_argument(
        "--format", "-fmt",
        choices=["json", "text", "html"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--visualize/--no-visualize", "-v/",
        default=True,
        action="store_true",
        help="Generate visualizations (default: True)"
    )
    parser.add_argument(
        "--viz-dir", "-vd",
        help="Directory for visualization outputs"
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directories to exclude (e.g. 'tests,docs')"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Set default output paths
    if not args.output_control and (args.analysis_type in ["control", "both"]):
        if os.path.isfile(args.path):
            output_name = f"{Path(args.path).stem}_control_flow"
        else:
            output_name = f"{os.path.basename(os.path.abspath(args.path))}_control_flow"
        
        if args.format == "html":
            args.output_control = f"reports/{output_name}.html"
        elif args.format == "json":
            args.output_control = f"reports/{output_name}.json"
        else:
            args.output_control = f"reports/{output_name}.txt"
    
    if not args.output_data and (args.analysis_type in ["data", "both"]):
        if os.path.isfile(args.path):
            output_name = f"{Path(args.path).stem}_data_flow"
        else:
            output_name = f"{os.path.basename(os.path.abspath(args.path))}_data_flow"
        
        if args.format == "html":
            args.output_data = f"reports/{output_name}.html"
        elif args.format == "json":
            args.output_data = f"reports/{output_name}.json"
        else:
            args.output_data = f"reports/{output_name}.txt"
    
    # Set visualization directory
    if args.visualize and not args.viz_dir:
        args.viz_dir = "reports/visualizations"
    
    # Create output directories
    os.makedirs(os.path.dirname(args.output_control or "reports/dummy"), exist_ok=True)
    os.makedirs(os.path.dirname(args.output_data or "reports/dummy"), exist_ok=True)
    if args.visualize:
        os.makedirs(args.viz_dir, exist_ok=True)
    
    # Parse exclude directories
    exclude_dirs = None
    if args.exclude:
        exclude_dirs = [dir.strip() for dir in args.exclude.split(',')]
    
    # Initialize analyzers
    code_analyzer = CodeAnalyzer()
    cf_analyzer = ControlFlowAnalyzer()
    df_analyzer = DataFlowAnalyzer()
    
    # Analyze the code
    print(f"Analyzing flow in {args.path}...")
    
    if os.path.isfile(args.path):
        # Analyze a single file
        file_result = code_analyzer.analyze_file(args.path)
        
        if "error" in file_result:
            print(f"Error analyzing file: {file_result['error']}")
            return 1
            
        # Generate CFGs first (needed for both control and data flow analysis)
        cfgs = cf_analyzer.create_cfg_from_tree(
            file_result["ast"], 
            file_result["code"], 
            file_result["language"], 
            args.function
        )
        
        if not cfgs:
            print("No functions found or unable to create control flow graphs")
            return 1
            
        # Run control flow analysis if requested
        if args.analysis_type in ["control", "both"]:
            print("Performing control flow analysis...")
            
            control_flow_results = analyze_control_flow(
                file_result, cf_analyzer, cfgs, args.function, 
                args.visualize, args.viz_dir
            )
            
            # Generate the report
            write_report(
                control_flow_results, 
                args.path, 
                args.output_control, 
                args.format,
                "control"
            )
        
        # Run data flow analysis if requested
        if args.analysis_type in ["data", "both"]:
            print("Performing data flow analysis...")
            
            data_flow_results = analyze_data_flow(
                file_result, df_analyzer, cfgs, args.function,
                args.visualize, args.viz_dir
            )
            
            # Generate the report
            write_report(
                data_flow_results, 
                args.path, 
                args.output_data, 
                args.format,
                "data"
            )
    else:
        # Analyze a directory
        file_results = code_analyzer.analyze_directory(args.path, exclude_dirs=exclude_dirs)
        
        # Control flow analysis results
        if args.analysis_type in ["control", "both"]:
            print("Performing control flow analysis...")
            
            control_flow_results = {
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
                    
                cfgs = cf_analyzer.create_cfg_from_tree(
                    file_result["ast"], 
                    file_result["code"], 
                    file_result["language"], 
                    args.function
                )
                
                if not cfgs:
                    continue
                
                file_analysis = analyze_control_flow(
                    file_result, cf_analyzer, cfgs, args.function,
                    args.visualize, args.viz_dir
                )
                
                # Update combined results
                control_flow_results["control_flow_graphs"].update(file_analysis["control_flow_graphs"])
                control_flow_results["issues"].update(file_analysis["issues"])
                control_flow_results["summary"]["total_functions"] += file_analysis["summary"]["total_functions"]
                control_flow_results["summary"]["total_issues"] += file_analysis["summary"]["total_issues"]
            
            # Generate the report
            write_report(
                control_flow_results, 
                args.path, 
                args.output_control, 
                args.format,
                "control"
            )
        
        # Data flow analysis results
        if args.analysis_type in ["data", "both"]:
            print("Performing data flow analysis...")
            
            data_flow_results = {
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
                    
                cfgs = cf_analyzer.create_cfg_from_tree(
                    file_result["ast"], 
                    file_result["code"], 
                    file_result["language"], 
                    args.function
                )
                
                if not cfgs:
                    continue
                
                file_analysis = analyze_data_flow(
                    file_result, df_analyzer, cfgs, args.function,
                    args.visualize, args.viz_dir
                )
                
                # Update combined results
                data_flow_results["data_flow_results"].update(file_analysis["data_flow_results"])
                data_flow_results["issues"].update(file_analysis["issues"])
                data_flow_results["summary"]["total_functions"] += file_analysis["summary"]["total_functions"]
                data_flow_results["summary"]["total_variables"] += file_analysis["summary"]["total_variables"]
                data_flow_results["summary"]["total_issues"] += file_analysis["summary"]["total_issues"]
            
            # Generate the report
            write_report(
                data_flow_results, 
                args.path, 
                args.output_data, 
                args.format,
                "data"
            )
    
    print("Flow analysis complete.")
    return 0

def analyze_control_flow(file_result, cf_analyzer, cfgs, function_name, visualize, viz_dir):
    """Analyze control flow for a file.
    
    Args:
        file_result: Result from CodeAnalyzer.analyze_file
        cf_analyzer: ControlFlowAnalyzer instance
        cfgs: Dictionary of control flow graphs
        function_name: Optional name of function to analyze
        visualize: Whether to generate a visualization
        viz_dir: Directory for visualization outputs
        
    Returns:
        Dictionary containing analysis results
    """
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
        if visualize and (function_name is None or function_name == func_name):
            # Create a unique filename for this function's visualization
            file_base = os.path.basename(file_path)
            viz_file = f"{os.path.join(viz_dir, file_base)}_{func_name}_cfg.png"
            
            cfg.visualize(viz_file)
    
    return analysis_results

def analyze_data_flow(file_result, df_analyzer, cfgs, function_name, visualize, viz_dir):
    """Analyze data flow for a file.
    
    Args:
        file_result: Result from CodeAnalyzer.analyze_file
        df_analyzer: DataFlowAnalyzer instance
        cfgs: Dictionary of control flow graphs
        function_name: Optional name of function to analyze
        visualize: Whether to generate a visualization
        viz_dir: Directory for visualization outputs
        
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
        # Skip if a specific function was requested and this isn't it
        if function_name is not None and func_name != function_name:
            continue
            
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
        if visualize:
            # Create a unique filename for this function's visualization
            file_base = os.path.basename(file_path)
            viz_file = f"{os.path.join(viz_dir, file_base)}_{func_name}_df.png"
            
            df_analyzer.visualize_data_flow(cfg, df_result, viz_file)
    
    return analysis_results

def write_report(analysis_results, path, output_file, format_type, analysis_type):
    """Write a report of the flow analysis results.
    
    Args:
        analysis_results: Results from analyze_control_flow or analyze_data_flow
        path: Path that was analyzed
        output_file: Path to write the report to
        format_type: Format of the report (json, text, html)
        analysis_type: Type of analysis (control or data)
    """
    if not output_file:
        return
        
    import json
    from src.commands.flow import (
        generate_json_report, 
        generate_text_report, 
        generate_html_report,
        generate_text_report_data_flow,
        generate_html_report_data_flow
    )
    
    # Generate the report based on the format and analysis type
    if format_type == "json":
        report = generate_json_report(analysis_results)
    elif format_type == "html":
        if analysis_type == "control":
            report = generate_html_report(analysis_results, path)
        else:
            report = generate_html_report_data_flow(analysis_results, path)
    else:  # text format
        if analysis_type == "control":
            report = generate_text_report(analysis_results, path)
        else:
            report = generate_text_report_data_flow(analysis_results, path)
    
    # Write the report
    with open(output_file, "w") as f:
        f.write(report)
    
    print(f"{analysis_type.capitalize()} flow analysis report written to {output_file}")

if __name__ == "__main__":
    sys.exit(main())