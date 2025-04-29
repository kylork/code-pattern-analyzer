#!/usr/bin/env python3
"""
Pattern Transformation Integration with Code Pattern Analyzer

This script integrates the Pattern Transformation functionality with the main
Code Pattern Analyzer GUI. It adds API endpoints to transform code patterns 
directly within the main application.

Usage:
    python integrate_pattern_transformation.py
"""

import os
import sys
import logging
import argparse
import json
import threading
import shutil
from pathlib import Path
import webbrowser
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Path constants
ROOT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "tmp"
STATIC_DIR = ROOT_DIR / "web_ui" / "static"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

def update_gui_api():
    """Update the GUI API with Pattern Transformation endpoints.
    
    This function adds the necessary API endpoints to the CodePatternAnalyzerAPI
    class in the code_pattern_analyzer_gui.py file.
    """
    gui_path = ROOT_DIR / "code_pattern_analyzer_gui.py"
    
    if not gui_path.exists():
        logger.error(f"GUI file not found at {gui_path}")
        return False
    
    # Read the GUI file
    with open(gui_path, 'r') as f:
        gui_code = f.read()
    
    # Check if the Pattern Transformation endpoints already exist
    if "def handle_pattern_transformation_request" in gui_code:
        logger.info("Pattern Transformation endpoints already exist in GUI")
        return True
    
    # Find the handle_api_request method to add our endpoints
    api_request_handler = """    def handle_api_request(self):
        \"\"\"Handle API requests.\"\"\"
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
            self.handle_generate_report_request()"""
    
    # Add our endpoints
    new_api_request_handler = """    def handle_api_request(self):
        \"\"\"Handle API requests.\"\"\"
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
            self.handle_transformations_list_request()"""
    
    # Replace the handler method with our updated version
    updated_gui_code = gui_code.replace(api_request_handler, new_api_request_handler)
    
    # Add our new handler methods before the class definition ends
    pattern_handlers = """
    def handle_pattern_transformation_request(self):
        \"\"\"Handle request to open the pattern transformation interface.\"\"\"
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
        \"\"\"Handle request to detect pattern opportunities in a file.\"\"\"
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
        \"\"\"Detect pattern opportunities in the background.\"\"\"
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
        \"\"\"Handle request to list applied transformations.\"\"\"
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
"""
    
    # Find where to insert our new methods
    index = updated_gui_code.find("class ThreadedHTTPServer")
    if index == -1:
        logger.error("Could not find the ThreadedHTTPServer class definition")
        return False
    
    # Insert the new methods before the ThreadedHTTPServer class
    updated_gui_code = updated_gui_code[:index] + pattern_handlers + updated_gui_code[index:]
    
    # Add required imports
    if "import tempfile" not in updated_gui_code:
        updated_gui_code = updated_gui_code.replace(
            "import time", 
            "import time\nimport tempfile"
        )
    
    # Write the updated GUI file
    with open(gui_path, 'w') as f:
        f.write(updated_gui_code)
    
    logger.info("Updated GUI API with Pattern Transformation endpoints")
    return True

