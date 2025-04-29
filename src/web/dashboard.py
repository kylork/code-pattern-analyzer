"""
Interactive dashboard for the Code Pattern Analyzer.

This module provides a Dash-based dashboard for visualizing and exploring
analysis results from the Code Pattern Analyzer.
"""

import os
import sys
import json
import logging
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import dash
    from dash import dcc, html, callback, Input, Output, State
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
except ImportError:
    print("Error: Dashboard dependencies not found. Please install the required packages:")
    print("pip install dash dash-bootstrap-components plotly pandas")
    sys.exit(1)

# Add project src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.analyzer import CodeAnalyzer
from src.flow.control_flow import ControlFlowAnalyzer
from src.flow.data_flow import DataFlowAnalyzer
from src.metrics.complexity.complexity_analyzer import ComplexityAnalyzer
from src.refactoring.refactoring_suggestion import CompositeSuggestionGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dashboard")


def create_dashboard_app():
    """Create a Dash app for the dashboard.
    
    Returns:
        Dash app instance
    """
    # Create the Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    
    # Define the layout
    app.layout = html.Div([
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.Img(src="/assets/logo.png", height="30px"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("Code Pattern Analyzer Dashboard", className="ms-2")),
                    ],
                    align="center",
                    className="g-0"
                    ),
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Overview", href="#overview")),
                        dbc.NavItem(dbc.NavLink("Complexity", href="#complexity")),
                        dbc.NavItem(dbc.NavLink("Flow Analysis", href="#flow")),
                        dbc.NavItem(dbc.NavLink("Refactoring", href="#refactoring")),
                        dbc.NavItem(dbc.NavLink("Architecture", href="#architecture")),
                    ]),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]),
            color="dark",
            dark=True,
        ),
        
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Code Pattern Analyzer Dashboard", className="mt-4 mb-4"),
                    html.P(
                        "This dashboard provides an interactive view of code analysis results. "
                        "Upload a results file or analyze a project directly.",
                        className="lead"
                    ),
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Analysis Options"),
                        dbc.CardBody([
                            dbc.Tabs([
                                dbc.Tab([
                                    dbc.Form([
                                        dbc.Label("Results File (JSON)"),
                                        dcc.Upload(
                                            id='upload-results',
                                            children=dbc.Button('Upload Results File'),
                                            multiple=False
                                        ),
                                        html.Div(id='upload-status')
                                    ])
                                ], label="Upload Results"),
                                dbc.Tab([
                                    dbc.Form([
                                        dbc.Label("Project Path"),
                                        dbc.Input(id='project-path', type='text', placeholder='/path/to/project'),
                                        html.Br(),
                                        dbc.Label("Analysis Types"),
                                        dbc.Checklist(
                                            id='analysis-types',
                                            options=[
                                                {'label': 'Patterns', 'value': 'patterns'},
                                                {'label': 'Flow Analysis', 'value': 'flow'},
                                                {'label': 'Complexity', 'value': 'complexity'},
                                                {'label': 'Refactoring', 'value': 'refactoring'},
                                                {'label': 'Architecture', 'value': 'architecture'},
                                            ],
                                            value=['patterns', 'flow', 'complexity', 'refactoring'],
                                            inline=True
                                        ),
                                        html.Br(),
                                        dbc.Button('Run Analysis', id='run-analysis', color='primary')
                                    ])
                                ], label="Run Analysis"),
                            ], id='analysis-tabs'),
                        ])
                    ], className="mb-4"),
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div(id='results-overview')
                ], width=12)
            ]),
            
            # Content sections that will be populated based on results
            html.Div([
                html.Hr(id='overview'),
                html.H2("Overview", className="mt-4 mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Summary"),
                            dbc.CardBody(id='summary-content')
                        ]),
                    ], width=12),
                ]),
                
                html.Hr(id='complexity'),
                html.H2("Complexity Analysis", className="mt-4 mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Complexity Metrics"),
                            dbc.CardBody(id='complexity-content')
                        ]),
                    ], width=12),
                ]),
                
                html.Hr(id='flow'),
                html.H2("Flow Analysis", className="mt-4 mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Control & Data Flow"),
                            dbc.CardBody(id='flow-content')
                        ]),
                    ], width=12),
                ]),
                
                html.Hr(id='refactoring'),
                html.H2("Refactoring Suggestions", className="mt-4 mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Refactoring Overview"),
                            dbc.CardBody(id='refactoring-overview')
                        ]),
                    ], width=12),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Refactoring Suggestions"),
                            dbc.CardBody(id='refactoring-content')
                        ]),
                    ], width=12),
                ]),
                
                html.Hr(id='architecture'),
                html.H2("Architecture Analysis", className="mt-4 mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Architecture Overview"),
                            dbc.CardBody(id='architecture-content')
                        ]),
                    ], width=12),
                ]),
            ], id='results-content', style={'display': 'none'}),
            
            html.Div(id='result-storage', style={'display': 'none'}),
            
            html.Footer([
                html.Hr(),
                html.P(
                    "Code Pattern Analyzer Dashboard • Developed by Claude",
                    className="text-center text-muted"
                )
            ], className="mt-4 mb-4")
        ], fluid=True)
    ])
    
    # Callback to handle file upload
    @app.callback(
        [Output('upload-status', 'children'),
         Output('result-storage', 'children')],
        Input('upload-results', 'contents'),
        State('upload-results', 'filename')
    )
    def update_output(contents, filename):
        if contents is None:
            return "", ""
        
        try:
            content_type, content_string = contents.split(',')
            import base64
            import io
            decoded = base64.b64decode(content_string)
            
            # Check file type
            if filename.endswith('.json'):
                results = json.loads(decoded.decode('utf-8'))
                return html.Div([
                    html.P(f"Loaded file: {filename}", className="text-success"),
                    html.P(f"Analysis target: {results.get('target', 'Unknown')}")
                ]), json.dumps(results)
            else:
                return html.P(f"Invalid file type. Please upload a JSON file.", className="text-danger"), ""
        
        except Exception as e:
            return html.P(f"Error processing file: {str(e)}", className="text-danger"), ""
    
    # Callback to run analysis
    @app.callback(
        [Output('upload-status', 'children', allow_duplicate=True),
         Output('result-storage', 'children', allow_duplicate=True)],
        Input('run-analysis', 'n_clicks'),
        State('project-path', 'value'),
        State('analysis-types', 'value'),
        prevent_initial_call=True
    )
    def run_analysis(n_clicks, project_path, analysis_types):
        if n_clicks is None or not project_path:
            return "", ""
        
        try:
            # Check if path exists
            if not os.path.exists(project_path):
                return html.P(f"Error: Path does not exist: {project_path}", className="text-danger"), ""
            
            # Convert analysis types to string
            include = "all" if set(analysis_types) == set(['patterns', 'flow', 'complexity', 'refactoring', 'architecture']) else ",".join(analysis_types)
            
            # Run analysis
            results = {}
            results["target"] = project_path
            results["analysis_types"] = include
            
            # Run the selected analyses
            if 'patterns' in analysis_types:
                code_analyzer = CodeAnalyzer(use_mock=False)
                results["patterns"] = code_analyzer.analyze_directory(project_path)
            
            if 'flow' in analysis_types:
                # Control flow analysis
                cfg_analyzer = ControlFlowAnalyzer()
                results["control_flow"] = cfg_analyzer.analyze(project_path)
                
                # Data flow analysis
                df_analyzer = DataFlowAnalyzer()
                results["data_flow"] = df_analyzer.analyze(project_path)
            
            if 'complexity' in analysis_types:
                complexity_analyzer = ComplexityAnalyzer()
                results["complexity"] = complexity_analyzer.analyze(project_path)
            
            if 'refactoring' in analysis_types:
                refactoring_generator = CompositeSuggestionGenerator()
                refactoring_suggestions = refactoring_generator.generate_all_suggestions(project_path)
                results["refactoring_suggestions"] = [s.to_dict() for s in refactoring_suggestions]
            
            if 'architecture' in analysis_types:
                code_analyzer = CodeAnalyzer(use_mock=False)
                results["architecture"] = code_analyzer.analyze_architecture(project_path)
            
            return html.Div([
                html.P(f"Analysis completed for: {project_path}", className="text-success"),
                html.P(f"Included analyses: {include}")
            ]), json.dumps(results)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return html.P(f"Error running analysis: {str(e)}", className="text-danger"), ""
    
    # Callback to update results display
    @app.callback(
        [Output('results-overview', 'children'),
         Output('results-content', 'style'),
         Output('summary-content', 'children'),
         Output('complexity-content', 'children'),
         Output('flow-content', 'children'),
         Output('refactoring-overview', 'children'),
         Output('refactoring-content', 'children'),
         Output('architecture-content', 'children')],
        Input('result-storage', 'children')
    )
    def update_results_display(results_json):
        if not results_json:
            return (
                html.Div([
                    html.P("No results to display. Please upload a results file or run an analysis.", className="lead text-center mt-4")
                ]),
                {'display': 'none'},
                "", "", "", "", "", ""
            )
        
        try:
            results = json.loads(results_json)
            
            # Create overview card
            overview = create_overview_card(results)
            
            # Create content for each section
            summary = create_summary_content(results)
            complexity = create_complexity_content(results)
            flow = create_flow_content(results)
            refactoring_overview = create_refactoring_overview(results)
            refactoring = create_refactoring_content(results)
            architecture = create_architecture_content(results)
            
            return (
                overview,
                {'display': 'block'},
                summary, complexity, flow, refactoring_overview, refactoring, architecture
            )
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return (
                html.Div([
                    html.P(f"Error displaying results: {str(e)}", className="text-danger")
                ]),
                {'display': 'none'},
                "", "", "", "", "", ""
            )
    
    return app


