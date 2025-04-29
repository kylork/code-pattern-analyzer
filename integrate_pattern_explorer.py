#!/usr/bin/env python3
"""
Design Pattern Explorer Integration with Code Pattern Analyzer

This script integrates the Design Pattern Explorer with the main Code Pattern Analyzer GUI.
It adds API endpoints to browse and explore design patterns directly within the main application.

Usage:
    python integrate_pattern_explorer.py
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
import http.server
import socketserver
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
TEMPLATES_DIR = ROOT_DIR / "src" / "templates"
OUTPUT_DIR = ROOT_DIR / "output"
TEMP_DIR = ROOT_DIR / "tmp"

# Ensure output and temp directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Design pattern categories and available patterns
DESIGN_PATTERNS = {
    "Creational": [
        "Factory Method",
        "Abstract Factory",
        "Builder",
        "Prototype",
        "Singleton"
    ],
    "Structural": [
        "Adapter",
        "Bridge",
        "Composite",
        "Decorator",
        "Facade",
        "Flyweight",
        "Proxy"
    ],
    "Behavioral": [
        "Chain of Responsibility",
        "Command",
        "Interpreter",
        "Iterator",
        "Mediator",
        "Memento",
        "Observer",
        "State",
        "Strategy",
        "Template Method",
        "Visitor"
    ]
}

# Pattern to template file mapping
PATTERN_TEMPLATES = {
    "Factory Method": "factory_method_pattern.html",
    "Observer": "interactive_patterns.html"  # This is the original Observer pattern template
}

def get_available_patterns():
    """Get list of patterns that have template implementations."""
    return list(PATTERN_TEMPLATES.keys())

def generate_pattern_explorer(pattern, output_path):
    """Generate the HTML for a specific design pattern.
    
    Args:
        pattern: Name of the pattern to generate
        output_path: Path to save the HTML file
        
    Returns:
        Path to the generated HTML file
    """
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if the pattern template exists
    if pattern not in PATTERN_TEMPLATES:
        raise ValueError(f"Pattern '{pattern}' is not available")
    
    template_filename = PATTERN_TEMPLATES[pattern]
    template_path = TEMPLATES_DIR / template_filename
    
    if not template_path.exists():
        raise ValueError(f"Template file for '{pattern}' not found at {template_path}")
    
    # Copy template to output path
    shutil.copy(template_path, output_path)
    
    logger.info(f"Generated {pattern} pattern at {output_path}")
    return output_path

def update_gui_api():
    """Update the GUI API with Design Pattern Explorer endpoints.
    
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
    
    # Check if the Pattern Explorer endpoints already exist
    if "def handle_design_patterns_request" in gui_code:
        logger.info("Design Pattern Explorer endpoints already exist in GUI")
        return True
    
    # Find the handle_api_request method to add our endpoints
    api_request_handler = """    def handle_api_request(self):
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
            self.handle_generate_report_request()"""
    
    # Add our endpoints
    new_api_request_handler = """    def handle_api_request(self):
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
        elif self.path == '/api/design-patterns':
            self.handle_design_patterns_request()
        elif self.path == '/api/view-pattern':
            self.handle_view_pattern_request()"""
    
    # Replace the handler method with our updated version
    updated_gui_code = gui_code.replace(api_request_handler, new_api_request_handler)
    
    # Add our new handler methods before the class definition ends
    pattern_handlers = """
    def handle_design_patterns_request(self):
        """Handle request to list available design patterns."""
        # Build patterns data
        patterns_data = {}
        for category, patterns in DESIGN_PATTERNS.items():
            patterns_data[category] = []
            for pattern in patterns:
                pattern_info = {
                    'name': pattern,
                    'available': pattern in get_available_patterns()
                }
                patterns_data[category].append(pattern_info)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'success',
            'patterns': patterns_data
        }).encode())
    
    def handle_view_pattern_request(self):
        """Handle request to view a specific design pattern."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_data = json.loads(post_data.decode('utf-8'))
        
        pattern = request_data.get('pattern')
        if not pattern:
            self.send_error(400, "Missing pattern parameter")
            return
        
        # Check if pattern is available
        available_patterns = get_available_patterns()
        if pattern not in available_patterns:
            self.send_error(404, f"Pattern '{pattern}' is not available")
            return
        
        try:
            # Generate pattern explorer
            job_id = str(int(time.time()))
            output_file = f"pattern_{pattern.lower().replace(' ', '_')}_{job_id}.html"
            output_path = os.path.join(OUTPUT_DIR, output_file)
            
            # Start pattern generation in background
            threading.Thread(
                target=self._generate_pattern,
                args=(pattern, output_path, job_id)
            ).start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'started',
                'message': f'Generating pattern explorer for {pattern}',
                'job_id': job_id
            }).encode())
            
        except Exception as e:
            self.send_error(500, f"Error generating pattern: {str(e)}")
    
    def _generate_pattern(self, pattern, output_path, job_id):
        """Generate a design pattern explorer in the background.
        
        Args:
            pattern: Name of the pattern to generate
            output_path: Path to save the HTML file
            job_id: Job ID for tracking status
        """
        try:
            # Generate the pattern explorer
            generate_pattern_explorer(pattern, output_path)
            
            # Save the result status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'completed',
                    'output_file': os.path.basename(output_path),
                    'message': f'Pattern explorer for {pattern} generated successfully',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
                
            logger.info(f"Pattern explorer generation completed: {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating pattern explorer: {str(e)}")
            # Save error status
            status_file = os.path.join(TEMP_DIR, f"job_{job_id}.json")
            with open(status_file, 'w') as f:
                status = {
                    'status': 'failed',
                    'message': f'Error generating pattern explorer: {str(e)}',
                    'job_id': job_id,
                    'timestamp': time.time()
                }
                json.dump(status, f)