def update_dashboard_html():
    """Update the dashboard HTML to include Pattern Transformation UI.
    
    This function adds UI elements for pattern transformation to the simple dashboard HTML.
    """
    dashboard_path = ROOT_DIR / "web_ui" / "static" / "dashboard.html"
    
    if not dashboard_path.exists():
        # The dashboard might not exist yet, it will be created when the GUI is run
        logger.warning(f"Dashboard file not found at {dashboard_path}, it will be updated when the GUI is run")
        return True
    
    # Read the dashboard file
    with open(dashboard_path, 'r') as f:
        dashboard_html = f.read()
    
    # Check if the Pattern Transformation tab already exists
    if '<button class="tab-button" data-tab="transformation">Transform</button>' in dashboard_html:
        logger.info("Pattern Transformation tab already exists in dashboard")
        return True
    
    # Add the transformation tab button
    tab_buttons = """                <div class="tab-buttons">
                    <button class="tab-button active" data-tab="analyze">Analyze</button>
                    <button class="tab-button" data-tab="demo">Demo</button>
                </div>"""
    
    new_tab_buttons = """                <div class="tab-buttons">
                    <button class="tab-button active" data-tab="analyze">Analyze</button>
                    <button class="tab-button" data-tab="demo">Demo</button>
                    <button class="tab-button" data-tab="transformation">Transform</button>
                </div>"""
    
    updated_dashboard_html = dashboard_html.replace(tab_buttons, new_tab_buttons)
    
    # Add the transformation tab content
    tab_contents = """                <div id="demoTab" class="tab-content">
                    <h2>Demo Projects</h2>
                    <p>Try these sample projects to see the analyzer in action.</p>
                    <div id="demoProjectsList">
                        <p>Loading demo projects...</p>
                    </div>
                </div>"""
    
    transformation_tab = """                <div id="demoTab" class="tab-content">
                    <h2>Demo Projects</h2>
                    <p>Try these sample projects to see the analyzer in action.</p>
                    <div id="demoProjectsList">
                        <p>Loading demo projects...</p>
                    </div>
                </div>
                
                <div id="transformationTab" class="tab-content">
                    <h2>Pattern Transformation</h2>
                    <p>Transform your code to apply design patterns and improve architecture.</p>
                    
                    <div class="action-section">
                        <button id="openTransformationBtn" class="action-btn">Open Pattern Transformation Tool</button>
                        <p>Use this tool to analyze your code for pattern opportunities and apply transformations.</p>
                    </div>
                    
                    <div class="recent-section">
                        <h3>Recent Transformations</h3>
                        <div id="transformationsList">
                            <p>Loading recent transformations...</p>
                        </div>
                    </div>
                </div>"""
    
    updated_dashboard_html = updated_dashboard_html.replace(tab_contents, transformation_tab)
    
    # Add JavaScript code to handle pattern transformation
    js_code = """        // Initial load
        fetchVisualizations();
        fetchDemoProjects();
        """
    
    new_js_code = """        // Initial load
        fetchVisualizations();
        fetchDemoProjects();
        
        // Set up transformation tab
        const openTransformationBtn = document.getElementById('openTransformationBtn');
        if (openTransformationBtn) {
            openTransformationBtn.addEventListener('click', openPatternTransformation);
        }
        
        // Fetch transformations list if on that tab
        if (document.querySelector('.tab-button[data-tab="transformation"]').classList.contains('active')) {
            fetchTransformations();
        }
        """
    
    updated_dashboard_html = updated_dashboard_html.replace(js_code, new_js_code)
    
    # Add the transformation functions
    function_to_add = """
        // Open pattern transformation tool
        async function openPatternTransformation() {
            try {
                const response = await fetch('/api/pattern-transformation', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showStatus(`Opening Pattern Transformation tool...`, 'info');
                } else {
                    showStatus(`Failed to open Pattern Transformation tool: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error opening Pattern Transformation tool:', error);
            }
        }
        
        // Fetch transformations list
        async function fetchTransformations() {
            try {
                const transformationsList = document.getElementById('transformationsList');
                if (!transformationsList) return;
                
                transformationsList.innerHTML = '<p>Loading transformations...</p>';
                
                const response = await fetch('/api/transformations-list', {
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
                if (document.getElementById('transformationsList')) {
                    document.getElementById('transformationsList').innerHTML = '<p>Error loading transformations.</p>';
                }
            }
        }
        
        // Display transformations
        function displayTransformations(transformations) {
            const transformationsList = document.getElementById('transformationsList');
            if (!transformationsList) return;
            
            transformationsList.innerHTML = '';
            
            if (transformations.length === 0) {
                transformationsList.innerHTML = '<p>No transformations have been applied yet.</p>';
                return;
            }
            
            transformations.forEach(transformation => {
                const card = document.createElement('div');
                card.className = 'card';
                
                // Format date
                const date = new Date(transformation.timestamp * 1000);
                const formattedDate = date.toLocaleString();
                
                card.innerHTML = `
                    <h3>${transformation.pattern} Pattern</h3>
                    <p><strong>Source:</strong> ${transformation.target}</p>
                    <p><strong>Applied on:</strong> ${formattedDate}</p>
                    <button class="visualize-btn" data-file="${transformation.output_path}">View Transformed File</button>
                `;
                
                transformationsList.appendChild(card);
                
                // Add click handler for the view button
                const viewButton = card.querySelector('button');
                viewButton.addEventListener('click', () => {
                    openVisualization(transformation.output_path);
                });
            });
        }
        
        // Add event listener for tab changes
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                if (button.getAttribute('data-tab') === 'transformation') {
                    fetchTransformations();
                }
            });
        });"""
    
    # Add our JS code before the closing script tag
    script_end = updated_dashboard_html.rfind("</script>")
    if script_end == -1:
        logger.error("Could not find the closing script tag")
        return False
    
    updated_dashboard_html = updated_dashboard_html[:script_end] + function_to_add + updated_dashboard_html[script_end:]
    
    # Add CSS for transformation tab
    css_to_add = """
        .action-section {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
            border-left: 4px solid #5bc0de;
        }
        
        .action-btn {
            background-color: #5bc0de;
            margin-bottom: 10px;
        }
        
        .recent-section {
            margin-top: 20px;
        }"""
    
    # Add CSS before the closing style tag
    style_end = updated_dashboard_html.find("</style>")
    if style_end == -1:
        logger.error("Could not find the closing style tag")
        return False
    
    updated_dashboard_html = updated_dashboard_html[:style_end] + css_to_add + updated_dashboard_html[style_end:]
    
    # Write the updated dashboard HTML
    with open(dashboard_path, 'w') as f:
        f.write(updated_dashboard_html)
    
    logger.info("Updated dashboard HTML with Pattern Transformation UI")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Integrate Pattern Transformation with Code Pattern Analyzer"
    )
    
    parser.add_argument(
        "--run-gui",
        action="store_true",
        help="Run the GUI after integrating"
    )
    
    args = parser.parse_args()
    
    try:
        # Update the GUI API
        update_gui_api()
        
        # Update the dashboard HTML
        update_dashboard_html()
        
        logger.info("Pattern Transformation successfully integrated with Code Pattern Analyzer")
        
        # Run the GUI if requested
        if args.run_gui:
            logger.info("Starting Code Pattern Analyzer GUI...")
            gui_path = ROOT_DIR / "code_pattern_analyzer_gui.py"
            os.system(f"{sys.executable} {gui_path}")
            
    except Exception as e:
        logger.error(f"Error integrating Pattern Transformation: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())