def create_overview_card(results: Dict[str, Any]) -> html.Div:
    """Create an overview card for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the overview card
    """
    target = results.get("target", "Unknown")
    analysis_types = results.get("analysis_types", "all")
    
    # Count issues by category
    issues_count = {}
    
    # Patterns count
    if "patterns" in results:
        issues_count["Patterns"] = len(results["patterns"])
    
    # Control flow issues
    if "control_flow" in results:
        cf = results["control_flow"]
        dead_code = len(cf.get("dead_code", []))
        infinite_loops = len(cf.get("infinite_loops", []))
        issues_count["Dead Code"] = dead_code
        issues_count["Potential Infinite Loops"] = infinite_loops
    
    # Data flow issues
    if "data_flow" in results:
        df = results["data_flow"]
        unused_vars = len(df.get("unused_variables", []))
        undefined_vars = len(df.get("undefined_variables", []))
        issues_count["Unused Variables"] = unused_vars
        issues_count["Undefined Variables"] = undefined_vars
    
    # Complexity issues
    if "complexity" in results:
        complexity = results["complexity"]
        if "cyclomatic_complexity" in complexity:
            cc = complexity["cyclomatic_complexity"]
            high_complexity = sum(1 for file_data in cc.values() 
                                 for func_data in file_data.values() 
                                 if func_data.get("complexity", 0) > 10)
            issues_count["High Complexity Functions"] = high_complexity
    
    # Refactoring suggestions
    if "refactoring_suggestions" in results:
        suggestions = results["refactoring_suggestions"]
        issues_count["Refactoring Suggestions"] = len(suggestions)
        
        # Count by impact
        for impact in ["critical", "high", "medium", "low"]:
            count = sum(1 for s in suggestions if s["impact"] == impact)
            if count > 0:
                issues_count[f"{impact.capitalize()} Impact Refactorings"] = count
    
    # Architecture issues
    if "architecture" in results:
        arch = results["architecture"]
        if "anti_patterns" in arch:
            issues_count["Architecture Anti-patterns"] = len(arch["anti_patterns"])
    
    # Create overview card
    return html.Div([
        dbc.Card([
            dbc.CardHeader(html.H3("Analysis Results Overview")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4("Project Information"),
                        html.P(f"Target: {target}"),
                        html.P(f"Analysis Types: {analysis_types}")
                    ], width=6),
                    dbc.Col([
                        html.H4("Issues Summary"),
                        html.Div([
                            create_badge(category, count)
                            for category, count in issues_count.items()
                        ])
                    ], width=6)
                ])
            ])
        ], className="mb-4")
    ])


