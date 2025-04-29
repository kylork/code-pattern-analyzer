#!/usr/bin/env python3
"""
Pattern Recommendation GUI

This script provides a web-based interface for the Pattern Recommendation System.
It allows users to analyze code files or directories to receive design pattern
recommendations with implementation guidance.

Usage:
    python pattern_recommendation_gui.py
"""

import os
import sys
import logging
import argparse
import json
import threading
import time
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import Pattern Recommendation System
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.pattern_recommendation import (
    detect_opportunities,
    analyze_directory_for_opportunities,
    PatternOpportunity,
    OPPORTUNITY_DETECTORS
)

# Path constants
ROOT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "tmp"
STATIC_DIR = ROOT_DIR / "web_ui" / "static"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

class PatternRecommendationHandler(SimpleHTTPRequestHandler):
    """Handler for Pattern Recommendation API requests."""
    
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
        elif self.path == '/api/list-patterns':
            self.handle_list_patterns_request()
        elif self.path == '/api/status':
            self.handle_status_request()
        elif self.path == '/api/list-reports':
            self.handle_list_reports_request()
        elif self.path == '/api/view-report':
            self.handle_view_report_request()
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_analyze_request(self):
        """Handle request to analyze code for pattern opportunities."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        target = request_data.get('target')
        patterns = request_data.get('patterns', [])  # Optional list of patterns to check
        
        if not target:
            self.send_error(400, "Missing target parameter")
            return
        
        # Run analysis in background
        job_id = str(int(time.time()))
        result = {
            'status': 'started',
            'message': f'Pattern analysis started for {target}',
            'job_id': job_id,
        }
        
        threading.Thread(
            target=self._run_analysis,
            args=(target, patterns, job_id)
        ).start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def _run_analysis(self, target, patterns, job_id):
        """Run pattern recommendation analysis in background."""
        try:
            logger.info(f"Starting pattern analysis of {target}")
            
            # Generate output filenames
            json_output = os.path.join(OUTPUT_DIR, f"pattern_recommendations_{job_id}.json")
            html_output = os.path.join(OUTPUT_DIR, f"pattern_recommendations_{job_id}.html")
            
            # Analyze target
            if os.path.isfile(target):
                opportunities = {target: detect_opportunities(target)}
            else:
                opportunities = analyze_directory_for_opportunities(target)
            
            # Filter by requested patterns if specified
            if patterns:
                filtered_opportunities = {}
                for file_path, file_opps in opportunities.items():
                    filtered_file_opps = [opp for opp in file_opps if opp.pattern_name in patterns]
                    if filtered_file_opps:
                        filtered_opportunities[file_path] = filtered_file_opps
                opportunities = filtered_opportunities
            
            # Save results as JSON
            serializable_results = {}
            for file_path, file_opportunities in opportunities.items():
                serializable_results[file_path] = [opp.to_dict() for opp in file_opportunities]
            
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2)
            
            # Generate HTML report
            from src.pattern_recommendation import generate_html_report
            generate_html_report(opportunities, html_output)
            
            # Save the result status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'completed',
                    'message': 'Pattern analysis completed successfully',
                    'target': target,
                    'json_output': os.path.basename(json_output),
                    'html_output': os.path.basename(html_output),
                    'opportunity_count': sum(len(opps) for opps in opportunities.values()),
                    'file_count': len(opportunities),
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"Pattern analysis completed with {status['opportunity_count']} opportunities found")
            
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
    
    def handle_list_patterns_request(self):
        """Handle request to list available pattern detectors."""
        patterns = []
        
        for detector in OPPORTUNITY_DETECTORS:
            patterns.append({
                'name': detector.pattern_name,
                'languages': detector.languages,
                'benefits': detector.get_benefits()
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
                'message': 'Pattern analysis is still running'
            }).encode())
            return
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def handle_list_reports_request(self):
        """Handle request to list available pattern recommendation reports."""
        reports = []
        
        # Get all HTML reports in the output directory
        for file in os.listdir(OUTPUT_DIR):
            if file.startswith('pattern_recommendations_') and file.endswith('.html'):
                file_path = os.path.join(OUTPUT_DIR, file)
                # Try to find corresponding status file to get metadata
                job_id = file.replace('pattern_recommendations_', '').replace('.html', '')
                status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
                
                report_info = {
                    'filename': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': os.path.getmtime(file_path),
                    'job_id': job_id
                }
                
                # Add metadata if available
                if os.path.exists(status_file):
                    with open(status_file, 'r') as f:
                        status = json.load(f)
                        report_info.update({
                            'target': status.get('target', 'Unknown'),
                            'opportunity_count': status.get('opportunity_count', 0),
                            'file_count': status.get('file_count', 0)
                        })
                
                reports.append(report_info)
        
        # Sort by modification time (newest first)
        reports.sort(key=lambda x: x['modified'], reverse=True)
        
        # Return the list
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'reports': reports
        }).encode())
    
    def handle_view_report_request(self):
        """Handle request to view a pattern recommendation report."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        filename = request_data.get('filename')
        if not filename:
            self.send_error(400, "Missing filename parameter")
            return
        
        # Construct full path
        full_path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(full_path):
            self.send_error(404, "Report file not found")
            return
        
        # Open the report in the browser
        webbrowser.open(f"file://{full_path}")
        
        # Return success
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'message': f'Opening report: {filename}'
        }).encode())

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

