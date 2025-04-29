#!/usr/bin/env python3
"""
Code Pattern Analyzer - Unified GUI Launcher

This is the main entry point for the Code Pattern Analyzer application.
It provides a web-based GUI that gives access to all the tool's features:
- Architectural pattern detection
- Code visualization
- Code-pattern linkage
- Analysis reports
- And more

Usage:
    python code_pattern_analyzer_gui.py
"""

import os
import sys
import webbrowser
import logging
import argparse
import subprocess
import threading
import time
from pathlib import Path
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import signal

# Import Code Pattern Analyzer modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.demo_projects import get_demo_projects, get_demo_project_by_name

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Path constants
ROOT_DIR = Path(__file__).parent.absolute()
DASHBOARD_DIR = ROOT_DIR / "web_ui" / "frontend" / "build"
STATIC_DIR = ROOT_DIR / "web_ui" / "static"
API_DIR = ROOT_DIR / "web_ui" / "api"
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "tmp"

# Ensure output and temp directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

class CodePatternAnalyzerAPI(SimpleHTTPRequestHandler):
    """Handler for API requests from the web UI."""
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        # API endpoints
        if self.path.startswith('/api/'):
            self.handle_api_request()
            return
            
        # Serve static files
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path.startswith('/api/'):
            self.handle_api_request()
            return
            
        self.send_error(404, "Not Found")
    
    def handle_api_request(self):
        """Handle API requests."""
        if self.path == '/api/analyze':
            self.handle_analyze_request()
        elif self.path == '/api/visualize':
            self.handle_visualize_request()
        elif self.path == '/api/list-visualizations':
            self.handle_list_visualizations()
        elif self.path == '/api/status':
            self.handle_status_request()
        elif self.path == '/api/demo-projects':
            self.handle_demo_projects_request()
        elif self.path == '/api/run-demo':
            self.handle_run_demo_request()
        elif self.path == '/api/generate-report':
            self.handle_generate_report_request()
        elif self.path == '/api/pattern-transformation':
            self.handle_pattern_transformation_request()
        elif self.path == '/api/pattern-opportunities':
            self.handle_pattern_opportunities_request()
        elif self.path == '/api/transformations-list':
            self.handle_transformations_list_request()
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_analyze_request(self):
        """Handle requests to analyze code."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        directory = request_data.get('directory')
        style = request_data.get('style', 'layered')
        
        if not directory:
            self.send_error(400, "Missing directory parameter")
            return
        
        # Run analysis in background
        result = {
            'status': 'started',
            'message': f'Analysis started for {directory}',
            'job_id': str(int(time.time())),
        }
        
        threading.Thread(
            target=self._run_analysis,
            args=(directory, style, result['job_id'])
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def _run_analysis(self, directory, style, job_id):
        """Run analysis in background."""
        try:
            logger.info(f"Starting analysis of {directory} with style {style}")
            output_file = f"analysis_{job_id}.html"
            output_path = os.path.join(OUTPUT_DIR, output_file)
            
            # Run the code pattern linkage analysis
            cmd = [
                sys.executable,
                os.path.join(ROOT_DIR, "run_code_pattern_linkage.py"),
                directory,
                "--output", output_file,
                "--output-dir", str(OUTPUT_DIR),
                "--style", style,
                "--title", f"Analysis of {os.path.basename(directory)}"
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Save the result status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'completed' if result.returncode == 0 else 'failed',
                    'output_file': output_file if result.returncode == 0 else None,
                    'message': 'Analysis completed successfully' if result.returncode == 0 else 'Analysis failed',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode,
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"Analysis completed with status: {status['status']}")
            
        except Exception as e:
            logger.error(f"Error running analysis: {str(e)}")
            # Save error status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'failed',
                    'message': f'Error running analysis: {str(e)}',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
    
    def handle_visualize_request(self):
        """Handle request to visualize analysis results."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        visualization_file = request_data.get('file')
        if not visualization_file:
            self.send_error(400, "Missing file parameter")
            return
        
        # Construct full path
        full_path = os.path.join(OUTPUT_DIR, visualization_file)
        if not os.path.exists(full_path):
            self.send_error(404, "Visualization file not found")
            return
        
        # Open the visualization in the browser
        webbrowser.open(f"file://{full_path}")
        
        # Return success
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'message': f'Opening visualization: {visualization_file}'
        }).encode())
    
    def handle_list_visualizations(self):
        """Handle request to list available visualizations."""
        visualizations = []
        
        # Get all HTML files in the output directory
        for file in os.listdir(OUTPUT_DIR):
            if file.endswith('.html'):
                file_path = os.path.join(OUTPUT_DIR, file)
                visualizations.append({
                    'filename': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': os.path.getmtime(file_path)
                })
        
        # Sort by modification time (newest first)
        visualizations.sort(key=lambda x: x['modified'], reverse=True)
        
        # Return the list
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'visualizations': visualizations
        }).encode())
    
    def handle_status_request(self):
        """Handle request for job status."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        job_id = request_data.get('job_id')
        if not job_id:
            self.send_error(400, "Missing job_id parameter")
            return
        
        status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
        if not os.path.exists(status_file):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'running',
                'message': 'Analysis is still running'
            }).encode())
            return
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
        
    def handle_demo_projects_request(self):
        """Handle request to list available demo projects."""
        demo_projects = get_demo_projects()
        
        # Convert to dictionaries for JSON serialization
        projects_data = [project.to_dict() for project in demo_projects]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'demo_projects': projects_data
        }).encode())
    
    def handle_run_demo_request(self):
        """Handle request to run analysis on a demo project."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        project_name = request_data.get('project_name')
        if not project_name:
            self.send_error(400, "Missing project_name parameter")
            return
        
        # Get the demo project
        demo_project = get_demo_project_by_name(project_name)
        if not demo_project:
            self.send_error(404, "Demo project not found")
            return
        
        # Get the full path to the demo project
        project_path = demo_project.get_full_path()
        if not os.path.exists(project_path):
            self.send_error(404, f"Demo project directory not found: {project_path}")
            return
        
        # Start analysis in background
        result = {
            'status': 'started',
            'message': f'Demo analysis started for {project_name}',
            'job_id': str(int(time.time())),
            'project': demo_project.to_dict()
        }
        
        threading.Thread(
            target=self._run_analysis,
            args=(project_path, demo_project.architecture_style, result['job_id'])
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def handle_generate_report_request(self):
        """Handle request to generate a shareable report from a visualization."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        visualization_file = request_data.get('file')
        if not visualization_file:
            self.send_error(400, "Missing file parameter")
            return
        
        # Construct full path
        full_path = os.path.join(OUTPUT_DIR, visualization_file)
        if not os.path.exists(full_path):
            self.send_error(404, "Visualization file not found")
            return
        
        # Create report job ID
        job_id = str(int(time.time()))
        
        # Start report generation in background
        threading.Thread(
            target=self._generate_report,
            args=(full_path, job_id)
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'started',
            'message': 'Report generation started',
            'job_id': job_id
        }).encode())
    
    def _generate_report(self, visualization_path, job_id):
        """Generate a shareable report from a visualization.
        
        Args:
            visualization_path: Path to the visualization HTML file
            job_id: Job ID for tracking status
        """
        try:
            # Create output report filename
            report_filename = f"report_{os.path.basename(visualization_path)}"
            report_path = os.path.join(OUTPUT_DIR, report_filename)
            
            # Create a portable bundle
            bundle_dir = os.path.join(OUTPUT_DIR, f"report_bundle_{job_id}")
            os.makedirs(bundle_dir, exist_ok=True)
            
            # Import here to avoid circular imports
            from src.visualization.visualization_utilities import create_visualization_bundle
            
            # Create the bundle
            bundle_path = create_visualization_bundle(visualization_path, bundle_dir)
            
            # Save the result status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'completed',
                    'report_file': report_filename,
                    'bundle_path': bundle_path,
                    'message': 'Report generated successfully',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"Report generation completed: {bundle_path}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            # Save error status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'failed',
                    'message': f'Error generating report: {str(e)}',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)


    def handle_pattern_transformation_request(self):
        """Handle request to open the pattern transformation interface."""
        # Open the pattern transformation GUI in a new browser tab
        transformation_url = "http://localhost:8082/pattern_transformation.html"
        webbrowser.open(transformation_url)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'message': 'Opening Pattern Transformation interface'
        }).encode())
    
    def handle_pattern_opportunities_request(self):
        """Handle request to detect pattern opportunities in a file."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        target = request_data.get('target')
        content = request_data.get('content')
        
        if not target and not content:
            self.send_error(400, "Missing target or content parameter")
            return
        
        # Create a job ID for tracking
        job_id = str(int(time.time()))
        
        # Start analysis in background
        threading.Thread(
            target=self._detect_pattern_opportunities,
            args=(target, content, job_id)
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'started',
            'message': f'Pattern opportunity detection started',
            'job_id': job_id
        }).encode())
    
    def _detect_pattern_opportunities(self, target, content, job_id):
        """Detect pattern opportunities in the background."""
        try:
            # Import here to avoid circular imports
            from recommendation_detector import detect_pattern_opportunities
            
            # Create temporary file if content is provided
            temp_file = None
            if content:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                    f.write(content.encode('utf-8'))
                    temp_file = f.name
                    target = temp_file
            
            # Detect pattern opportunities
            opportunities = detect_pattern_opportunities(target)
            
            # Group opportunities by pattern
            grouped_opportunities = {}
            for opportunity in opportunities:
                pattern_name = opportunity["pattern_name"]
                if pattern_name not in grouped_opportunities:
                    grouped_opportunities[pattern_name] = []
                grouped_opportunities[pattern_name].append(opportunity)
            
            # Save the result status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'completed',
                    'message': 'Pattern opportunity detection completed successfully',
                    'target': target,
                    'opportunities': grouped_opportunities,
                    'job_id': job_id,
                    'temp_file': temp_file,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"Pattern opportunity detection completed with {len(opportunities)} opportunities found")
            
        except Exception as e:
            logger.error(f"Error detecting pattern opportunities: {str(e)}")
            # Save error status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'failed',
                    'message': f'Error detecting pattern opportunities: {str(e)}',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
            
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def handle_transformations_list_request(self):
        """Handle request to list applied transformations."""
        # Look for transformation record files
        transformations = []
        
        for file in os.listdir(TEMP_DIR):
            if file.startswith('transformation_') and file.endswith('.json'):
                file_path = os.path.join(TEMP_DIR, file)
                
                with open(file_path, 'r') as f:
                    record = json.load(f)
                
                # Check if the output file exists
                output_path = record.get('output_path')
                if output_path and os.path.exists(output_path):
                    record['exists'] = True
                    record['size'] = os.path.getsize(output_path)
                else:
                    record['exists'] = False
                
                transformations.append(record)
        
        # Sort by timestamp (newest first)
        transformations.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'transformations': transformations
        }).encode())
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