def create_badge(category: str, count: int) -> html.Div:
    """Create a badge for an issue category.
    
    Args:
        category: Issue category
        count: Issue count
        
    Returns:
        Dash component with the badge
    """
    # Determine badge color based on category
    color = "primary"
    if "Critical" in category or "Error" in category or "Infinite" in category:
        color = "danger"
    elif "High" in category or "Undefined" in category:
        color = "warning"
    elif "Medium" in category or "Dead" in category or "Unused" in category:
        color = "info"
    elif "Low" in category:
        color = "success"
    
    return html.Div([
        dbc.Badge(f"{category}: {count}", color=color, className="me-1 mb-1 badge-pill")
    ], className="d-inline-block")


def create_summary_content(results: Dict[str, Any]) -> html.Div:
    """Create summary content for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the summary content
    """
    target = results.get("target", "Unknown")
    
    # Create metrics
    metrics = []
    
    # Patterns count
    if "patterns" in results:
        patterns_count = len(results["patterns"])
        metrics.append(create_metric_card("Patterns Detected", patterns_count, "primary"))
    
    # Control & data flow issues
    flow_issues = 0
    if "control_flow" in results:
        cf = results["control_flow"]
        flow_issues += len(cf.get("dead_code", []))
        flow_issues += len(cf.get("infinite_loops", []))
    
    if "data_flow" in results:
        df = results["data_flow"]
        flow_issues += len(df.get("unused_variables", []))
        flow_issues += len(df.get("undefined_variables", []))
    
    if flow_issues > 0:
        metrics.append(create_metric_card("Flow Issues", flow_issues, "warning"))
    
    # Complexity
    if "complexity" in results:
        complexity = results["complexity"]
        if "cyclomatic_complexity" in complexity:
            cc = complexity["cyclomatic_complexity"]
            high_complexity = sum(1 for file_data in cc.values() 
                                 for func_data in file_data.values() 
                                 if func_data.get("complexity", 0) > 10)
            metrics.append(create_metric_card("High Complexity", high_complexity, "danger"))
    
    # Refactoring suggestions
    if "refactoring_suggestions" in results:
        suggestions = results["refactoring_suggestions"]
        metrics.append(create_metric_card("Refactoring Suggestions", len(suggestions), "success"))
    
    # Architecture issues
    if "architecture" in results:
        arch = results["architecture"]
        if "anti_patterns" in arch:
            metrics.append(create_metric_card("Architecture Anti-patterns", len(arch["anti_patterns"]), "info"))
    
    # Create summary card
    return html.Div([
        dbc.Row([
            dbc.Col(metric, width=12 // len(metrics) if len(metrics) > 0 else 12)
            for metric in metrics
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H4("Analysis Results Distribution"),
                dcc.Graph(figure=create_summary_chart(results))
            ], width=12)
        ])
    ])