def create_dashboard_html():
    """Create the Pattern Recommendation dashboard HTML."""
    dashboard_path = STATIC_DIR / "pattern_recommendation.html"
    
    if dashboard_path.exists():
        return dashboard_path
        
    with open(dashboard_path, 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Recommendation System</title>
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
            max-width: 1200px;
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
        select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
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
        
        /* Pattern checkboxes */
        .patterns-container {
            margin-top: 15px;
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
        }
        
        .pattern-checkbox {
            margin-bottom: 8px;
        }
        
        /* Reports */
        .reports-list {
            margin-top: 20px;
        }
        
        .report-card {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            transition: transform 0.2s;
            cursor: pointer;
        }
        
        .report-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .report-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .report-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .report-stats {
            display: flex;
            gap: 15px;
        }
        
        .report-stat {
            background-color: #f8f9fa;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.9em;
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
    </style>
</head>
<body>
    <h1>Pattern Recommendation System</h1>
    
    <div class="container">
        <div class="header">
            <div class="logo">Design Pattern Recommendations</div>
        </div>
        
        <div class="main-layout">
            <div class="sidebar">
                <h2>Analyze Code</h2>
                <form id="analyzeForm">
                    <div class="form-group">
                        <label for="target">Code Path:</label>
                        <input type="text" id="target" placeholder="/path/to/code" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Available Patterns:</label>
                        <div class="patterns-container" id="patternsContainer">
                            <p>Loading available patterns...</p>
                        </div>
                    </div>
                    
                    <button type="submit">Analyze for Patterns</button>
                </form>
                
                <div class="status" id="status"></div>
            </div>
            
            <div class="main-content">
                <h2>Pattern Recommendation Reports</h2>
                <div class="reports-list" id="reportsList">
                    <p>Loading reports...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // DOM elements
        const analyzeForm = document.getElementById('analyzeForm');
        const targetInput = document.getElementById('target');
        const patternsContainer = document.getElementById('patternsContainer');
        const statusDiv = document.getElementById('status');
        const reportsList = document.getElementById('reportsList');
        
        // Current job ID
        let currentJobId = null;
        let statusCheckInterval = null;
        
        // On page load
        document.addEventListener('DOMContentLoaded', () => {
            // Fetch available patterns
            fetchPatterns();
            
            // Fetch existing reports
            fetchReports();
            
            // Setup form submission
            analyzeForm.addEventListener('submit', handleAnalyzeSubmit);
        });
        
        // Fetch available pattern detectors
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
                    displayPatterns(data.patterns);
                } else {
                    patternsContainer.innerHTML = '<p>Failed to load patterns.</p>';
                }
            } catch (error) {
                console.error('Error fetching patterns:', error);
                patternsContainer.innerHTML = '<p>Error loading patterns.</p>';
            }
        }
        
        // Display available patterns
        function displayPatterns(patterns) {
            patternsContainer.innerHTML = '';
            
            if (patterns.length === 0) {
                patternsContainer.innerHTML = '<p>No pattern detectors available.</p>';
                return;
            }
            
            // Create a checkbox for each pattern
            patterns.forEach((pattern, index) => {
                const checkboxDiv = document.createElement('div');
                checkboxDiv.className = 'pattern-checkbox';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `pattern-${index}`;
                checkbox.name = 'patterns';
                checkbox.value = pattern.name;
                checkbox.checked = true;  // Default to checked
                
                const label = document.createElement('label');
                label.htmlFor = `pattern-${index}`;
                label.textContent = `${pattern.name} (${pattern.languages.join(', ')})`;
                
                checkboxDiv.appendChild(checkbox);
                checkboxDiv.appendChild(label);
                patternsContainer.appendChild(checkboxDiv);
            });
        }
        
        // Fetch existing reports
        async function fetchReports() {
            try {
                const response = await fetch('/api/list-reports', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayReports(data.reports);
                } else {
                    reportsList.innerHTML = '<p>Failed to load reports.</p>';
                }
            } catch (error) {
                console.error('Error fetching reports:', error);
                reportsList.innerHTML = '<p>Error loading reports.</p>';
            }
        }
        
        // Display reports
        function displayReports(reports) {
            reportsList.innerHTML = '';
            
            if (reports.length === 0) {
                reportsList.innerHTML = '<p>No reports available. Run an analysis to generate reports.</p>';
                return;
            }
            
            reports.forEach(report => {
                const reportCard = document.createElement('div');
                reportCard.className = 'report-card';
                reportCard.dataset.filename = report.filename;
                
                // Format date
                const date = new Date(report.modified * 1000);
                const formattedDate = date.toLocaleString();
                
                // Create report title
                const title = document.createElement('div');
                title.className = 'report-title';
                title.textContent = report.target || `Report ${report.job_id}`;
                
                // Create report metadata
                const meta = document.createElement('div');
                meta.className = 'report-meta';
                meta.textContent = `Generated on ${formattedDate}`;
                
                // Create report stats
                const stats = document.createElement('div');
                stats.className = 'report-stats';
                
                if (report.opportunity_count !== undefined) {
                    const opportunityStat = document.createElement('div');
                    opportunityStat.className = 'report-stat';
                    opportunityStat.textContent = `${report.opportunity_count} opportunities`;
                    stats.appendChild(opportunityStat);
                }
                
                if (report.file_count !== undefined) {
                    const fileStat = document.createElement('div');
                    fileStat.className = 'report-stat';
                    fileStat.textContent = `${report.file_count} files`;
                    stats.appendChild(fileStat);
                }
                
                // Create view button
                const viewButton = document.createElement('button');
                viewButton.textContent = 'View Report';
                viewButton.style.marginTop = '10px';
                
                // Add all elements to the card
                reportCard.appendChild(title);
                reportCard.appendChild(meta);
                reportCard.appendChild(stats);
                reportCard.appendChild(viewButton);
                
                // Add click handler
                viewButton.addEventListener('click', () => {
                    viewReport(report.filename);
                });
                
                reportsList.appendChild(reportCard);
            });
        }
        
        // Handle analyze form submission
        async function handleAnalyzeSubmit(event) {
            event.preventDefault();
            
            const target = targetInput.value.trim();
            
            if (!target) {
                showStatus('Please enter a path to analyze', 'error');
                return;
            }
            
            // Get selected patterns
            const selectedPatterns = [];
            document.querySelectorAll('input[name="patterns"]:checked').forEach(checkbox => {
                selectedPatterns.push(checkbox.value);
            });
            
            try {
                showStatus('Starting pattern analysis...', 'info');
                
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        target,
                        patterns: selectedPatterns
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentJobId = data.job_id;
                    showStatus(`Analysis started for ${target} <span id="statusLoader" class="loader"></span>`, 'info');
                    
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
                    
                    // Refresh reports list
                    fetchReports();
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
        
        // View a report
        async function viewReport(filename) {
            try {
                const response = await fetch('/api/view-report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ filename })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showStatus(`Opening report: ${filename}`, 'success');
                } else {
                    showStatus(`Failed to open report: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error opening report:', error);
            }
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

def start_server(host="localhost", port=8081):
    """Start the HTTP server."""
    try:
        # Create the dashboard HTML
        dashboard_path = create_dashboard_html()
        
        # Change to the directory where the dashboard is located
        os.chdir(str(dashboard_path.parent))
        
        # Create and configure the server
        server = ThreadedHTTPServer((host, port), PatternRecommendationHandler)
        
        logger.info(f"Starting Pattern Recommendation Server at http://{host}:{port}")
        
        # Open browser
        webbrowser.open(f"http://{host}:{port}/pattern_recommendation.html")
        
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
        description="Pattern Recommendation System GUI"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to run the server on (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8081,
        help="Port to run the server on (default: 8081)"
    )
    
    args = parser.parse_args()
    
    # Start the server
    return start_server(args.host, args.port)

if __name__ == "__main__":
    sys.exit(main())