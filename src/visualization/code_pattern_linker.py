"""
Code-Pattern Linkage System.

This module provides a bidirectional linkage between architectural visualizations 
and code implementations, allowing users to explore the connection between 
high-level patterns and concrete code.
"""

import os
import json
import html
from typing import Dict, List, Optional, Set, Any, Tuple
from pathlib import Path
import re

class CodePatternLinker:
    """Creates bidirectional links between code and architectural patterns."""
    
    def __init__(self, code_root: str = ""):
        """Initialize the code-pattern linker.
        
        Args:
            code_root: Root directory of the codebase being analyzed
        """
        self.code_root = code_root
        
    def generate_linked_visualization(self, 
                                     graph_data: Dict[str, Any],
                                     output_file: str,
                                     title: str = "Code-Pattern Linkage",
                                     description: str = "") -> str:
        """Generate an HTML visualization with bidirectional code-pattern linkage.
        
        Args:
            graph_data: Dictionary containing nodes and links for the graph
            output_file: Path to save the HTML file
            title: Title for the visualization
            description: Description text for the visualization
            
        Returns:
            Path to the saved HTML file
        """
        # Ensure code snippets are available for each node
        self._process_node_code_snippets(graph_data)
        
        # Generate the HTML
        html_content = self._generate_html(graph_data, title, description)
        
        # Save the HTML file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    def _process_node_code_snippets(self, graph_data: Dict[str, Any]) -> None:
        """Extract code snippets for nodes in the graph.
        
        Args:
            graph_data: Dictionary containing nodes and links for the graph
        """
        for node in graph_data.get('nodes', []):
            file_path = node.get('file', '')
            if file_path:
                # Attempt to extract class or function definition
                node['code_snippet'] = self._extract_code_snippet(file_path, node)
                
                # Generate a simplified summary
                node['code_summary'] = self._generate_code_summary(node.get('code_snippet', ''))
    
    def _extract_code_snippet(self, file_path: str, node: Dict[str, Any]) -> str:
        """Extract a relevant code snippet for a node.
        
        Args:
            file_path: Path to the file containing the code
            node: Node data containing information about the component
            
        Returns:
            Code snippet as a string
        """
        # Check if file exists
        if not os.path.exists(file_path):
            # Try with code root
            full_path = os.path.join(self.code_root, file_path)
            if not os.path.exists(full_path):
                return f"// File not found: {file_path}"
            file_path = full_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract relevant snippet based on node type
            node_type = node.get('type', '')
            node_name = node.get('name', '')
            
            if node_type == 'class' and node_name:
                return self._extract_class_definition(content, node_name)
            elif node_type == 'function' and node_name:
                return self._extract_function_definition(content, node_name)
            elif node_type == 'module':
                # For modules, show the imports and first few lines
                lines = content.split('\n')
                return '\n'.join(lines[:min(20, len(lines))])
            else:
                # Default to showing the first 20 lines
                lines = content.split('\n')
                return '\n'.join(lines[:min(20, len(lines))])
        
        except Exception as e:
            return f"// Error extracting code: {str(e)}"
    
    def _extract_class_definition(self, content: str, class_name: str) -> str:
        """Extract a class definition from code content.
        
        Args:
            content: Full code content
            class_name: Name of the class to extract
            
        Returns:
            Class definition code
        """
        # Simple regex-based extraction - in a real implementation, you'd use AST
        patterns = [
            # Python
            rf"class\s+{re.escape(class_name)}\s*\(.*?\):\s*(?:\s*\"\"\".*?\"\"\"\s*)?.*?(?=\n\S|\Z)",
            # JavaScript
            rf"class\s+{re.escape(class_name)}\s*(\{{|\extends.*?\{{).*?(?=\n\}}|\Z)",
            # Java
            rf"(public|private|protected)?\s*class\s+{re.escape(class_name)}\s*(\{{|\extends.*?\{{|\implements.*?\{{).*?(?=\n\}}|\Z)"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, content, re.DOTALL)
            if matches:
                code = matches.group(0)
                # Limit to a reasonable snippet size
                lines = code.split('\n')
                if len(lines) > 30:
                    return '\n'.join(lines[:30]) + "\n// ... (truncated)"
                return code
        
        # If no match found, return a small section of the file
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                start = max(0, i - 2)
                end = min(len(lines), i + 20)
                return '\n'.join(lines[start:end])
        
        return f"// Class definition not found: {class_name}"
    
    def _extract_function_definition(self, content: str, function_name: str) -> str:
        """Extract a function definition from code content.
        
        Args:
            content: Full code content
            function_name: Name of the function to extract
            
        Returns:
            Function definition code
        """
        # Simple regex-based extraction - in a real implementation, you'd use AST
        patterns = [
            # Python
            rf"def\s+{re.escape(function_name)}\s*\(.*?\).*?(?=\n\S|\Z)",
            # JavaScript
            rf"(function\s+{re.escape(function_name)}\s*\(.*?\)|const\s+{re.escape(function_name)}\s*=\s*function\s*\(.*?\)|const\s+{re.escape(function_name)}\s*=\s*\(.*?\)\s*=>).*?(?=\n\}}|\Z)",
            # Java
            rf"(public|private|protected)?\s*(static\s+)?[a-zA-Z0-9_<>]+\s+{re.escape(function_name)}\s*\(.*?\).*?(?=\n\}}|\Z)"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, content, re.DOTALL)
            if matches:
                code = matches.group(0)
                # Limit to a reasonable snippet size
                lines = code.split('\n')
                if len(lines) > 20:
                    return '\n'.join(lines[:20]) + "\n// ... (truncated)"
                return code
        
        # If no match found, return a small section of the file
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if function_name in line and ("def " in line or "function " in line):
                start = max(0, i - 2)
                end = min(len(lines), i + 15)
                return '\n'.join(lines[start:end])
        
        return f"// Function definition not found: {function_name}"
    
    def _generate_code_summary(self, code_snippet: str) -> str:
        """Generate a summary of the code snippet.
        
        Args:
            code_snippet: Code snippet to summarize
            
        Returns:
            Short summary of the code
        """
        # Extract the first line - usually the definition
        lines = code_snippet.split('\n')
        if not lines:
            return "No code available"
        
        first_line = lines[0].strip()
        
        # Count the total lines
        total_lines = len(lines)
        
        # Check for docstring
        docstring = ""
        if total_lines > 1:
            for line in lines[1:min(5, total_lines)]:
                if '"""' in line or "'''" in line or "/**" in line or "*/" in line:
                    docstring_match = re.search(r'["\']([^"\']+)["\']|\/\*\*(.+?)\*\/', line)
                    if docstring_match:
                        docstring = docstring_match.group(1) or docstring_match.group(2)
                        docstring = docstring.strip()
                        break
        
        # Create a summary
        summary = first_line
        if docstring:
            summary += f" - {docstring}"
        
        return summary
    
    def _generate_html(self, 
                     graph_data: Dict[str, Any], 
                     title: str, 
                     description: str) -> str:
        """Generate the HTML for the linked visualization.
        
        Args:
            graph_data: Dictionary containing nodes and links for the graph
            title: Title for the visualization
            description: Description text for the visualization
            
        Returns:
            HTML content as a string
        """
        # Start building HTML
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'<title>{title}</title>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            self._get_styles(),
            # Include D3.js for visualization
            '<script src="https://d3js.org/d3.v7.min.js"></script>',
            # Include syntax highlighting
            '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/atom-one-dark.min.css">',
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>',
            '</head>',
            '<body>',
            '<div class="container">',
            f'<h1>{title}</h1>',
            
            # Description
            f'<div class="description">{description}</div>',
            
            # Main layout - split view
            '<div class="split-view">',
            
            # Left panel - visualization
            '<div class="split-view-left">',
            # Controls
            '<div class="controls">',
            '<div class="control-group">',
            '<label for="group-select">Group by:</label>',
            '<select id="group-select">',
            '<option value="none">None</option>',
            '<option value="type">Type</option>',
            '<option value="layer" selected>Layer</option>',
            '<option value="module">Module</option>',
            '</select>',
            '</div>',
            
            '<div class="control-group">',
            '<label for="filter-select">Filter:</label>',
            '<select id="filter-select">',
            '<option value="all" selected>All Components</option>',
            '<option value="presentation">Presentation Layer</option>',
            '<option value="business">Business Layer</option>',
            '<option value="data_access">Data Access Layer</option>',
            '<option value="domain">Domain Layer</option>',
            '</select>',
            '</div>',
            
            '<div class="control-group">',
            '<label>',
            '<input type="checkbox" id="show-violations" checked>',
            'Highlight Violations',
            '</label>',
            '</div>',
            
            '<div class="control-group">',
            '<button id="reset-zoom" class="btn">Reset View</button>',
            '</div>',
            '</div>',
            
            # Graph container
            '<div class="graph-container" id="graph"></div>',
            
            # Legend
            '<div class="legend" id="legend"></div>',
            '</div>',
            
            # Right panel - code view
            '<div class="split-view-right">',
            '<div class="code-view-header">',
            '<h3 id="code-view-title">Code View</h3>',
            '<button id="toggle-panel" class="btn">Hide Code</button>',
            '</div>',
            
            '<div class="code-snippet-container">',
            '<pre><code id="code-snippet" class="language-python">// Select a component to view its code</code></pre>',
            '</div>',
            
            # Component information
            '<div class="component-info">',
            '<div class="component-info-header">Component Details</div>',
            '<div id="component-details">',
            '<p>Select a component from the visualization to view details.</p>',
            '</div>',
            '</div>',
            '</div>',
            '</div>',
            
            # Add the graph data with code snippets
            f'<script>const graphData = {json.dumps(graph_data)};</script>',
            self._get_visualization_script(),
            
            '</div>', # Close container
            '</body>',
            '</html>'
        ]
        
        return '\n'.join(html)
    
    def _get_styles(self) -> str:
        """Get the CSS styles for the visualization.
        
        Returns:
            CSS styles as a string
        """
        return '''
            <style>
                /* General styles */
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    background-color: #f9fafc;
                    color: #343a40;
                }
                
                .container {
                    max-width: 1500px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                h1 {
                    margin: 0 0 15px 0;
                    color: #212529;
                    text-align: center;
                }
                
                .description {
                    margin-bottom: 20px;
                    text-align: center;
                    color: #6c757d;
                }
                
                /* Split View Layout */
                .split-view {
                    display: flex;
                    gap: 20px;
                    height: calc(100vh - 150px);
                    min-height: 600px;
                }
                
                .split-view-left {
                    flex: 1.3;
                    display: flex;
                    flex-direction: column;
                    min-width: 0;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }
                
                .split-view-right {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    min-width: 0;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    transition: flex 0.3s ease;
                }
                
                .split-view-right.collapsed {
                    flex: 0.1;
                }
                
                /* Controls */
                .controls {
                    display: flex;
                    flex-wrap: wrap;
                    align-items: center;
                    gap: 16px;
                    padding: 16px;
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #eaedf3;
                }
                
                .control-group {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .control-group label {
                    font-size: 0.9em;
                    color: #495057;
                }
                
                .control-group select,
                .control-group input {
                    padding: 6px 10px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    font-size: 0.9em;
                }
                
                .btn {
                    padding: 6px 12px;
                    background-color: #1565c0;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9em;
                    transition: background-color 0.2s;
                }
                
                .btn:hover {
                    background-color: #0d47a1;
                }
                
                /* Graph container */
                .graph-container {
                    flex-grow: 1;
                    position: relative;
                    overflow: hidden;
                }
                
                /* Legend */
                .legend {
                    padding: 16px;
                    background-color: #f8f9fa;
                    border-top: 1px solid #eaedf3;
                }
                
                .legend-title {
                    font-weight: 600;
                    margin-bottom: 10px;
                }
                
                .legend-items {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                }
                
                .legend-item {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                
                .legend-color {
                    width: 16px;
                    height: 16px;
                    border-radius: 3px;
                }
                
                /* Code View Panel */
                .code-view-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 16px;
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #eaedf3;
                }
                
                .code-view-header h3 {
                    margin: 0;
                    font-size: 1.1em;
                    color: #212529;
                }
                
                .code-snippet-container {
                    flex-grow: 1;
                    overflow: auto;
                    padding: 0;
                    background-color: #282c34;
                }
                
                .code-snippet-container pre {
                    margin: 0;
                    padding: 16px;
                }
                
                .code-snippet-container code {
                    font-family: 'Fira Code', Consolas, Monaco, 'Andale Mono', monospace;
                    font-size: 14px;
                    line-height: 1.5;
                }
                
                /* Component Info */
                .component-info {
                    padding: 16px;
                    background-color: #f8f9fa;
                    border-top: 1px solid #eaedf3;
                }
                
                .component-info-header {
                    font-weight: 600;
                    margin-bottom: 10px;
                    color: #212529;
                }
                
                .component-detail-row {
                    display: flex;
                    margin-bottom: 8px;
                }
                
                .component-detail-label {
                    flex: 0 0 100px;
                    font-weight: 500;
                    color: #495057;
                }
                
                .component-detail-value {
                    flex-grow: 1;
                    color: #212529;
                }
                
                /* Node and link styles (for D3) */
                .node circle {
                    stroke: #fff;
                    stroke-width: 2px;
                    cursor: pointer;
                }
                
                .node.selected circle {
                    stroke: #ffc107;
                    stroke-width: 3px;
                }
                
                .node text {
                    font-size: 10px;
                    fill: #212529;
                    text-anchor: middle;
                    pointer-events: none;
                }
                
                .link {
                    stroke-opacity: 0.6;
                }
                
                .link.violation {
                    stroke-dasharray: 4;
                }
                
                /* Layer colors */
                .presentation-layer { fill: #4caf50; }
                .business-layer { fill: #2196f3; }
                .data_access-layer { fill: #ff9800; }
                .domain-layer { fill: #9c27b0; }
                .unknown-layer { fill: #757575; }
                
                /* Responsive styles */
                @media (max-width: 1100px) {
                    .split-view {
                        flex-direction: column;
                        height: auto;
                    }
                    
                    .split-view-left, 
                    .split-view-right {
                        height: 500px;
                    }
                    
                    .controls {
                        flex-direction: column;
                        align-items: flex-start;
                    }
                }
            </style>
        '''
    
    def _get_visualization_script(self) -> str:
        """Get the JavaScript for the linked visualization.
        
        Returns:
            JavaScript as a string
        """
        return '''
            <script>
                // Initialize the force-directed graph visualization
                document.addEventListener('DOMContentLoaded', () => {
                    // Initialize syntax highlighting
                    hljs.highlightAll();
                    
                    // Check if we have data
                    if (!graphData || !graphData.nodes || !graphData.links) {
                        document.getElementById('graph').innerHTML = 
                            '<div style="text-align: center; padding: 50px;">No graph data available</div>';
                        return;
                    }
                    
                    // Initialize the visualization
                    const visualization = new CodeLinkedGraph('graph', 'legend');
                    
                    // Set up panel toggle
                    document.getElementById('toggle-panel').addEventListener('click', (e) => {
                        const panel = document.querySelector('.split-view-right');
                        const button = e.target;
                        
                        if (panel.classList.contains('collapsed')) {
                            panel.classList.remove('collapsed');
                            button.textContent = 'Hide Code';
                        } else {
                            panel.classList.add('collapsed');
                            button.textContent = 'Show Code';
                        }
                    });
                    
                    // Set up controls
                    document.getElementById('group-select').addEventListener('change', (e) => {
                        visualization.updateGrouping(e.target.value);
                    });
                    
                    document.getElementById('filter-select').addEventListener('change', (e) => {
                        visualization.updateFilter(e.target.value);
                    });
                    
                    document.getElementById('show-violations').addEventListener('change', (e) => {
                        visualization.toggleViolations(e.target.checked);
                    });
                    
                    document.getElementById('reset-zoom').addEventListener('click', () => {
                        visualization.resetZoom();
                    });
                    
                    // Initialize with the graph data
                    visualization.setData(graphData);
                    visualization.render();
                });
                
                // Code-linked graph visualization class
                class CodeLinkedGraph {
                    constructor(containerId, legendId) {
                        // Store element IDs
                        this.containerId = containerId;
                        this.legendId = legendId;
                        
                        // Get container dimensions
                        const container = document.getElementById(containerId);
                        this.width = container.clientWidth;
                        this.height = container.clientHeight;
                        
                        // Create SVG element
                        this.svg = d3.select(`#${containerId}`)
                            .append('svg')
                            .attr('width', this.width)
                            .attr('height', this.height);
                        
                        // Add a group for the graph elements
                        this.g = this.svg.append('g');
                        
                        // Add zoom behavior
                        this.zoom = d3.zoom()
                            .scaleExtent([0.1, 4])
                            .on('zoom', (event) => {
                                this.g.attr('transform', event.transform);
                            });
                        
                        this.svg.call(this.zoom);
                        
                        // Initialize data properties
                        this.nodes = [];
                        this.links = [];
                        this.filteredNodes = [];
                        this.filteredLinks = [];
                        
                        // Initialize visualization properties
                        this.groupBy = 'layer';
                        this.filter = 'all';
                        this.showViolations = true;
                        this.selectedNode = null;
                        
                        // Initialize the simulation
                        this.simulation = d3.forceSimulation()
                            .force('link', d3.forceLink().id(d => d.id).distance(100))
                            .force('charge', d3.forceManyBody().strength(-300))
                            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
                            .force('collision', d3.forceCollide().radius(30));
                    }
                    
                    // Set the graph data
                    setData(data) {
                        this.nodes = data.nodes || [];
                        this.links = data.links || [];
                        this.applyFilters();
                    }
                    
                    // Apply filtering based on current settings
                    applyFilters() {
                        // Filter nodes
                        if (this.filter === 'all') {
                            this.filteredNodes = [...this.nodes];
                        } else {
                            this.filteredNodes = this.nodes.filter(node => 
                                node.layer === this.filter
                            );
                            
                            // Get IDs of filtered nodes
                            const nodeIds = new Set(this.filteredNodes.map(node => node.id));
                            
                            // Add directly connected nodes
                            this.nodes.forEach(node => {
                                if (!nodeIds.has(node.id)) {
                                    // Check if this node is connected to any filtered node
                                    const hasConnection = this.links.some(link => 
                                        (link.source === node.id && nodeIds.has(link.target)) ||
                                        (link.target === node.id && nodeIds.has(link.source))
                                    );
                                    
                                    if (hasConnection) {
                                        this.filteredNodes.push(node);
                                        nodeIds.add(node.id);
                                    }
                                }
                            });
                        }
                        
                        // Filter links
                        const nodeIds = new Set(this.filteredNodes.map(node => node.id));
                        this.filteredLinks = this.links.filter(link => 
                            nodeIds.has(link.source) && nodeIds.has(link.target)
                        );
                    }
                    
                    // Update the grouping of nodes
                    updateGrouping(groupBy) {
                        this.groupBy = groupBy;
                        this.updateVisualization();
                    }
                    
                    // Update the filtering of nodes
                    updateFilter(filter) {
                        this.filter = filter;
                        this.applyFilters();
                        this.updateVisualization();
                    }
                    
                    // Toggle violation highlighting
                    toggleViolations(showViolations) {
                        this.showViolations = showViolations;
                        this.updateVisualization();
                    }
                    
                    // Reset zoom to default view
                    resetZoom() {
                        this.svg.transition()
                            .duration(750)
                            .call(this.zoom.transform, d3.zoomIdentity);
                    }
                    
                    // Display code for a node
                    displayNodeCode(node) {
                        // Update code view title
                        document.getElementById('code-view-title').textContent = 
                            `Code View: ${node.name || node.id}`;
                        
                        // Update code snippet
                        const codeSnippet = document.getElementById('code-snippet');
                        
                        // Determine language based on file extension
                        let language = 'text';
                        if (node.file) {
                            const ext = node.file.split('.').pop().toLowerCase();
                            if (['py', 'python'].includes(ext)) language = 'python';
                            else if (['js', 'jsx', 'ts', 'tsx'].includes(ext)) language = 'javascript';
                            else if (['java'].includes(ext)) language = 'java';
                            else if (['c', 'cpp', 'h', 'hpp'].includes(ext)) language = 'cpp';
                            else if (['cs'].includes(ext)) language = 'csharp';
                            else if (['go'].includes(ext)) language = 'go';
                            else if (['rb'].includes(ext)) language = 'ruby';
                        }
                        
                        // Set the code and language
                        codeSnippet.textContent = node.code_snippet || '// No code available';
                        codeSnippet.className = `language-${language}`;
                        
                        // Update syntax highlighting
                        hljs.highlightElement(codeSnippet);
                        
                        // Update component details
                        this.displayComponentDetails(node);
                    }
                    
                    // Display component details
                    displayComponentDetails(node) {
                        const detailsContainer = document.getElementById('component-details');
                        
                        // Clear previous content
                        detailsContainer.innerHTML = '';
                        
                        // Create detail rows
                        const details = [
                            { label: 'Name', value: node.name || node.id },
                            { label: 'Type', value: node.type || 'Unknown' },
                            { label: 'Layer', value: (node.layer || 'Unknown').replace('_', ' ').toUpperCase() },
                            { label: 'File', value: node.file || 'Unknown' },
                            { label: 'Summary', value: node.code_summary || 'No summary available' }
                        ];
                        
                        // Add details to container
                        details.forEach(detail => {
                            const row = document.createElement('div');
                            row.className = 'component-detail-row';
                            
                            const label = document.createElement('div');
                            label.className = 'component-detail-label';
                            label.textContent = detail.label + ':';
                            
                            const value = document.createElement('div');
                            value.className = 'component-detail-value';
                            value.textContent = detail.value;
                            
                            row.appendChild(label);
                            row.appendChild(value);
                            detailsContainer.appendChild(row);
                        });
                    }
                    
                    // Render the graph
                    render() {
                        // Clear existing elements
                        this.g.selectAll('*').remove();
                        
                        // Create arrow markers for links
                        this.g.append('defs').selectAll('marker')
                            .data(['arrow', 'violation-arrow'])
                            .enter().append('marker')
                            .attr('id', d => d)
                            .attr('viewBox', '0 -5 10 10')
                            .attr('refX', 25)
                            .attr('refY', 0)
                            .attr('markerWidth', 6)
                            .attr('markerHeight', 6)
                            .attr('orient', 'auto')
                            .append('path')
                            .attr('d', 'M0,-5L10,0L0,5')
                            .attr('fill', d => d === 'violation-arrow' ? '#e53935' : '#999');
                        
                        // Create links
                        this.linkElements = this.g.append('g')
                            .attr('class', 'links')
                            .selectAll('path')
                            .data(this.filteredLinks)
                            .enter().append('path')
                            .attr('class', d => `link${d.violation ? ' violation' : ''}`)
                            .attr('stroke', d => d.violation ? '#e53935' : '#999')
                            .attr('marker-end', d => `url(#${d.violation ? 'violation-arrow' : 'arrow'})`)
                            .attr('stroke-width', 1.5);
                        
                        // Create nodes
                        this.nodeElements = this.g.append('g')
                            .attr('class', 'nodes')
                            .selectAll('.node')
                            .data(this.filteredNodes)
                            .enter().append('g')
                            .attr('class', 'node')
                            .call(d3.drag()
                                .on('start', this.dragstarted.bind(this))
                                .on('drag', this.dragged.bind(this))
                                .on('end', this.dragended.bind(this))
                            )
                            .on('click', (event, d) => {
                                // Deselect previous node
                                if (this.selectedNode) {
                                    d3.select(this.selectedNode).classed('selected', false);
                                }
                                
                                // Select this node
                                this.selectedNode = event.currentTarget;
                                d3.select(this.selectedNode).classed('selected', true);
                                
                                // Display code and details
                                this.displayNodeCode(d);
                            });
                        
                        // Add circles to nodes
                        this.nodeElements.append('circle')
                            .attr('r', d => this._getNodeRadius(d))
                            .attr('class', d => `${d.layer || 'unknown'}-layer`)
                            .attr('stroke-width', 1.5);
                        
                        // Add labels to nodes
                        this.nodeElements.append('text')
                            .attr('dy', 4)
                            .text(d => this._getNodeLabel(d))
                            .attr('y', d => -this._getNodeRadius(d) - 5);
                        
                        // Update the simulation
                        this.simulation
                            .nodes(this.filteredNodes)
                            .force('link').links(this.filteredLinks);
                        
                        // Apply grouping force if needed
                        this._updateGroupingForce();
                        
                        // Set up the tick function
                        this.simulation.on('tick', () => this._tick());
                        
                        // Restart the simulation
                        this.simulation.alpha(1).restart();
                        
                        // Update the legend
                        this._updateLegend();
                        
                        // If there are nodes, select the first one to display code
                        if (this.filteredNodes.length > 0) {
                            setTimeout(() => {
                                const firstNode = this.filteredNodes[0];
                                const firstNodeElement = document.querySelector('.node');
                                if (firstNodeElement) {
                                    this.selectedNode = firstNodeElement;
                                    d3.select(this.selectedNode).classed('selected', true);
                                    this.displayNodeCode(firstNode);
                                }
                            }, 100);
                        }
                    }
                    
                    // Update the visualization without re-rendering everything
                    updateVisualization() {
                        // Update the grouping force
                        this._updateGroupingForce();
                        
                        // Update node classes for styling
                        this.nodeElements.selectAll('circle')
                            .attr('class', d => `${d.layer || 'unknown'}-layer`);
                        
                        // Update link styling for violations
                        this.linkElements
                            .attr('class', d => `link${d.violation && this.showViolations ? ' violation' : ''}`)
                            .attr('stroke', d => d.violation && this.showViolations ? '#e53935' : '#999')
                            .attr('marker-end', d => 
                                `url(#${d.violation && this.showViolations ? 'violation-arrow' : 'arrow'})`
                            );
                        
                        // Update the legend
                        this._updateLegend();
                        
                        // Restart the simulation
                        this.simulation.alpha(1).restart();
                    }
                    
                    // Handle drag start
                    dragstarted(event, d) {
                        if (!event.active) this.simulation.alphaTarget(0.3).restart();
                        d.fx = d.x;
                        d.fy = d.y;
                    }
                    
                    // Handle drag
                    dragged(event, d) {
                        d.fx = event.x;
                        d.fy = event.y;
                    }
                    
                    // Handle drag end
                    dragended(event, d) {
                        if (!event.active) this.simulation.alphaTarget(0);
                        d.fx = null;
                        d.fy = null;
                    }
                    
                    // Update the tick function for the simulation
                    _tick() {
                        // Update link paths
                        this.linkElements.attr('d', d => {
                            const dx = d.target.x - d.source.x;
                            const dy = d.target.y - d.source.y;
                            const dr = Math.sqrt(dx * dx + dy * dy);
                            
                            // Calculate offsets for source and target
                            const sourceRadius = this._getNodeRadius(d.source);
                            const targetRadius = this._getNodeRadius(d.target);
                            
                            // Calculate the start and end points
                            const offsetRatio = sourceRadius / dr;
                            const startX = d.source.x + dx * offsetRatio;
                            const startY = d.source.y + dy * offsetRatio;
                            
                            const targetOffsetRatio = targetRadius / dr;
                            const endX = d.target.x - dx * targetOffsetRatio;
                            const endY = d.target.y - dy * targetOffsetRatio;
                            
                            return `M${startX},${startY}L${endX},${endY}`;
                        });
                        
                        // Update node positions
                        this.nodeElements.attr('transform', d => `translate(${d.x},${d.y})`);
                    }
                    
                    // Update the grouping force
                    _updateGroupingForce() {
                        // Remove any existing group force
                        this.simulation.force('x', null);
                        this.simulation.force('y', null);
                        
                        if (this.groupBy === 'none') {
                            // No grouping - just center force
                            this.simulation.force('center', d3.forceCenter(this.width / 2, this.height / 2));
                        } else if (this.groupBy === 'layer') {
                            // Group by layer
                            const layers = ['presentation', 'business', 'data_access', 'domain', 'unknown'];
                            
                            this.simulation.force('x', d3.forceX().x(d => {
                                const layerIndex = layers.indexOf(d.layer || 'unknown');
                                const step = this.width / (layers.length + 1);
                                return (layerIndex + 1) * step;
                            }).strength(0.3));
                            
                            this.simulation.force('y', d3.forceY(this.height / 2).strength(0.1));
                            this.simulation.force('center', null);
                        } else if (this.groupBy === 'type') {
                            // Group by component type
                            this.simulation.force('x', d3.forceX().x(d => {
                                const type = d.type || 'unknown';
                                return type.includes('class') ? this.width * 0.25 : this.width * 0.75;
                            }).strength(0.3));
                            
                            this.simulation.force('y', d3.forceY(this.height / 2).strength(0.1));
                            this.simulation.force('center', null);
                        } else if (this.groupBy === 'module') {
                            // Group by module (folder)
                            const modules = new Set();
                            this.filteredNodes.forEach(node => {
                                const filePath = node.file || '';
                                const parts = filePath.split('/');
                                const module = parts.length > 1 ? parts[parts.length - 2] : 'unknown';
                                modules.add(module);
                                node.module = module;
                            });
                            
                            const moduleArray = Array.from(modules);
                            const columns = Math.ceil(Math.sqrt(moduleArray.length));
                            const rows = Math.ceil(moduleArray.length / columns);
                            
                            this.simulation.force('x', d3.forceX().x(d => {
                                const module = d.module || 'unknown';
                                const moduleIndex = moduleArray.indexOf(module);
                                const col = moduleIndex % columns;
                                const step = this.width / (columns + 1);
                                return (col + 1) * step;
                            }).strength(0.3));
                            
                            this.simulation.force('y', d3.forceY().y(d => {
                                const module = d.module || 'unknown';
                                const moduleIndex = moduleArray.indexOf(module);
                                const row = Math.floor(moduleIndex / columns);
                                const step = this.height / (rows + 1);
                                return (row + 1) * step;
                            }).strength(0.3));
                            
                            this.simulation.force('center', null);
                        }
                    }
                    
                    // Update the legend
                    _updateLegend() {
                        const legend = document.getElementById(this.legendId);
                        legend.innerHTML = '';
                        
                        // Create the legend title
                        const title = document.createElement('div');
                        title.className = 'legend-title';
                        title.textContent = this._getLegendTitle();
                        legend.appendChild(title);
                        
                        // Create the legend items container
                        const items = document.createElement('div');
                        items.className = 'legend-items';
                        
                        // Add legend items based on grouping
                        if (this.groupBy === 'layer') {
                            const layers = [
                                { name: 'Presentation', color: '#4caf50', class: 'presentation-layer' },
                                { name: 'Business', color: '#2196f3', class: 'business-layer' },
                                { name: 'Data Access', color: '#ff9800', class: 'data_access-layer' },
                                { name: 'Domain', color: '#9c27b0', class: 'domain-layer' },
                                { name: 'Unknown', color: '#757575', class: 'unknown-layer' }
                            ];
                            
                            layers.forEach(layer => {
                                const item = this._createLegendItem(layer.name, layer.color);
                                items.appendChild(item);
                            });
                        } else if (this.groupBy === 'type') {
                            const types = [
                                { name: 'Class', color: '#2196f3' },
                                { name: 'Function', color: '#4caf50' },
                                { name: 'Module', color: '#ff9800' },
                                { name: 'Unknown', color: '#757575' }
                            ];
                            
                            types.forEach(type => {
                                const item = this._createLegendItem(type.name, type.color);
                                items.appendChild(item);
                            });
                        }
                        
                        // Add link types
                        const linkTypes = [
                            { name: 'Dependency', color: '#999' }
                        ];
                        
                        if (this.showViolations) {
                            linkTypes.push({ name: 'Violation', color: '#e53935', dashed: true });
                        }
                        
                        linkTypes.forEach(link => {
                            const item = this._createLegendItem(
                                link.name, 
                                link.color, 
                                link.dashed ? '4' : '0'
                            );
                            items.appendChild(item);
                        });
                        
                        legend.appendChild(items);
                    }
                    
                    // Create a legend item
                    _createLegendItem(name, color, dashArray = '0') {
                        const item = document.createElement('div');
                        item.className = 'legend-item';
                        
                        const colorBox = document.createElement('div');
                        colorBox.className = 'legend-color';
                        colorBox.style.backgroundColor = color;
                        
                        // Add dashed border for links
                        if (dashArray !== '0') {
                            colorBox.style.backgroundColor = 'transparent';
                            colorBox.style.border = `2px dashed ${color}`;
                        }
                        
                        const label = document.createElement('span');
                        label.textContent = name;
                        
                        item.appendChild(colorBox);
                        item.appendChild(label);
                        
                        return item;
                    }
                    
                    // Get the legend title based on grouping
                    _getLegendTitle() {
                        if (this.groupBy === 'none') {
                            return 'Components';
                        } else if (this.groupBy === 'layer') {
                            return 'Layers';
                        } else if (this.groupBy === 'type') {
                            return 'Component Types';
                        } else if (this.groupBy === 'module') {
                            return 'Modules';
                        }
                        
                        return 'Legend';
                    }
                    
                    // Get node radius based on its properties
                    _getNodeRadius(node) {
                        // Base radius
                        let radius = 10;
                        
                        // Adjust based on type
                        if (node.type === 'class') {
                            radius = 12;
                        } else if (node.type === 'function') {
                            radius = 8;
                        }
                        
                        // Adjust based on connections
                        const connections = this._getNodeConnectionCount(node);
                        radius += Math.min(connections, 10);
                        
                        return radius;
                    }
                    
                    // Get the number of connections for a node
                    _getNodeConnectionCount(node) {
                        let count = 0;
                        
                        this.filteredLinks.forEach(link => {
                            if ((link.source.id && link.source.id === node.id) || 
                                (link.source === node.id) ||
                                (link.target.id && link.target.id === node.id) || 
                                (link.target === node.id)) {
                                count++;
                            }
                        });
                        
                        return count;
                    }
                    
                    // Get node label
                    _getNodeLabel(node) {
                        return node.name || node.id || '';
                    }
                }
            </script>
        '''