def create_metric_card(title: str, value: int, color: str) -> dbc.Card:
    """Create a metric card.
    
    Args:
        title: Metric title
        value: Metric value
        color: Card color
        
    Returns:
        Dash Bootstrap card component
    """
    return dbc.Card([
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.H2(value, className="card-text text-center"),
        ])
    ], color=color, inverse=True, className="mb-4 text-center")


def create_summary_chart(results: Dict[str, Any]) -> go.Figure:
    """Create a summary chart for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Plotly figure
    """
    categories = []
    values = []
    
    # Patterns count
    if "patterns" in results:
        categories.append("Patterns")
        values.append(len(results["patterns"]))
    
    # Control flow issues
    if "control_flow" in results:
        cf = results["control_flow"]
        categories.append("Dead Code")
        values.append(len(cf.get("dead_code", [])))
        categories.append("Infinite Loops")
        values.append(len(cf.get("infinite_loops", [])))
    
    # Data flow issues
    if "data_flow" in results:
        df = results["data_flow"]
        categories.append("Unused Variables")
        values.append(len(df.get("unused_variables", [])))
        categories.append("Undefined Variables")
        values.append(len(df.get("undefined_variables", [])))
    
    # Complexity issues
    if "complexity" in results:
        complexity = results["complexity"]
        if "cyclomatic_complexity" in complexity:
            cc = complexity["cyclomatic_complexity"]
            high_complexity = sum(1 for file_data in cc.values() 
                                 for func_data in file_data.values() 
                                 if func_data.get("complexity", 0) > 10)
            categories.append("High Complexity Functions")
            values.append(high_complexity)
    
    # Refactoring suggestions
    if "refactoring_suggestions" in results:
        suggestions = results["refactoring_suggestions"]
        # Count by impact
        for impact in ["critical", "high", "medium", "low"]:
            count = sum(1 for s in suggestions if s["impact"] == impact)
            if count > 0:
                categories.append(f"{impact.capitalize()} Impact Refactorings")
                values.append(count)
    
    # Architecture issues
    if "architecture" in results:
        arch = results["architecture"]
        if "anti_patterns" in arch:
            categories.append("Architecture Anti-patterns")
            values.append(len(arch["anti_patterns"]))
    
    # Create chart
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'][:len(categories)]
    )])
    
    fig.update_layout(
        title="Analysis Results by Category",
        xaxis_title="Category",
        yaxis_title="Count",
        template="plotly_white"
    )
    
    return fig