"""

    # Find where to insert our new methods
    index = updated_gui_code.find("class ThreadedHTTPServer")
    if index == -1:
        logger.error("Could not find the ThreadedHTTPServer class definition")
        return False
    
    # Insert the new methods before the ThreadedHTTPServer class
    updated_gui_code = updated_gui_code[:index] + pattern_handlers + updated_gui_code[index:]
    
    # Add required imports
    if "from pathlib import Path" not in updated_gui_code:
        updated_gui_code = updated_gui_code.replace(
            "import time", 
            "import time\nfrom pathlib import Path"
        )
    
    # Add constants for design patterns
    imports_end = updated_gui_code.find("# Path constants")
    if imports_end == -1:
        logger.error("Could not find the Path constants section")
        return False
    
    patterns_constants = """
# Design pattern categories and available patterns
DESIGN_PATTERNS = {
    "Creational": [
        "Factory Method",
        "Abstract Factory",
        "Builder",
        "Prototype",
        "Singleton"
    ],
    "Structural": [
        "Adapter",
        "Bridge",
        "Composite",
        "Decorator",
        "Facade",
        "Flyweight",
        "Proxy"
    ],
    "Behavioral": [
        "Chain of Responsibility",
        "Command",
        "Interpreter",
        "Iterator",
        "Mediator",
        "Memento",
        "Observer",
        "State",
        "Strategy",
        "Template Method",
        "Visitor"
    ]
}

# Pattern to template file mapping
PATTERN_TEMPLATES = {
    "Factory Method": "factory_method_pattern.html",
    "Observer": "interactive_patterns.html"
}

def get_available_patterns():
    \"\"\"Get list of patterns that have template implementations.\"\"\"
    return list(PATTERN_TEMPLATES.keys())