def create_simple_dashboard():
    """Create a simple dashboard HTML if the React frontend is not built."""
    dashboard_path = STATIC_DIR / "dashboard.html"
    STATIC_DIR.mkdir(exist_ok=True)
    
    if dashboard_path.exists():
        return dashboard_path
        
    with open(dashboard_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Pattern Analyzer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .main-container {
            display: flex;
            gap: 20px;
        }
        .sidebar {
            flex: 0 0 300px;
            background: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .content {
            flex: 1;
            background: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        button, input {
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            width: 100%;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background-color: #45a049;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .demo-card {
            border-left: 4px solid #5bc0de;
        }
        h2 {
            color: #2c3e50;
            margin-top: 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background-color: #dff0d8;
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        .error {
            background-color: #f2dede;
            color: #a94442;
            border: 1px solid #ebccd1;
        }
        .info {
            background-color: #d9edf7;
            color: #31708f;
            border: 1px solid #bce8f1;
        }
        .refresh-btn {
            background-color: #5bc0de;
            margin-top: 20px;
        }
        .visualize-btn {
            background-color: #f0ad4e;
            margin-right: 5px;
        }
        .report-btn {
            background-color: #5bc0de;
            margin-left: 5px;
        }
        .timestamp {
            font-size: 12px;
            color: #777;
            margin-top: 5px;
        }
        select {
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
            width: 100%;
        }
        .tab-container {
            margin-bottom: 20px;
        }
        .tab-buttons {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 15px;
        }
        .tab-button {
            background: none;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
            color: #777;
            width: auto;
        }
        .tab-button.active {
            color: #2c3e50;
            border-bottom: 3px solid #4CAF50;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .action-buttons {
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }
        .action-buttons button {
            flex: 1;
        }
        .demo-container {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }
        .badge-layered {
            background-color: #d9edf7;
            color: #31708f;
        }
        .badge-clean {
            background-color: #dff0d8;
            color: #3c763d;
        }
        .badge-hexagonal {
            background-color: #fcf8e3;
            color: #8a6d3b;
        }
        .badge-event_driven {
            background-color: #f2dede;
            color: #a94442;
        }
        .badge-microservices {
            background-color: #e8eaf6;
            color: #3f51b5;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Code Pattern Analyzer</div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <div class="tab-container">
                <div class="tab-buttons">
                    <button class="tab-button active" data-tab="analyze">Analyze</button>
                    <button class="tab-button" data-tab="demo">Demo</button>
                </div>
                
                <div id="analyzeTab" class="tab-content active">
                    <h2>Run Analysis</h2>
                    <form id="analyzeForm">
                        <div>
                            <label for="directoryInput">Project Directory:</label>
                            <input type="text" id="directoryInput" placeholder="/path/to/project" required>
                        </div>
                        <div>
                            <label for="styleSelect">Architectural Style:</label>
                            <select id="styleSelect">
                                <option value="layered">Layered Architecture</option>
                                <option value="hexagonal">Hexagonal Architecture</option>
                                <option value="clean">Clean Architecture</option>
                                <option value="event_driven">Event-driven Architecture</option>
                                <option value="microservices">Microservices Architecture</option>
                            </select>
                        </div>
                        <button type="submit">Analyze Project</button>
                    </form>
                </div>
                
                <div id="demoTab" class="tab-content">
                    <h2>Demo Projects</h2>
                    <p>Try these sample projects to see the analyzer in action.</p>
                    <div id="demoProjectsList">
                        <p>Loading demo projects...</p>
                    </div>
                </div>
            </div>
            
            <div id="status" class="status"></div>
            
            <button id="refreshBtn" class="refresh-btn">Refresh Visualizations</button>
        </div>
        
        <div class="content">
            <h2>Available Visualizations</h2>
            <div id="visualizationsList"></div>
        </div>
    </div>

    <script>
        // Current job id for tracking analysis status
        let currentJobId = null;
        let statusCheckInterval = null;
        
        // DOM elements
        const analyzeForm = document.getElementById('analyzeForm');
        const statusDiv = document.getElementById('status');
        const refreshBtn = document.getElementById('refreshBtn');
        const visualizationsList = document.getElementById('visualizationsList');
        const demoProjectsList = document.getElementById('demoProjectsList');
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        // Event listeners
        analyzeForm.addEventListener('submit', handleAnalyzeSubmit);
        refreshBtn.addEventListener('click', fetchVisualizations);
        
        // Tab functionality
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.getAttribute('data-tab');
                
                // Update active button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update active content
                tabContents.forEach(content => content.classList.remove('active'));
                document.getElementById(tabId + 'Tab').classList.add('active');
            });
        });
        
        // Initial load
        fetchVisualizations();
        fetchDemoProjects();
        
        // Handle form submission for analysis
        async function handleAnalyzeSubmit(event) {
            event.preventDefault();
            
            const directory = document.getElementById('directoryInput').value;
            const style = document.getElementById('styleSelect').value;
            
            if (!directory) {
                showStatus('Please enter a project directory', 'error');
                return;
            }
            
            try {
                showStatus('Starting analysis...', 'info');
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ directory, style })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentJobId = data.job_id;
                    showStatus(`Analysis started: ${data.message}`, 'info');
                    
                    // Start checking status
                    if (statusCheckInterval) {
                        clearInterval(statusCheckInterval);
                    }
                    statusCheckInterval = setInterval(checkAnalysisStatus, 2000);
                } else {
                    showStatus(`Failed to start analysis: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error starting analysis:', error);
            }
        }
        
        // Fetch demo projects
        async function fetchDemoProjects() {
            try {
                const response = await fetch('/api/demo-projects', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayDemoProjects(data.demo_projects);
                } else {
                    demoProjectsList.innerHTML = '<p>Failed to load demo projects.</p>';
                }
            } catch (error) {
                console.error('Error fetching demo projects:', error);
                demoProjectsList.innerHTML = '<p>Error loading demo projects.</p>';
            }
        }
        
        // Display demo projects
        function displayDemoProjects(projects) {
            demoProjectsList.innerHTML = '';
            
            if (projects.length === 0) {
                demoProjectsList.innerHTML = '<p>No demo projects available.</p>';
                return;
            }
            
            projects.forEach(project => {
                const card = document.createElement('div');
                card.className = 'card demo-card';
                
                // Create style badge
                const styleBadge = `<span class="badge badge-${project.architecture_style}">${project.architecture_style}</span>`;
                
                card.innerHTML = `
                    <h3>${project.name}</h3>
                    <p>${project.description}</p>
                    <p>${styleBadge} <span class="badge">${project.project_type}</span></p>
                    <button class="analyze-demo-btn" data-project="${project.name}">Run Demo Analysis</button>
                `;
                
                demoProjectsList.appendChild(card);
                
                // Add event listener to the button
                const button = card.querySelector('.analyze-demo-btn');
                button.addEventListener('click', () => runDemoAnalysis(project.name));
            });
        }
        
        // Run analysis on a demo project
        async function runDemoAnalysis(projectName) {
            try {
                showStatus(`Starting demo analysis for ${projectName}...`, 'info');
                
                const response = await fetch('/api/run-demo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ project_name: projectName })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentJobId = data.job_id;
                    showStatus(`Demo analysis started: ${data.message}`, 'info');
                    
                    // Start checking status
                    if (statusCheckInterval) {
                        clearInterval(statusCheckInterval);
                    }
                    statusCheckInterval = setInterval(checkAnalysisStatus, 2000);
                } else {
                    showStatus(`Failed to start demo analysis: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error starting demo analysis:', error);
            }
        }
        
        // Generate a shareable report from a visualization
        async function generateReport(filename) {
            try {
                showStatus(`Generating report for ${filename}...`, 'info');
                
                const response = await fetch('/api/generate-report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ file: filename })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentJobId = data.job_id;
                    showStatus(`Report generation started`, 'info');
                    
                    // Start checking status
                    if (statusCheckInterval) {
                        clearInterval(statusCheckInterval);
                    }
                    statusCheckInterval = setInterval(checkReportStatus, 2000);
                } else {
                    showStatus(`Failed to generate report: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error generating report:', error);
            }
        }
        
        // Check the status of a running report generation
        async function checkReportStatus() {
            if (!currentJobId) return;
            
            try {
                const response = await fetch('/api/status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ job_id: currentJobId })
                });
                
                const data = await response.json();
                
                // Update status display
                if (data.status === 'completed') {
                    showStatus(`Report generated successfully! Available at: ${data.bundle_path}`, 'success');
                    clearInterval(statusCheckInterval);
                    currentJobId = null;
                } else if (data.status === 'failed') {
                    showStatus(`Report generation failed: ${data.message || 'Unknown error'}`, 'error');
                    clearInterval(statusCheckInterval);
                    currentJobId = null;
                } else if (data.status === 'running') {
                    showStatus(`Report generation in progress...`, 'info');
                }
            } catch (error) {
                showStatus(`Error checking report status: ${error.message}`, 'error');
                console.error('Error checking report status:', error);
            }
        }
        
        // Check the status of a running analysis
        async function checkAnalysisStatus() {
            if (!currentJobId) return;
            
            try {
                const response = await fetch('/api/status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ job_id: currentJobId })
                });
                
                const data = await response.json();
                
                // Update status display
                if (data.status === 'completed') {
                    showStatus(`Analysis completed successfully!`, 'success');
                    clearInterval(statusCheckInterval);
                    currentJobId = null;
                    
                    // Refresh visualizations list
                    fetchVisualizations();
                } else if (data.status === 'failed') {
                    showStatus(`Analysis failed: ${data.message || 'Unknown error'}`, 'error');
                    clearInterval(statusCheckInterval);
                    currentJobId = null;
                } else if (data.status === 'running') {
                    showStatus(`Analysis in progress...`, 'info');
                }
            } catch (error) {
                showStatus(`Error checking status: ${error.message}`, 'error');
                console.error('Error checking analysis status:', error);
            }
        }
        
        // Fetch available visualizations
        async function fetchVisualizations() {
            try {
                const response = await fetch('/api/list-visualizations', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayVisualizations(data.visualizations);
                } else {
                    console.error('Failed to fetch visualizations:', data.message);
                }
            } catch (error) {
                console.error('Error fetching visualizations:', error);
            }
        }
        
        // Display visualizations in the UI
        function displayVisualizations(visualizations) {
            visualizationsList.innerHTML = '';
            
            if (visualizations.length === 0) {
                visualizationsList.innerHTML = '<p>No visualizations available. Run an analysis to generate visualizations.</p>';
                return;
            }
            
            visualizations.forEach(viz => {
                const card = document.createElement('div');
                card.className = 'card';
                
                // Format date
                const date = new Date(viz.modified * 1000);
                const formattedDate = date.toLocaleString();
                
                // Format file size
                const sizeInKB = Math.round(viz.size / 1024);
                const formattedSize = sizeInKB > 1024 
                    ? `${(sizeInKB / 1024).toFixed(1)} MB` 
                    : `${sizeInKB} KB`;
                
                card.innerHTML = `
                    <h3>${viz.filename}</h3>
                    <p>Size: ${formattedSize}</p>
                    <p class="timestamp">Created: ${formattedDate}</p>
                    <div class="action-buttons">
                        <button class="visualize-btn" data-file="${viz.filename}">Open Visualization</button>
                        <button class="report-btn" data-file="${viz.filename}">Generate Report</button>
                    </div>
                `;
                
                visualizationsList.appendChild(card);
                
                // Add event listeners to the buttons
                const openButton = card.querySelector('.visualize-btn');
                openButton.addEventListener('click', () => openVisualization(viz.filename));
                
                const reportButton = card.querySelector('.report-btn');
                reportButton.addEventListener('click', () => generateReport(viz.filename));
            });
        }
        
        // Open a visualization
        async function openVisualization(filename) {
            try {
                const response = await fetch('/api/visualize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ file: filename })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showStatus(`Opening visualization: ${filename}`, 'success');
                } else {
                    showStatus(`Failed to open visualization: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error opening visualization:', error);
            }
        }
        
        // Show status message
        function showStatus(message, type) {
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }
    </script>
</body>
</html>
""")
    
    return dashboard_path

def start_server(host="localhost", port=8080):
    """Start the HTTP server."""
    try:
        # Create a simple dashboard if the React app is not built
        dashboard_path = create_simple_dashboard()
        
        # Change to the directory where the dashboard is located
        os.chdir(str(dashboard_path.parent))
        
        # Create and configure the server
        server = ThreadedHTTPServer((host, port), CodePatternAnalyzerAPI)
        
        logger.info(f"Starting server at http://{host}:{port}")
        
        # Open browser
        webbrowser.open(f"http://{host}:{port}/dashboard.html")
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Shutting down server...")
            server.shutdown()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start the server
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        return 1
        
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Code Pattern Analyzer - Unified GUI"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to run the server on (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the server on (default: 8080)"
    )
    
    args = parser.parse_args()
    
    # Start the server
    return start_server(args.host, args.port)

if __name__ == "__main__":
    sys.exit(main())