def create_complexity_content(results: Dict[str, Any]) -> html.Div:
    """Create complexity content for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the complexity content
    """
    if "complexity" not in results:
        return html.P("No complexity data available.")
    
    complexity = results["complexity"]
    if "cyclomatic_complexity" not in complexity:
        return html.P("No cyclomatic complexity data available.")
    
    cc = complexity["cyclomatic_complexity"]
    
    # Extract functions with their complexity
    functions = []
    for file_path, file_data in cc.items():
        for func_name, func_data in file_data.items():
            complexity_value = func_data.get("complexity", 0)
            functions.append({
                "file": os.path.basename(file_path),
                "function": func_name,
                "complexity": complexity_value,
                "start_line": func_data.get("start_line", 0),
                "end_line": func_data.get("end_line", 0)
            })
    
    # Sort by complexity
    functions = sorted(functions, key=lambda x: x["complexity"], reverse=True)
    
    # Create data for bar chart
    if functions:
        # Take top 20 functions for the chart
        top_functions = functions[:20]
        
        # Create chart
        fig = go.Figure(data=[go.Bar(
            x=[f"{func['function']} ({func['file']})" for func in top_functions],
            y=[func["complexity"] for func in top_functions],
            marker_color=['#d62728' if func["complexity"] > 15 else 
                          '#ff7f0e' if func["complexity"] > 10 else 
                          '#2ca02c' if func["complexity"] > 7 else 
                          '#1f77b4' for func in top_functions]
        )])
        
        fig.update_layout(
            title="Top 20 Functions by Cyclomatic Complexity",
            xaxis_title="Function",
            yaxis_title="Cyclomatic Complexity",
            template="plotly_white",
            xaxis_tickangle=-45,
            height=500
        )
        
        # Add threshold lines
        fig.add_shape(type="line",
            x0=-0.5, y0=15, x1=len(top_functions)-0.5, y1=15,
            line=dict(color="red", width=2, dash="dash")
        )
        
        fig.add_shape(type="line",
            x0=-0.5, y0=10, x1=len(top_functions)-0.5, y1=10,
            line=dict(color="orange", width=2, dash="dash")
        )
        
        fig.add_shape(type="line",
            x0=-0.5, y0=7, x1=len(top_functions)-0.5, y1=7,
            line=dict(color="green", width=2, dash="dash")
        )
        
        # Create table of high complexity functions (complexity > 7)
        high_complexity_funcs = [func for func in functions if func["complexity"] > 7]
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H4("Function Complexity Distribution"),
                    dcc.Graph(figure=fig)
                ], width=12)
            ]),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.H4(f"High Complexity Functions ({len(high_complexity_funcs)})"),
                    dbc.Table.from_dataframe(
                        pd.DataFrame(high_complexity_funcs),
                        striped=True, bordered=True, hover=True, responsive=True,
                    ) if high_complexity_funcs else html.P("No high complexity functions found.")
                ], width=12)
            ])
        ])
    else:
        return html.P("No complexity data available.")


