#!/usr/bin/env python3
"""
Interactive Pattern Transformation GUI

This script provides a web-based interface for transforming code to apply design patterns.
It allows users to:
- Analyze code for pattern opportunities
- Select which patterns to apply
- Preview and customize the transformations
- Apply the transformations to the code

Usage:
    python pattern_transformation_gui.py
"""

import os
import sys
import logging
import argparse
import json
import threading
import time
import difflib
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import pattern detection and transformation modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommendation_detector import detect_pattern_opportunities, DETECTORS
from pattern_transformer import transform_file, create_transformer

# Path constants
ROOT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "tmp"
STATIC_DIR = ROOT_DIR / "web_ui" / "static"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

class PatternTransformationHandler(SimpleHTTPRequestHandler):
    """Handler for Pattern Transformation API requests."""
    
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
        elif self.path == '/api/preview-transformation':
            self.handle_preview_transformation()
        elif self.path == '/api/apply-transformation':
            self.handle_apply_transformation()
        elif self.path == '/api/list-patterns':
            self.handle_list_patterns_request()
        elif self.path == '/api/status':
            self.handle_status_request()
        elif self.path == '/api/list-transformations':
            self.handle_list_transformations_request()
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_analyze_request(self):
        """Handle request to analyze code for pattern opportunities."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        target = request_data.get('target')
        content = request_data.get('content')
        
        if not target and not content:
            self.send_error(400, "Missing target or content parameter")
            return
        
        # Create temporary file if content is provided
        temp_file = None
        if content:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
                f.write(content.encode('utf-8'))
                temp_file = f.name
                target = temp_file
        
        # Run analysis in background
        job_id = str(int(time.time()))
        result = {
            'status': 'started',
            'message': f'Pattern analysis started',
            'job_id': job_id,
        }
        
        threading.Thread(
            target=self._run_analysis,
            args=(target, job_id, temp_file)
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def _run_analysis(self, target, job_id, temp_file=None):
        """Run pattern opportunity analysis in background."""
        try:
            logger.info(f"Starting pattern analysis of {target}")
            
            # Analyze target
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
                    'message': 'Pattern analysis completed successfully',
                    'target': target,
                    'opportunities': grouped_opportunities,
                    'job_id': job_id,
                    'temp_file': temp_file,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"Pattern analysis completed with {len(opportunities)} opportunities found")
            
        except Exception as e:
            logger.error(f"Error running pattern analysis: {str(e)}")
            # Save error status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'failed',
                    'message': f'Error running pattern analysis: {str(e)}',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
            
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def handle_preview_transformation(self):
        """Handle request to preview a pattern transformation."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        job_id = request_data.get('job_id')
        pattern = request_data.get('pattern')
        
        if not job_id or not pattern:
            self.send_error(400, "Missing job_id or pattern parameter")
            return
        
        # Get the analysis status file
        status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
        if not os.path.exists(status_file):
            self.send_error(404, "Analysis not found")
            return
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        if status['status'] != 'completed':
            self.send_error(400, "Analysis not completed")
            return
        
        target = status['target']
        opportunities = status.get('opportunities', {}).get(pattern, [])
        
        if not opportunities:
            self.send_error(400, f"No {pattern} opportunities found in analysis")
            return
        
        # Run preview in background
        preview_job_id = f"{job_id}_{pattern}"
        result = {
            'status': 'started',
            'message': f'Transformation preview started',
            'preview_job_id': preview_job_id,
        }
        
        threading.Thread(
            target=self._run_preview,
            args=(target, pattern, opportunities, preview_job_id, status.get('temp_file'))
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def _run_preview(self, target, pattern, opportunities, preview_job_id, temp_file=None):
        """Run pattern transformation preview in background."""
        try:
            logger.info(f"Starting {pattern} transformation preview for {target}")
            
            # Create transformer
            transformer = create_transformer(pattern, target, opportunities)
            
            # Transform the code
            transformed_code = transformer.transform()
            
            # Read original code
            with open(target, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Generate diff
            diff = difflib.unified_diff(
                original_code.splitlines(),
                transformed_code.splitlines(),
                fromfile='original',
                tofile='transformed',
                lineterm=''
            )
            
            # Save the result status
            status_file = os.path.join(TEMP_DIR, f"preview_{preview_job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'completed',
                    'message': f'{pattern} transformation preview completed',
                    'target': target,
                    'pattern': pattern,
                    'original_code': original_code,
                    'transformed_code': transformed_code,
                    'diff': list(diff),
                    'preview_job_id': preview_job_id,
                    'temp_file': temp_file,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"{pattern} transformation preview completed for {target}")
            
        except Exception as e:
            logger.error(f"Error generating transformation preview: {str(e)}")
            # Save error status
            status_file = os.path.join(TEMP_DIR, f"preview_{preview_job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'failed',
                    'message': f'Error generating transformation preview: {str(e)}',
                    'preview_job_id': preview_job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
    
    def handle_apply_transformation(self):
        """Handle request to apply a pattern transformation."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        preview_job_id = request_data.get('preview_job_id')
        custom_code = request_data.get('custom_code')  # Optional
        
        if not preview_job_id:
            self.send_error(400, "Missing preview_job_id parameter")
            return
        
        # Get the preview status file
        status_file = os.path.join(TEMP_DIR, f"preview_{preview_job_id}.json")
        if not os.path.exists(status_file):
            self.send_error(404, "Preview not found")
            return
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        if status['status'] != 'completed':
            self.send_error(400, "Preview not completed")
            return
        
        target = status['target']
        pattern = status['pattern']
        
        # Create output filename
        target_path = Path(target)
        stem = target_path.stem
        suffix = target_path.suffix
        output_path = os.path.join(OUTPUT_DIR, f"{stem}_{pattern.lower().replace(' ', '_')}_transformed{suffix}")
        
        # Apply transformation (use custom code if provided)
        code_to_save = custom_code if custom_code is not None else status['transformed_code']
        
        # Save the transformed code
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code_to_save)
        
        # Create transformation record
        transformation_id = str(int(time.time()))
        record_file = os.path.join(TEMP_DIR, f"transformation_{transformation_id}.json")
        with open(record_file, 'w') as f:
            record = {
                'transformation_id': transformation_id,
                'target': target,
                'pattern': pattern,
                'output_path': output_path,
                'timestamp': time.time()
            }
            json.dump(record, f)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'message': f'Transformation applied successfully',
            'transformation_id': transformation_id,
            'output_path': output_path
        }).encode())
    
    def handle_list_patterns_request(self):
        """Handle request to list available pattern detectors."""
        patterns = []
        
        for pattern_name, detector in DETECTORS.items():
            patterns.append({
                'name': pattern_name,
                'description': detector['description'],
                'benefits': detector['benefits']
            })
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'patterns': patterns
        }).encode())
    
    def handle_status_request(self):
        """Handle request for job status."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        job_id = request_data.get('job_id')
        preview_job_id = request_data.get('preview_job_id')
        
        if not job_id and not preview_job_id:
            self.send_error(400, "Missing job_id or preview_job_id parameter")
            return
        
        status_file = None
        if job_id:
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
        elif preview_job_id:
            status_file = os.path.join(TEMP_DIR, f"preview_{preview_job_id}.json")
        
        if not os.path.exists(status_file):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'running',
                'message': 'Job is still running'
            }).encode())
            return
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def handle_list_transformations_request(self):
        """Handle request to list applied transformations."""
        transformations = []
        
        # Look for transformation record files
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