"""
    
    updated_gui_code = updated_gui_code[:imports_end] + patterns_constants + updated_gui_code[imports_end:]
    
    # Write the updated GUI file
    with open(gui_path, 'w') as f:
        f.write(updated_gui_code)
    
    logger.info("Updated GUI API with Design Pattern Explorer endpoints")
    return True

def update_dashboard_html():
    """Update the dashboard HTML to include Design Pattern Explorer UI.
    
    This function adds UI elements for design patterns to the simple dashboard HTML.
    """
    dashboard_path = ROOT_DIR / "web_ui" / "static" / "dashboard.html"
    
    if not dashboard_path.exists():
        # The dashboard might not exist yet, it will be created when the GUI is run
        logger.warning(f"Dashboard file not found at {dashboard_path}, it will be updated when the GUI is run")
        return True
    
    # Read the dashboard file
    with open(dashboard_path, 'r') as f:
        dashboard_html = f.read()
    
    # Check if the Design Pattern Explorer tab already exists
    if '<button class="tab-button" data-tab="patterns">Patterns</button>' in dashboard_html:
        logger.info("Design Pattern Explorer tab already exists in dashboard")
        return True
    
    # Add the patterns tab button
    tab_buttons = """                <div class="tab-buttons">
                    <button class="tab-button active" data-tab="analyze">Analyze</button>
                    <button class="tab-button" data-tab="demo">Demo</button>
                </div>"""
    
    new_tab_buttons = """                <div class="tab-buttons">
                    <button class="tab-button active" data-tab="analyze">Analyze</button>
                    <button class="tab-button" data-tab="demo">Demo</button>
                    <button class="tab-button" data-tab="patterns">Patterns</button>
                </div>"""
    
    updated_dashboard_html = dashboard_html.replace(tab_buttons, new_tab_buttons)
    
    # Add the patterns tab content
    tab_contents = """                <div id="demoTab" class="tab-content">
                    <h2>Demo Projects</h2>
                    <p>Try these sample projects to see the analyzer in action.</p>
                    <div id="demoProjectsList">
                        <p>Loading demo projects...</p>
                    </div>
                </div>"""
    
    patterns_tab = """                <div id="demoTab" class="tab-content">
                    <h2>Demo Projects</h2>
                    <p>Try these sample projects to see the analyzer in action.</p>
                    <div id="demoProjectsList">
                        <p>Loading demo projects...</p>
                    </div>
                </div>
                
                <div id="patternsTab" class="tab-content">
                    <h2>Design Patterns Explorer</h2>
                    <p>Browse and learn about design patterns with interactive examples.</p>
                    <div id="patternsList">
                        <p>Loading design patterns...</p>
                    </div>
                </div>"""
    
    updated_dashboard_html = updated_dashboard_html.replace(tab_contents, patterns_tab)
    
    # Add JavaScript code to handle design patterns
    js_code = """        // Initial load
        fetchVisualizations();
        fetchDemoProjects();
        """
    
    new_js_code = """        // Initial load
        fetchVisualizations();
        fetchDemoProjects();
        fetchDesignPatterns();
        """
    
    updated_dashboard_html = updated_dashboard_html.replace(js_code, new_js_code)
    
    # Add the fetchDesignPatterns function
    function_to_add = """        // Fetch design patterns
        async function fetchDesignPatterns() {
            try {
                const response = await fetch('/api/design-patterns', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayDesignPatterns(data.patterns);
                } else {
                    patternsList.innerHTML = '<p>Failed to load design patterns.</p>';
                }
            } catch (error) {
                console.error('Error fetching design patterns:', error);
                patternsList.innerHTML = '<p>Error loading design patterns.</p>';
            }
        }
        
        // Display design patterns
        function displayDesignPatterns(patterns) {
            const patternsList = document.getElementById('patternsList');
            patternsList.innerHTML = '';
            
            // Create UI for each pattern category
            for (const category in patterns) {
                const categorySection = document.createElement('div');
                categorySection.className = 'pattern-category';
                
                const categoryHeader = document.createElement('h3');
                categoryHeader.textContent = category;
                categorySection.appendChild(categoryHeader);
                
                const patternItems = document.createElement('div');
                patternItems.className = 'pattern-items';
                
                // Create UI for each pattern in the category
                patterns[category].forEach(pattern => {
                    const patternCard = document.createElement('div');
                    patternCard.className = 'card';
                    
                    const patternName = document.createElement('h4');
                    patternName.textContent = pattern.name;
                    patternCard.appendChild(patternName);
                    
                    // Show if the pattern is available
                    if (pattern.available) {
                        const viewButton = document.createElement('button');
                        viewButton.textContent = 'Explore Pattern';
                        viewButton.className = 'analyze-demo-btn';
                        viewButton.addEventListener('click', () => viewPattern(pattern.name));
                        patternCard.appendChild(viewButton);
                    } else {
                        const unavailableMsg = document.createElement('p');
                        unavailableMsg.textContent = 'Coming soon';
                        unavailableMsg.style.fontStyle = 'italic';
                        unavailableMsg.style.color = '#999';
                        patternCard.appendChild(unavailableMsg);
                    }
                    
                    patternItems.appendChild(patternCard);
                });
                
                categorySection.appendChild(patternItems);
                patternsList.appendChild(categorySection);
            }
        }
        
        // View a specific design pattern
        async function viewPattern(patternName) {
            try {
                showStatus(`Loading ${patternName} pattern explorer...`, 'info');
                
                const response = await fetch('/api/view-pattern', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ pattern: patternName })
                });
                
                const data = await response.json();
                
                if (data.status === 'started') {
                    currentJobId = data.job_id;
                    showStatus(`Pattern explorer generation started`, 'info');
                    
                    // Start checking status
                    if (statusCheckInterval) {
                        clearInterval(statusCheckInterval);
                    }
                    statusCheckInterval = setInterval(checkPatternStatus, 2000);
                } else {
                    showStatus(`Failed to load pattern: ${data.message || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                console.error('Error loading pattern:', error);
            }
        }
        
        // Check the status of a pattern generation job
        async function checkPatternStatus() {
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
                    showStatus(`Pattern explorer generated successfully!`, 'success');
                    clearInterval(statusCheckInterval);
                    
                    // Open the pattern explorer visualization
                    openVisualization(data.output_file);
                    
                    currentJobId = null;
                } else if (data.status === 'failed') {
                    showStatus(`Pattern generation failed: ${data.message || 'Unknown error'}`, 'error');
                    clearInterval(statusCheckInterval);
                    currentJobId = null;
                } else if (data.status === 'running') {
                    showStatus(`Pattern generation in progress...`, 'info');
                }
            } catch (error) {
                showStatus(`Error checking pattern status: ${error.message}`, 'error');
                console.error('Error checking pattern status:', error);
            }
        }"""
    
    # Add our JS code before the closing script tag
    script_end = updated_dashboard_html.rfind("</script>")
    if script_end == -1:
        logger.error("Could not find the closing script tag")
        return False
    
    updated_dashboard_html = updated_dashboard_html[:script_end] + function_to_add + updated_dashboard_html[script_end:]
    
    # Add CSS for pattern display
    css_to_add = """        .pattern-category {
            margin-bottom: 20px;
        }
        .pattern-items {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        .pattern-item {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #5bc0de;
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
    
    logger.info("Updated dashboard HTML with Design Pattern Explorer UI")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Integrate Design Pattern Explorer with Code Pattern Analyzer"
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
        
        logger.info("Design Pattern Explorer successfully integrated with Code Pattern Analyzer")
        
        # Run the GUI if requested
        if args.run_gui:
            logger.info("Starting Code Pattern Analyzer GUI...")
            gui_path = ROOT_DIR / "code_pattern_analyzer_gui.py"
            os.system(f"{sys.executable} {gui_path}")
            
    except Exception as e:
        logger.error(f"Error integrating Design Pattern Explorer: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())