def create_flow_content(results: Dict[str, Any]) -> html.Div:
    """Create flow content for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the flow content
    """
    content = []
    
    # Control flow issues
    if "control_flow" in results:
        cf = results["control_flow"]
        
        # Dead code
        if "dead_code" in cf and cf["dead_code"]:
            dead_code = cf["dead_code"]
            content.append(html.Div([
                html.H4(f"Dead Code ({len(dead_code)})"),
                dbc.Table.from_dataframe(
                    pd.DataFrame([{
                        "file": os.path.basename(item["file_path"]),
                        "function": item["function_name"],
                        "lines": f"{item['start_line']}-{item['end_line']}",
                        "type": item["type"]
                    } for item in dead_code]),
                    striped=True, bordered=True, hover=True, responsive=True,
                ) if dead_code else html.P("No dead code found.")
            ]))
        
        # Infinite loops
        if "infinite_loops" in cf and cf["infinite_loops"]:
            infinite_loops = cf["infinite_loops"]
            content.append(html.Div([
                html.H4(f"Potential Infinite Loops ({len(infinite_loops)})"),
                dbc.Table.from_dataframe(
                    pd.DataFrame([{
                        "file": os.path.basename(item["file_path"]),
                        "function": item["function_name"],
                        "lines": f"{item['start_line']}-{item['end_line']}"
                    } for item in infinite_loops]),
                    striped=True, bordered=True, hover=True, responsive=True,
                ) if infinite_loops else html.P("No potential infinite loops found.")
            ]))
    
    # Data flow issues
    if "data_flow" in results:
        df = results["data_flow"]
        
        # Unused variables
        if "unused_variables" in df and df["unused_variables"]:
            unused_vars = df["unused_variables"]
            content.append(html.Div([
                html.H4(f"Unused Variables ({len(unused_vars)})"),
                dbc.Table.from_dataframe(
                    pd.DataFrame([{
                        "file": os.path.basename(item["file_path"]),
                        "function": item["function_name"],
                        "variable": item["variable_name"],
                        "line": item["line"]
                    } for item in unused_vars]),
                    striped=True, bordered=True, hover=True, responsive=True,
                ) if unused_vars else html.P("No unused variables found.")
            ]))
        
        # Undefined variables
        if "undefined_variables" in df and df["undefined_variables"]:
            undefined_vars = df["undefined_variables"]
            content.append(html.Div([
                html.H4(f"Potentially Undefined Variables ({len(undefined_vars)})"),
                dbc.Table.from_dataframe(
                    pd.DataFrame([{
                        "file": os.path.basename(item["file_path"]),
                        "function": item["function_name"],
                        "variable": item["variable_name"],
                        "line": item["line"]
                    } for item in undefined_vars]),
                    striped=True, bordered=True, hover=True, responsive=True,
                ) if undefined_vars else html.P("No undefined variables found.")
            ]))
    
    if not content:
        return html.P("No flow analysis data available.")
    
    return html.Div(content)


def create_refactoring_overview(results: Dict[str, Any]) -> html.Div:
    """Create refactoring overview for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the refactoring overview
    """
    if "refactoring_suggestions" not in results or not results["refactoring_suggestions"]:
        return html.P("No refactoring suggestions available.")
    
    suggestions = results["refactoring_suggestions"]
    
    # Count by impact
    impact_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for s in suggestions:
        impact = s["impact"]
        impact_counts[impact] += 1
    
    # Count by type
    type_counts = {}
    for s in suggestions:
        refactoring_type = s["refactoring_type"]
        if refactoring_type not in type_counts:
            type_counts[refactoring_type] = 0
        type_counts[refactoring_type] += 1
    
    # Create impact pie chart
    impact_fig = go.Figure(data=[go.Pie(
        labels=list(impact_counts.keys()),
        values=list(impact_counts.values()),
        hole=.3,
        marker_colors=['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4']
    )])
    
    impact_fig.update_layout(
        title="Refactoring Suggestions by Impact",
        template="plotly_white"
    )
    
    # Create type bar chart
    type_fig = go.Figure(data=[go.Bar(
        x=list(type_counts.keys()),
        y=list(type_counts.values()),
        marker_color='#1f77b4'
    )])
    
    type_fig.update_layout(
        title="Refactoring Suggestions by Type",
        xaxis_title="Refactoring Type",
        yaxis_title="Count",
        template="plotly_white",
        xaxis_tickangle=-45
    )
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=impact_fig)
            ], width=6),
            dbc.Col([
                dcc.Graph(figure=type_fig)
            ], width=6)
        ])
    ])