def create_dashboard_html():
    """Create the Pattern Transformation dashboard HTML."""
    dashboard_path = STATIC_DIR / "pattern_transformation.html"
    
    if dashboard_path.exists():
        return dashboard_path
        
    with open(dashboard_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Pattern Transformation</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f9fafc;
        }
        
        h1, h2, h3, h4 {
            color: #2c3e50;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }
        
        h1 {
            text-align: center;
            padding: 20px 0;
            margin-top: 0;
            background-color: #2c3e50;
            color: white;
        }
        
        /* Container styles */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
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
        
        /* Main layout */
        .main-layout {
            display: flex;
            gap: 20px;
        }
        
        .sidebar {
            flex: 0 0 300px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
        }
        
        .main-content {
            flex: 1;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
        }
        
        /* Form elements */
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        input[type="text"],
        select,
        textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        textarea {
            min-height: 150px;
            font-family: monospace;
        }
        
        button {
            padding: 10px 15px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        
        button:hover {
            background-color: #2980b9;
        }
        
        button.secondary {
            background-color: #95a5a6;
        }
        
        button.secondary:hover {
            background-color: #7f8c8d;
        }
        
        button.success {
            background-color: #2ecc71;
        }
        
        button.success:hover {
            background-color: #27ae60;
        }
        
        button.danger {
            background-color: #e74c3c;
        }
        
        button.danger:hover {
            background-color: #c0392b;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 10px 15px;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: bold;
        }
        
        .tab.active {
            border-bottom-color: #3498db;
            color: #3498db;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Status message */
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        
        .status.info {
            background-color: #d9edf7;
            color: #31708f;
            border: 1px solid #bce8f1;
        }
        
        .status.success {
            background-color: #dff0d8;
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        
        .status.error {
            background-color: #f2dede;
            color: #a94442;
            border: 1px solid #ebccd1;
        }
        
        /* Pattern cards */
        .pattern-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        
        .pattern-card {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            transition: transform 0.2s;
            cursor: pointer;
        }
        
        .pattern-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .pattern-card.selected {
            border-color: #3498db;
            background-color: #ebf5fb;
        }
        
        .pattern-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .pattern-description {
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .pattern-benefits {
            font-size: 0.8em;
        }
        
        .pattern-benefits ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        
        /* Code preview */
        .code-preview {
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }
        
        .code-panel {
            flex: 1;
        }
        
        .code-header {
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .code-container {
            height: 400px;
            overflow: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            white-space: pre;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .diff-line-add {
            background-color: #e6ffed;
            color: #22863a;
        }
        
        .diff-line-remove {
            background-color: #ffeef0;
            color: #cb2431;
        }
        
        .diff-line-context {
            color: #666;
        }
        
        /* Transformations list */
        .transformations-list {
            margin-top: 20px;
        }
        
        .transformation-card {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        
        .transformation-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .transformation-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        /* Loader */
        .loader {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-left: 10px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Media queries */
        @media (max-width: 768px) {
            .main-layout {
                flex-direction: column;
            }
            
            .sidebar {
                flex: none;
                width: 100%;
            }
            
            .code-preview {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <h1>Interactive Pattern Transformation</h1>
    
    <div class="container">
        <div class="header">
            <div class="logo">Design Pattern Transformer</div>
        </div>
        
        <div class="main-layout">
            <div class="sidebar">
                <div class="tabs">
                    <div class="tab active" data-tab="analyze">Analyze Code</div>
                    <div class="tab" data-tab="transformations">Transformations</div>
                </div>
                
                <div id="analyzeTab" class="tab-content active">
                    <h2>Analyze for Patterns</h2>
                    <form id="analyzeForm">
                        <div class="form-group">
                            <label for="targetInput">File Path:</label>
                            <input type="text" id="targetInput" placeholder="/path/to/file.py">
                        </div>
                        
                        <div class="form-group">
                            <label for="codeInput">Or Paste Code:</label>
                            <textarea id="codeInput" placeholder="Paste your code here..."></textarea>
                        </div>
                        
                        <button type="submit">Analyze Code</button>
                    </form>
                </div>
                
                <div id="transformationsTab" class="tab-content">
                    <h2>Applied Transformations</h2>
                    <div id="transformationsList">
                        <p>Loading transformations...</p>
                    </div>
                    
                    <button id="refreshTransformationsBtn" class="secondary">Refresh List</button>
                </div>
                
                <div class="status" id="status"></div>
            </div>
            
            <div class="main-content">
                <div id="analysisResults" style="display: none;">
                    <h2>Pattern Opportunities</h2>
                    <p>Select a pattern to preview transformation:</p>
                    
                    <div class="pattern-cards" id="patternCards"></div>
                </div>
                
                <div id="transformationPreview" style="display: none;">
                    <h2>Transformation Preview</h2>
                    <div class="transformation-header">
                        <button id="backToPatterns" class="secondary">← Back to Patterns</button>
                        <button id="applyTransformation" class="success">Apply Transformation</button>
                    </div>
                    
                    <div class="code-preview">
                        <div class="code-panel">
                            <div class="code-header">Original Code</div>
                            <div class="code-container" id="originalCode"></div>
                        </div>
                        
                        <div class="code-panel">
                            <div class="code-header">
                                Transformed Code
                                <button id="editTransformation" class="secondary" style="float: right; padding: 2px 8px;">Edit</button>
                            </div>
                            <div class="code-container" id="transformedCode"></div>
                            <textarea id="editableCode" style="display: none; height: 400px;"></textarea>
                        </div>
                    </div>
                    
                    <div class="diff-view" style="margin-top: 20px;">
                        <div class="code-header">Diff View</div>
                        <div class="code-container" id="diffView"></div>
                    </div>
                </div>
                
                <div id="noResults" style="display: none;">
                    <h2>No Pattern Opportunities Found</h2>
                    <p>No pattern opportunities were detected in the provided code. Try analyzing a different file or check that your code contains patterns that can be detected.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // DOM elements
        const analyzeForm = document.getElementById('analyzeForm');
        const targetInput = document.getElementById('targetInput');
        const codeInput = document.getElementById('codeInput');
        const statusDiv = document.getElementById('status');
        const analysisResults = document.getElementById('analysisResults');
        const patternCards = document.getElementById('patternCards');
        const transformationPreview = document.getElementById('transformationPreview');
        const noResults = document.getElementById('noResults');
        const originalCode = document.getElementById('originalCode');
        const transformedCode = document.getElementById('transformedCode');
        const editableCode = document.getElementById('editableCode');
        const diffView = document.getElementById('diffView');
        const backToPatterns = document.getElementById('backToPatterns');
        const applyTransformation = document.getElementById('applyTransformation');
        const editTransformation = document.getElementById('editTransformation');
        const transformationsList = document.getElementById('transformationsList');
        const refreshTransformationsBtn = document.getElementById('refreshTransformationsBtn');
        
        // Tab functionality
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById(tab.getAttribute('data-tab') + 'Tab').classList.add('active');
                
                // Load transformations if switching to that tab
                if (tab.getAttribute('data-tab') === 'transformations') {
                    fetchTransformations();
                }
            });
        });
        
        // Current job state
        let currentJobId = null;
        let currentPreviewJobId = null;
        let statusCheckInterval = null;
        let previewCheckInterval = null;
        let availablePatterns = {};
        let selectedPattern = null;
        let isEditMode = false;
        
        // Event listeners
        analyzeForm.addEventListener('submit', handleAnalyzeSubmit);
        backToPatterns.addEventListener('click', showPatternCards);
        applyTransformation.addEventListener('click', handleApplyTransformation);
        editTransformation.addEventListener('click', toggleEditMode);
        refreshTransformationsBtn.addEventListener('click', fetchTransformations);
        
        // Fetch available patterns on load
        fetchPatterns();
        
        // Functions
        
        // Fetch available patterns
        async function fetchPatterns() {
            try {
                const response = await fetch('/api/list-patterns', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Store patterns data
                    data.patterns.forEach(pattern => {
                        availablePatterns[pattern.name] = pattern;
                    });
                }
            } catch (error) {
                console.error('Error fetching patterns:', error);
            }
        }
        
        // Handle analyze form submission
        async function handleAnalyzeSubmit(event) {
            event.preventDefault();
            
            const target = targetInput.value.trim();
            const code = codeInput.value.trim();
            
            if (!target && !code) {
                showStatus('Please enter a file path or paste code', 'error');
                return;
            }
            
            try {
                showStatus('Starting pattern analysis...', 'info');
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        target: target || null,
                        content: code || null
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentJobId = data.job_id;
                    showStatus(`Analysis started <span id="statusLoader" class="loader"></span>`, 'info');
                    
                    // Hide results while analyzing
                    analysisResults.style.display = 'none';
                    transformationPreview.style.display = 'none';
                    noResults.style.display = 'none';
                    
                    // Start checking status
                    if (statusCheckInterval) {
                        clearInterval(statusCheckInterval);
                    }
                    statusCheckInterval = setInterval(checkAnalysisStatus, 1000);
                } else {
                    showStatus(`Failed to start analysis: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error starting analysis:', error);
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
                    
                    // Display results
                    displayAnalysisResults(data);
                } else if (data.status === 'failed') {
                    showStatus(`Analysis failed: ${data.message || 'Unknown error'}`, 'error');
                    clearInterval(statusCheckInterval);
                    currentJobId = null;
                } else if (data.status === 'running') {
                    // Status already shown
                }
            } catch (error) {
                showStatus(`Error checking status: ${error.message}`, 'error');
                console.error('Error checking analysis status:', error);
            }
        }
        
        // Display analysis results
        function displayAnalysisResults(data) {
            const opportunities = data.opportunities || {};
            const patternNames = Object.keys(opportunities);
            
            if (patternNames.length === 0) {
                // No opportunities found
                noResults.style.display = 'block';
                analysisResults.style.display = 'none';
                transformationPreview.style.display = 'none';
                return;
            }
            
            // Clear pattern cards
            patternCards.innerHTML = '';
            
            // Create a card for each pattern
            patternNames.forEach(patternName => {
                const patternData = availablePatterns[patternName] || {
                    name: patternName,
                    description: 'A design pattern',
                    benefits: []
                };
                
                const card = document.createElement('div');
                card.className = 'pattern-card';
                card.dataset.pattern = patternName;
                
                // Add pattern details
                card.innerHTML = `
                    <div class="pattern-name">${patternName} Pattern</div>
                    <div class="pattern-description">${patternData.description}</div>
                    <div class="pattern-benefits">
                        <strong>Benefits:</strong>
                        <ul>
                            ${patternData.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="pattern-count">
                        ${opportunities[patternName].length} opportunities detected
                    </div>
                `;
                
                // Add click handler
                card.addEventListener('click', () => {
                    selectPattern(patternName);
                });
                
                patternCards.appendChild(card);
            });
            
            // Show results
            analysisResults.style.display = 'block';
            transformationPreview.style.display = 'none';
            noResults.style.display = 'none';
        }
        
        // Select a pattern for transformation
        async function selectPattern(patternName) {
            selectedPattern = patternName;
            
            // Highlight the selected card
            document.querySelectorAll('.pattern-card').forEach(card => {
                if (card.dataset.pattern === patternName) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            });
            
            // Request transformation preview
            try {
                showStatus(`Generating ${patternName} transformation preview...`, 'info');
                
                const response = await fetch('/api/preview-transformation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        job_id: currentJobId,
                        pattern: patternName
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentPreviewJobId = data.preview_job_id;
                    
                    // Start checking preview status
                    if (previewCheckInterval) {
                        clearInterval(previewCheckInterval);
                    }
                    previewCheckInterval = setInterval(checkPreviewStatus, 1000);
                } else {
                    showStatus(`Failed to generate preview: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error generating preview:', error);
            }
        }
        
        // Check the status of a transformation preview
        async function checkPreviewStatus() {
            if (!currentPreviewJobId) return;
            
            try {
                const response = await fetch('/api/status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ preview_job_id: currentPreviewJobId })
                });
                
                const data = await response.json();
                
                // Update status display
                if (data.status === 'completed') {
                    showStatus(`Transformation preview generated successfully!`, 'success');
                    clearInterval(previewCheckInterval);
                    
                    // Display preview
                    displayTransformationPreview(data);
                } else if (data.status === 'failed') {
                    showStatus(`Preview generation failed: ${data.message || 'Unknown error'}`, 'error');
                    clearInterval(previewCheckInterval);
                    currentPreviewJobId = null;
                } else if (data.status === 'running') {
                    // Status already shown
                }
            } catch (error) {
                showStatus(`Error checking preview status: ${error.message}`, 'error');
                console.error('Error checking preview status:', error);
            }
        }
        
        // Display transformation preview
        function displayTransformationPreview(data) {
            // Display the original and transformed code
            originalCode.textContent = data.original_code;
            transformedCode.textContent = data.transformed_code;
            editableCode.value = data.transformed_code;
            
            // Format the diff
            diffView.innerHTML = '';
            data.diff.forEach(line => {
                const diffLine = document.createElement('div');
                
                if (line.startsWith('+')) {
                    diffLine.className = 'diff-line-add';
                } else if (line.startsWith('-')) {
                    diffLine.className = 'diff-line-remove';
                } else {
                    diffLine.className = 'diff-line-context';
                }
                
                diffLine.textContent = line;
                diffView.appendChild(diffLine);
            });
            
            // Reset edit mode
            isEditMode = false;
            editableCode.style.display = 'none';
            transformedCode.style.display = 'block';
            editTransformation.textContent = 'Edit';
            
            // Show the preview
            analysisResults.style.display = 'none';
            transformationPreview.style.display = 'block';
            noResults.style.display = 'none';
        }
        
        // Show pattern cards (go back from preview)
        function showPatternCards() {
            analysisResults.style.display = 'block';
            transformationPreview.style.display = 'none';
            noResults.style.display = 'none';
        }
        
        // Toggle edit mode for transformed code
        function toggleEditMode() {
            isEditMode = !isEditMode;
            
            if (isEditMode) {
                // Switch to edit mode
                transformedCode.style.display = 'none';
                editableCode.style.display = 'block';
                editTransformation.textContent = 'Preview';
            } else {
                // Switch to preview mode
                transformedCode.style.display = 'block';
                editableCode.style.display = 'none';
                editTransformation.textContent = 'Edit';
                
                // Update preview code
                transformedCode.textContent = editableCode.value;
            }
        }
        
        // Apply the transformation
        async function handleApplyTransformation() {
            if (!currentPreviewJobId) {
                showStatus('No transformation preview available', 'error');
                return;
            }
            
            try {
                showStatus('Applying transformation...', 'info');
                
                const response = await fetch('/api/apply-transformation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        preview_job_id: currentPreviewJobId,
                        custom_code: isEditMode ? editableCode.value : null
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showStatus(`Transformation applied successfully! Saved to ${data.output_path}`, 'success');
                    
                    // Refresh transformations list
                    fetchTransformations();
                } else {
                    showStatus(`Failed to apply transformation: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error applying transformation:', error);
            }
        }
        
        // Fetch applied transformations
        async function fetchTransformations() {
            try {
                transformationsList.innerHTML = '<p>Loading transformations...</p>';
                
                const response = await fetch('/api/list-transformations', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayTransformations(data.transformations);
                } else {
                    transformationsList.innerHTML = '<p>Failed to load transformations.</p>';
                }
            } catch (error) {
                console.error('Error fetching transformations:', error);
                transformationsList.innerHTML = '<p>Error loading transformations.</p>';
            }
        }
        
        // Display applied transformations
        function displayTransformations(transformations) {
            transformationsList.innerHTML = '';
            
            if (transformations.length === 0) {
                transformationsList.innerHTML = '<p>No transformations have been applied yet.</p>';
                return;
            }
            
            transformations.forEach(transformation => {
                const card = document.createElement('div');
                card.className = 'transformation-card';
                
                // Format date
                const date = new Date(transformation.timestamp * 1000);
                const formattedDate = date.toLocaleString();
                
                // Create transformation item
                card.innerHTML = `
                    <div class="transformation-title">
                        ${transformation.pattern} Pattern
                    </div>
                    <div class="transformation-meta">
                        Applied on ${formattedDate}
                    </div>
                    <div>
                        <div><strong>Source:</strong> ${transformation.target}</div>
                        <div><strong>Output:</strong> ${transformation.output_path}</div>
                    </div>
                `;
                
                transformationsList.appendChild(card);
            });
        }
        
        // Show status message
        function showStatus(message, type) {
            statusDiv.innerHTML = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }
    </script>
</body>
</html>
""")
    
    return dashboard_path

def start_server(host="localhost", port=8082):
    """Start the HTTP server."""
    try:
        # Create the dashboard HTML
        dashboard_path = create_dashboard_html()
        
        # Change to the directory where the dashboard is located
        os.chdir(str(dashboard_path.parent))
        
        # Create and configure the server
        server = ThreadedHTTPServer((host, port), PatternTransformationHandler)
        
        logger.info(f"Starting Pattern Transformation Server at http://{host}:{port}")
        
        # Open browser
        webbrowser.open(f"http://{host}:{port}/pattern_transformation.html")
        
        # Handle graceful shutdown
        import signal
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
        description="Interactive Pattern Transformation GUI"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to run the server on (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8082,
        help="Port to run the server on (default: 8082)"
    )
    
    args = parser.parse_args()
    
    # Start the server
    return start_server(args.host, args.port)

if __name__ == "__main__":
    sys.exit(main())