def create_refactoring_content(results: Dict[str, Any]) -> html.Div:
    """Create refactoring content for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the refactoring content
    """
    if "refactoring_suggestions" not in results or not results["refactoring_suggestions"]:
        return html.P("No refactoring suggestions available.")
    
    suggestions = results["refactoring_suggestions"]
    
    # Sort by impact
    impact_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_suggestions = sorted(suggestions, key=lambda s: (impact_order[s["impact"]], s["file_path"]))
    
    # Create cards for each suggestion
    cards = []
    for i, suggestion in enumerate(sorted_suggestions):
        description = suggestion["description"]
        refactoring_type = suggestion["refactoring_type"]
        impact = suggestion["impact"]
        file_path = suggestion["file_path"]
        line_range = suggestion["line_range"]
        benefits = suggestion.get("benefits", [])
        
        # Determine card color based on impact
        color = "primary"
        if impact == "critical":
            color = "danger"
        elif impact == "high":
            color = "warning"
        elif impact == "medium":
            color = "info"
        elif impact == "low":
            color = "success"
        
        card = dbc.Card([
            dbc.CardHeader([
                html.H5(f"{description}", className="card-title"),
                html.Div([
                    dbc.Badge(refactoring_type, className="me-1"),
                    dbc.Badge(impact.upper(), color=color, className="me-1")
                ])
            ]),
            dbc.CardBody([
                html.P(f"File: {os.path.basename(file_path)}"),
                html.P(f"Lines: {line_range[0]}-{line_range[1]}"),
                html.H6("Benefits:") if benefits else None,
                html.Ul([html.Li(benefit) for benefit in benefits]) if benefits else None,
                
                dbc.Button(
                    "View Code",
                    id=f"view-code-btn-{i}",
                    color="secondary",
                    size="sm",
                    className="mt-2",
                    n_clicks=0
                ) if suggestion.get("before_code") else None,
                
                dbc.Collapse([
                    html.Hr(),
                    html.H6("Current Code:"),
                    dbc.Card(dbc.CardBody(dcc.Markdown(f"```python\n{suggestion.get('before_code', '')}\n```")), className="bg-light"),
                    html.H6("Suggested Code:") if suggestion.get("after_code") else None,
                    dbc.Card(dbc.CardBody(dcc.Markdown(f"```python\n{suggestion.get('after_code', '')}\n```")), className="bg-light") if suggestion.get("after_code") else None
                ], id=f"code-collapse-{i}", is_open=False)
            ])
        ], className="mb-3 border-left-{color}")
        
        cards.append(card)
    
    # Add callbacks for code view buttons
    for i in range(len(sorted_suggestions)):
        @callback(
            Output(f"code-collapse-{i}", "is_open"),
            Input(f"view-code-btn-{i}", "n_clicks"),
            State(f"code-collapse-{i}", "is_open"),
        )
        def toggle_code_collapse(n_clicks, is_open, i=i):
            if n_clicks:
                return not is_open
            return is_open
    
    return html.Div([
        html.Div(card) for card in cards
    ])


def create_architecture_content(results: Dict[str, Any]) -> html.Div:
    """Create architecture content for the dashboard.
    
    Args:
        results: Analysis results
        
    Returns:
        Dash component with the architecture content
    """
    if "architecture" not in results:
        return html.P("No architecture analysis data available.")
    
    arch = results["architecture"]
    content = []
    
    # Architectural styles
    if "styles" in arch and arch["styles"]:
        styles = arch["styles"]
        
        # Create chart for styles confidence
        style_fig = go.Figure(data=[go.Bar(
            x=[style["name"] for style in styles],
            y=[style["confidence"] for style in styles],
            marker_color='#1f77b4'
        )])
        
        style_fig.update_layout(
            title="Detected Architectural Styles",
            xaxis_title="Style",
            yaxis_title="Confidence (%)",
            template="plotly_white"
        )
        
        content.append(html.Div([
            html.H4("Architectural Styles"),
            dcc.Graph(figure=style_fig)
        ]))
    
    # Architectural anti-patterns
    if "anti_patterns" in arch and arch["anti_patterns"]:
        anti_patterns = arch["anti_patterns"]
        
        content.append(html.Div([
            html.H4(f"Architectural Anti-patterns ({len(anti_patterns)})"),
            dbc.Table.from_dataframe(
                pd.DataFrame([{
                    "name": anti["name"],
                    "description": anti.get("description", ""),
                    "severity": anti.get("severity", "")
                } for anti in anti_patterns]),
                striped=True, bordered=True, hover=True, responsive=True,
            ) if anti_patterns else html.P("No architectural anti-patterns found.")
        ]))
    
    if not content:
        return html.P("No architecture analysis data available.")
    
    return html.Div(content)


def run_dashboard() -> None:
    """Run the Code Pattern Analyzer dashboard."""
    app = create_dashboard_app()
    
    # Create assets directory if it doesn't exist
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Open browser
    webbrowser.open("http://127.0.0.1:8050/")
    
    # Run server
    app.run_server(debug=True)


if __name__ == "__main__":
    run_dashboard()