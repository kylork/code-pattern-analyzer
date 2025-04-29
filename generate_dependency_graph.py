#!/usr/bin/env python3
"""
Generate dependency graphs for Python projects.

This script analyzes Python imports and module dependencies in a project,
generating graphical representations of the dependency structure.
"""

import os
import sys
import ast
import argparse
import logging
import json
from pathlib import Path
import importlib.util
from collections import defaultdict
import re

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Visualization libraries
import matplotlib.pyplot as plt
import networkx as nx

# Import project modules
from src.analyzer import CodeAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    """Analyzes import dependencies between modules in a Python project."""
    
    def __init__(self, use_tree_sitter=True):
        """Initialize the analyzer.
        
        Args:
            use_tree_sitter (bool): Whether to use tree-sitter for parsing.
        """
        self.analyzer = CodeAnalyzer(use_mock=not use_tree_sitter)
        self.dependencies = defaultdict(set)
        self.import_stats = {
            'total_imports': 0,
            'external_imports': 0,
            'internal_imports': 0,
            'relative_imports': 0,
            'modules_with_most_imports': [],
            'most_imported_modules': []
        }
        self.cycles = []
        self.module_to_path = {}
        self.path_to_module = {}
    
    def _is_internal_import(self, import_name, project_root, module_name):
        """Check if an import is internal to the project.
        
        Args:
            import_name (str): The name of the imported module.
            project_root (str): The root directory of the project.
            module_name (str): The name of the current module.
            
        Returns:
            bool: True if the import is internal to the project, False otherwise.
        """
        # Handle relative imports
        if import_name.startswith('.'):
            return True
            
        # Check if any project modules match this import
        for path_module in self.path_to_module.values():
            # Check if the import name is a submodule of an internal module
            if import_name == path_module or import_name.startswith(f"{path_module}."):
                return True
        
        # Try to find the import on the system
        try:
            spec = importlib.util.find_spec(import_name.split('.')[0])
            if spec and spec.origin:
                # If the import is found within the project directory, it's internal
                return project_root in spec.origin
            return False
        except (ImportError, AttributeError, ValueError):
            # If we can't find the module, assume it's external
            return False
    
    def _resolve_relative_import(self, import_name, current_module):
        """Resolve a relative import to its absolute name.
        
        Args:
            import_name (str): The name of the imported module.
            current_module (str): The name of the current module.
            
        Returns:
            str: The absolute name of the imported module.
        """
        if not import_name.startswith('.'):
            return import_name
            
        # Count the number of dots to determine how many levels to go up
        dots = 0
        while dots < len(import_name) and import_name[dots] == '.':
            dots += 1
            
        # Get the parts of the current module
        if '.' not in current_module and dots > 1:
            # If we're at the top level and trying to go up, that's an error
            logger.warning(f"Invalid relative import {import_name} in {current_module}")
            return None
            
        current_parts = current_module.split('.')
        
        # Remove parts based on the number of dots
        if dots > len(current_parts):
            logger.warning(f"Invalid relative import {import_name} in {current_module}")
            return None
            
        base_parts = current_parts[:-dots] if dots > 0 else current_parts
        
        # Add the remainder of the import name
        import_remainder = import_name[dots:]
        if import_remainder:
            return '.'.join(base_parts + [import_remainder])
        else:
            return '.'.join(base_parts)
    
    def _extract_imports_ast(self, file_path, code, module_name):
        """Extract imports from Python code using the AST.
        
        Args:
            file_path (str): The path to the file being analyzed.
            code (str): The code to analyze.
            module_name (str): The name of the module being analyzed.
            
        Returns:
            list: A list of imported module names.
        """
        imports = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    if node.level > 0:  # Relative import
                        prefix = '.' * node.level
                        module = f"{prefix}{module}"
                        
                    if module:
                        # For 'from x import y' style, add the module itself
                        imports.append(module)
                        
                        # Also add the specific imports if they're submodules
                        for name in node.names:
                            if name.name != '*' and not name.name.startswith('_'):
                                # Only add qualified names for potential modules, not functions/classes
                                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name.name):
                                    full_name = f"{module}.{name.name}"
                                    try:
                                        # Only add it if it looks like a module
                                        spec = importlib.util.find_spec(self._resolve_relative_import(full_name, module_name))
                                        if spec:
                                            imports.append(full_name)
                                    except (ImportError, ValueError, AttributeError):
                                        pass
                                        
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error parsing imports from {file_path}: {str(e)}")
            
        return imports
    
    def _extract_imports_regex(self, code):
        """Extract imports from Python code using regex (fallback method).
        
        Args:
            code (str): The code to analyze.
            
        Returns:
            list: A list of imported module names.
        """
        imports = []
        
        # Match 'import x' and 'import x as y'
        import_pattern = r'^\s*import\s+([\w\., ]+)'
        # Match 'from x import y' and 'from x import (y, z)'
        from_import_pattern = r'^\s*from\s+([\w\.]+)\s+import\s+'
        
        for line in code.split('\n'):
            # Skip comments
            if line.strip().startswith('#'):
                continue
                
            # Process 'import x' statements
            match = re.match(import_pattern, line)
            if match:
                modules = match.group(1).split(',')
                for module in modules:
                    # Handle 'import x as y'
                    name = module.split('as')[0].strip()
                    imports.append(name)
                    
            # Process 'from x import y' statements
            match = re.match(from_import_pattern, line)
            if match:
                module = match.group(1)
                imports.append(module)
                
        return imports
    
    def _map_file_to_module(self, project_root, files):
        """Map file paths to module names.
        
        Args:
            project_root (str): The root directory of the project.
            files (list): A list of file paths to analyze.
        """
        for file_path in files:
            if not file_path.endswith('.py'):
                continue
                
            # Convert path to module name
            rel_path = os.path.relpath(file_path, project_root)
            
            # Skip files that are not in a Python package
            if not any(os.path.isfile(os.path.join(os.path.dirname(file_path), '__init__.py')) 
                    for _ in range(len(Path(file_path).parts))):
                # This is a standalone script, use the filename without extension
                module_name = Path(file_path).stem
            else:
                # This is part of a package
                module_parts = []
                current_path = file_path
                
                while current_path != project_root:
                    parent_dir = os.path.dirname(current_path)
                    
                    if os.path.isfile(os.path.join(parent_dir, '__init__.py')):
                        # This directory is a package
                        if os.path.basename(current_path).endswith('.py'):
                            if os.path.basename(current_path) != '__init__.py':
                                # Add the filename without extension
                                module_parts.insert(0, Path(current_path).stem)
                            current_path = parent_dir
                        else:
                            # We've reached a non-Python file
                            break
                    else:
                        # We've reached a directory that's not a package
                        if os.path.basename(current_path).endswith('.py'):
                            # Add the filename without extension
                            module_parts.insert(0, Path(current_path).stem)
                        break
                    
                    # Add the directory name
                    module_parts.insert(0, os.path.basename(parent_dir))
                    current_path = parent_dir
                
                module_name = '.'.join(module_parts)
            
            self.module_to_path[module_name] = file_path
            self.path_to_module[file_path] = module_name
    
    def analyze_directory(self, directory, exclude_dirs=None, file_extensions=None):
        """Analyze all Python files in a directory.
        
        Args:
            directory (str): The directory to analyze.
            exclude_dirs (list): List of directories to exclude.
            file_extensions (list): List of file extensions to analyze.
            
        Returns:
            dict: Analysis results containing dependencies and metrics.
        """
        project_root = os.path.abspath(directory)
        
        # Get all Python files in the directory
        file_results = self.analyzer.analyze_directory(
            directory, 
            exclude_dirs=exclude_dirs,
            file_extensions=['.py'] if not file_extensions else file_extensions
        )
        
        # Map file paths to module names
        self._map_file_to_module(project_root, [r['file'] for r in file_results if 'error' not in r])
        
        # Analyze each file for dependencies
        for result in file_results:
            if 'error' in result:
                continue
                
            file_path = result['file']
            code = result['code']
            
            # Skip non-Python files
            if not file_path.endswith('.py'):
                continue
                
            # Get the module name for this file
            module_name = self.path_to_module.get(file_path, Path(file_path).stem)
            
            # Extract imports
            imports = self._extract_imports_ast(file_path, code, module_name) or self._extract_imports_regex(code)
            
            # Update stats
            self.import_stats['total_imports'] += len(imports)
            
            # Process each import
            file_external_imports = 0
            file_internal_imports = 0
            file_relative_imports = 0
            
            for import_name in imports:
                # Handle relative imports
                is_relative = import_name.startswith('.')
                if is_relative:
                    file_relative_imports += 1
                    self.import_stats['relative_imports'] += 1
                    
                    # Resolve relative import to absolute
                    resolved_import = self._resolve_relative_import(import_name, module_name)
                    if resolved_import:
                        import_name = resolved_import
                    else:
                        continue
                
                # Check if this is an internal or external import
                if self._is_internal_import(import_name, project_root, module_name):
                    file_internal_imports += 1
                    self.import_stats['internal_imports'] += 1
                    
                    # Only add internal dependencies to the graph
                    self.dependencies[module_name].add(import_name)
                else:
                    file_external_imports += 1
                    self.import_stats['external_imports'] += 1
        
        # Find cycles in the dependency graph
        self._detect_cycles()
        
        # Calculate additional metrics
        self._calculate_metrics()
        
        return {
            'dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'cycles': self.cycles,
            'stats': self.import_stats,
            'module_map': self.module_to_path
        }
    
    def _detect_cycles(self):
        """Detect cycles in the dependency graph using Tarjan's algorithm."""
        # Build a graph representation
        graph = nx.DiGraph()
        
        for module, imports in self.dependencies.items():
            graph.add_node(module)
            for imp in imports:
                if imp in self.module_to_path:  # Only add edges for modules in the project
                    graph.add_edge(module, imp)
        
        # Find strongly connected components (cycles)
        cycles = list(nx.simple_cycles(graph))
        
        # Filter out self-loops and sort cycles by length
        self.cycles = sorted(
            [cycle for cycle in cycles if len(cycle) > 1],
            key=len,
            reverse=True
        )
    
    def _calculate_metrics(self):
        """Calculate additional dependency metrics."""
        # Find modules with most imports
        modules_by_imports = sorted(
            [(module, len(imports)) for module, imports in self.dependencies.items()],
            key=lambda x: x[1],
            reverse=True
        )
        self.import_stats['modules_with_most_imports'] = modules_by_imports[:10]
        
        # Find most imported modules
        imported_count = defaultdict(int)
        for module, imports in self.dependencies.items():
            for imp in imports:
                if imp in self.module_to_path:  # Only count internal modules
                    imported_count[imp] += 1
        
        most_imported = sorted(
            [(module, count) for module, count in imported_count.items()],
            key=lambda x: x[1],
            reverse=True
        )
        self.import_stats['most_imported_modules'] = most_imported[:10]
    
    def visualize_dependencies(self, output_file, title="Module Dependencies", max_nodes=100, format="png"):
        """Visualize the dependency graph.
        
        Args:
            output_file (str): The file to write the visualization to.
            title (str): The title of the visualization.
            max_nodes (int): Maximum number of nodes to show in the graph.
            format (str): Output format (png, svg, pdf, html).
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for module, imports in self.dependencies.items():
            G.add_node(module)
            for imp in imports:
                if imp in self.module_to_path:  # Only add edges for modules in the project
                    G.add_edge(module, imp)
        
        # If the graph is too large, reduce it to the most important nodes
        if len(G.nodes) > max_nodes:
            # Sort nodes by degree centrality
            centrality = nx.degree_centrality(G)
            important_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            important_node_names = {n[0] for n in important_nodes}
            
            # Create a subgraph with the important nodes
            G = G.subgraph(important_node_names)
        
        if format == 'html':
            return self._generate_html_visualization(G, output_file, title)
        else:
            return self._generate_matplotlib_visualization(G, output_file, title, format)
    
    def _generate_matplotlib_visualization(self, G, output_file, title, format):
        """Generate a static visualization using matplotlib.
        
        Args:
            G (DiGraph): The graph to visualize.
            output_file (str): The file to write the visualization to.
            title (str): The title of the visualization.
            format (str): Output format (png, svg, pdf).
            
        Returns:
            str: Path to the generated file.
        """
        plt.figure(figsize=(12, 10))
        
        # Detect cycles for coloring
        cycle_nodes = set()
        for cycle in self.cycles:
            cycle_nodes.update(cycle)
        
        # Choose a layout
        if len(G.nodes) < 20:
            pos = nx.spring_layout(G, seed=42)
        else:
            pos = nx.kamada_kawai_layout(G)
        
        # Draw nodes - red for nodes in cycles, blue for others
        node_colors = ['#ff6666' if node in cycle_nodes else '#6666ff' for node in G.nodes]
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=0.8, node_size=500)
        nx.draw_networkx_edges(G, pos, edge_color='#999999', width=1, alpha=0.7, arrows=True, arrowsize=15)
        
        # Simplify labels for cleaner visualization
        labels = {}
        for node in G.nodes:
            parts = node.split('.')
            if len(parts) > 2:
                # Abbreviate middle parts
                labels[node] = f"{parts[0]}...{parts[-1]}"
            else:
                labels[node] = node
                
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
        
        # Add title and adjust layout
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        
        # Save the figure
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file, format=format)
        plt.close()
        
        return output_file
    
    def _generate_html_visualization(self, G, output_file, title):
        """Generate an interactive HTML visualization using D3.js.
        
        Args:
            G (DiGraph): The graph to visualize.
            output_file (str): The file to write the visualization to.
            title (str): The title of the visualization.
            
        Returns:
            str: Path to the generated file.
        """
        # Convert the graph to a JSON structure for D3.js
        nodes = []
        links = []
        
        # Identify cycle nodes for highlighting
        cycle_nodes = set()
        for cycle in self.cycles:
            cycle_nodes.update(cycle)
        
        # Create nodes
        for i, node in enumerate(G.nodes):
            # Calculate node size based on centrality
            in_degree = G.in_degree(node)
            out_degree = G.out_degree(node)
            
            nodes.append({
                'id': node,
                'name': node.split('.')[-1],  # Short name for display
                'full_name': node,  # Full module name
                'group': 1 if node in cycle_nodes else 2,
                'in_degree': in_degree,
                'out_degree': out_degree,
                'size': 5 + (in_degree + out_degree)
            })
        
        # Create links
        for edge in G.edges:
            source_idx = list(G.nodes).index(edge[0])
            target_idx = list(G.nodes).index(edge[1])
            
            links.append({
                'source': edge[0],
                'target': edge[1],
                'value': 1
            })
        
        # Prepare data for D3
        graph_data = {
            'nodes': nodes,
            'links': links
        }
        
        # Read the D3.js visualization template
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'templates')
        
        # If the template directory doesn't exist, create a minimum template
        if not os.path.exists(template_dir):
            os.makedirs(template_dir, exist_ok=True)
            
            # Create a minimal D3 template
            template_content = self._create_d3_template()
        else:
            # Try to use existing template
            template_path = os.path.join(template_dir, 'dependency_graph_template.html')
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template_content = f.read()
            else:
                template_content = self._create_d3_template()
        
        # Replace placeholders in the template
        html_content = template_content.replace('{{TITLE}}', title)
        html_content = html_content.replace('{{GRAPH_DATA}}', json.dumps(graph_data))
        
        # Add dependency cycles information
        cycles_html = "<h3>Dependency Cycles</h3>"
        if self.cycles:
            cycles_html += "<ul>"
            for cycle in self.cycles[:10]:  # Show top 10 cycles
                cycles_html += f"<li>{' → '.join(cycle)} → {cycle[0]}</li>"
            if len(self.cycles) > 10:
                cycles_html += f"<li>...and {len(self.cycles) - 10} more cycles</li>"
            cycles_html += "</ul>"
        else:
            cycles_html += "<p>No dependency cycles detected.</p>"
            
        html_content = html_content.replace('{{CYCLES_INFO}}', cycles_html)
        
        # Write the HTML file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        return output_file
    
    def _create_d3_template(self):
        """Create a minimal D3.js template for dependency graph visualization.
        
        Returns:
            str: HTML template with D3.js visualization.
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        #graph {
            width: 100%;
            height: 700px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .node {
            stroke: #fff;
            stroke-width: 1.5px;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
        }
        .node-label {
            font-size: 10px;
            pointer-events: none;
        }
        .cycles-list {
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{TITLE}}</h1>
        
        <div id="graph"></div>
        
        <div class="cycles-list">
            {{CYCLES_INFO}}
        </div>
    </div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        // Graph data
        const graph = {{GRAPH_DATA}};
        
        // Set up the visualization
        const width = document.getElementById('graph').offsetWidth;
        const height = document.getElementById('graph').offsetHeight;
        
        // Create SVG
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Create tooltip
        const tooltip = d3.select("#tooltip");
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });
            
        svg.call(zoom);
        
        // Create container for graph elements
        const g = svg.append("g");
        
        // Set up forces
        const simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size * 2));
        
        // Create the links
        const link = g.append("g")
            .selectAll("line")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke-width", 1)
            .attr("marker-end", "url(#arrowhead)");
        
        // Define arrow marker
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");
        
        // Create the nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(graph.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => d.group === 1 ? "#ff6666" : "#6666ff")
            .call(d3.drag()
                .on("start", dragStarted)
                .on("drag", dragged)
                .on("end", dragEnded))
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);
        
        // Add node labels
        const label = g.append("g")
            .selectAll("text")
            .data(graph.nodes)
            .enter().append("text")
            .attr("class", "node-label")
            .text(d => d.name)
            .attr("font-size", 10)
            .attr("dx", 12)
            .attr("dy", 4);
        
        // Update positions on each tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });
        
        // Drag functions
        function dragStarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragEnded(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Tooltip functions
        function showTooltip(event, d) {
            tooltip.style("opacity", 1)
                .html(`<strong>${d.full_name}</strong><br>
                        Incoming: ${d.in_degree}<br>
                        Outgoing: ${d.out_degree}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }
        
        function hideTooltip() {
            tooltip.style("opacity", 0);
        }
    </script>
</body>
</html>
"""

def generate_text_report(results, path, threshold=None):
    """Generate a text report of the dependency analysis.
    
    Args:
        results (dict): The analysis results.
        path (str): The path that was analyzed.
        threshold (int): Complexity threshold to highlight.
        
    Returns:
        str: The text report.
    """
    deps = results['dependencies']
    cycles = results['cycles']
    stats = results['stats']
    module_map = results['module_map']
    
    report = []
    report.append(f"Dependency Analysis Report: {path}")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    report.append("Summary Statistics:")
    report.append(f"  Total Modules: {len(deps)}")
    report.append(f"  Total Imports: {stats['total_imports']}")
    report.append(f"  Internal Imports: {stats['internal_imports']}")
    report.append(f"  External Imports: {stats['external_imports']}")
    report.append(f"  Relative Imports: {stats['relative_imports']}")
    report.append("")
    
    # Dependency cycles
    report.append("Dependency Cycles:")
    if cycles:
        for i, cycle in enumerate(cycles[:10], 1):
            report.append(f"  {i}. {' → '.join(cycle)} → {cycle[0]}")
        if len(cycles) > 10:
            report.append(f"  ... and {len(cycles) - 10} more cycles")
    else:
        report.append("  No dependency cycles detected.")
    report.append("")
    
    # Modules with most dependencies
    report.append("Modules with Most Outgoing Dependencies:")
    modules_list = stats['modules_with_most_imports']
    for module, count in modules_list[:10]:
        if count > 0:
            report.append(f"  {module}: {count} dependencies")
    report.append("")
    
    # Most imported modules
    report.append("Most Imported Modules:")
    modules_list = stats['most_imported_modules']
    for module, count in modules_list[:10]:
        if count > 0:
            report.append(f"  {module}: imported by {count} modules")
    report.append("")
    
    # Module details (top 20 by dependency count)
    report.append("Module Details:")
    sorted_deps = sorted(deps.items(), key=lambda x: len(x[1]), reverse=True)
    for module, imports in sorted_deps[:20]:
        if imports:
            report.append(f"  {module} ({module_map.get(module, 'unknown path')})")
            report.append(f"    Dependencies ({len(imports)}):")
            for imp in sorted(imports)[:10]:
                report.append(f"      {imp}")
            if len(imports) > 10:
                report.append(f"      ... and {len(imports) - 10} more")
            report.append("")
    
    if len(sorted_deps) > 20:
        report.append(f"  ... and {len(sorted_deps) - 20} more modules")
    
    return "\n".join(report)

def generate_html_report(results, path, threshold=None):
    """Generate an HTML report of the dependency analysis.
    
    Args:
        results (dict): The analysis results.
        path (str): The path that was analyzed.
        threshold (int): Complexity threshold to highlight.
        
    Returns:
        str: The HTML report.
    """
    deps = results['dependencies']
    cycles = results['cycles']
    stats = results['stats']
    module_map = results['module_map']
    
    # Start with the HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dependency Analysis: {os.path.basename(path)}</title>
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
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .card {{
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .stats {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }}
        .stat-card {{
            flex: 1 1 200px;
            margin: 10px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin-top: 0;
            font-size: 16px;
        }}
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .cycle {{
            background-color: #fff3f3;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #e74c3c;
        }}
        .module-card {{
            background: #f8f9fa;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #3498db;
        }}
        .dep-list {{
            list-style-type: none;
            padding-left: 20px;
        }}
        .dep-list li {{
            margin-bottom: 4px;
        }}
        .highlight {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .tabs {{
            display: flex;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border: 1px solid #ddd;
            border-bottom: none;
            margin-right: 5px;
            border-radius: 4px 4px 0 0;
        }}
        .tab.active {{
            background-color: #3498db;
            color: white;
            border-color: #3498db;
        }}
        .tab-content {{
            display: none;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 4px 4px 4px;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Dependency Analysis Report</h1>
        <p>Path: {path}</p>
    </div>
    
    <div class="card">
        <div class="section">
            <h2>Summary</h2>
            <div class="stats">
                <div class="stat-card">
                    <h3>Modules</h3>
                    <div class="value">{len(deps)}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Imports</h3>
                    <div class="value">{stats['total_imports']}</div>
                </div>
                <div class="stat-card">
                    <h3>Internal Imports</h3>
                    <div class="value">{stats['internal_imports']}</div>
                </div>
                <div class="stat-card">
                    <h3>External Imports</h3>
                    <div class="value">{stats['external_imports']}</div>
                </div>
                <div class="stat-card">
                    <h3>Dependency Cycles</h3>
                    <div class="value" style="color: {'#e74c3c' if cycles else '#2ecc71'};">{len(cycles)}</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="tabs">
            <div class="tab active" onclick="showTab('cycles')">Dependency Cycles</div>
            <div class="tab" onclick="showTab('outgoing')">Highest Outgoing</div>
            <div class="tab" onclick="showTab('incoming')">Most Imported</div>
            <div class="tab" onclick="showTab('details')">Module Details</div>
        </div>
        
        <div id="cycles" class="tab-content active">
            <h2>Dependency Cycles</h2>
    """
    
    # Add cycles
    if cycles:
        for i, cycle in enumerate(cycles[:20], 1):
            cycle_str = ' → '.join(cycle) + f' → {cycle[0]}'
            html += f'<div class="cycle"><strong>Cycle {i}:</strong> {cycle_str}</div>'
        
        if len(cycles) > 20:
            html += f'<p>... and {len(cycles) - 20} more cycles</p>'
    else:
        html += '<p>No dependency cycles detected. This is good!</p>'
    
    html += """
        </div>
        
        <div id="outgoing" class="tab-content">
            <h2>Modules with Most Outgoing Dependencies</h2>
    """
    
    # Add modules with most outgoing deps
    modules_list = stats['modules_with_most_imports']
    for module, count in modules_list[:15]:
        if count > 0:
            file_path = module_map.get(module, 'Unknown path')
            html += f'<div class="module-card"><strong>{module}</strong> ({file_path})<br>Outgoing dependencies: {count}</div>'
    
    html += """
        </div>
        
        <div id="incoming" class="tab-content">
            <h2>Most Imported Modules</h2>
    """
    
    # Add most imported modules
    modules_list = stats['most_imported_modules']
    for module, count in modules_list[:15]:
        if count > 0:
            file_path = module_map.get(module, 'Unknown path')
            html += f'<div class="module-card"><strong>{module}</strong> ({file_path})<br>Imported by {count} modules</div>'
    
    html += """
        </div>
        
        <div id="details" class="tab-content">
            <h2>Module Details</h2>
    """
    
    # Add module details
    sorted_deps = sorted(deps.items(), key=lambda x: len(x[1]), reverse=True)
    for module, imports in sorted_deps[:20]:
        if imports:
            html += f'<div class="module-card"><strong>{module}</strong> ({module_map.get(module, "unknown path")})<br>'
            html += f'Dependencies ({len(imports)}):<ul class="dep-list">'
            
            for imp in sorted(imports)[:10]:
                # Check if this import is in a cycle
                in_cycle = any(module in cycle and imp in cycle for cycle in cycles)
                if in_cycle:
                    html += f'<li><span class="highlight">{imp}</span></li>'
                else:
                    html += f'<li>{imp}</li>'
                    
            if len(imports) > 10:
                html += f'<li>... and {len(imports) - 10} more</li>'
                
            html += '</ul></div>'
    
    # End HTML
    html += """
        </div>
    </div>
    
    <script>
    function showTab(tabId) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show the selected tab
        document.getElementById(tabId).classList.add('active');
        
        // Add active class to clicked tab button
        Array.from(document.querySelectorAll('.tab')).find(tab => 
            tab.textContent.toLowerCase().includes(tabId)).classList.add('active');
    }
    </script>
</body>
</html>
    """
    
    return html

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate dependency graphs for Python projects."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the file or directory to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file for the report or visualization"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "html", "png", "svg", "pdf"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directories to exclude (e.g. 'tests,docs')"
    )
    parser.add_argument(
        "--extensions", "-e",
        help="Comma-separated list of file extensions to analyze (e.g. '.py,.js')"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        help="Threshold for highlighting in reports"
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=100,
        help="Maximum number of nodes to display in the visualization"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--visualization-only",
        action="store_true",
        help="Only generate visualization, not full report"
    )
    
    args = parser.parse_args()
    
    # Set default output file if not specified
    if not args.output:
        if os.path.isfile(args.path):
            output_name = f"{Path(args.path).stem}_dependencies"
        else:
            output_name = f"{os.path.basename(args.path)}_dependencies"
        
        if args.format == "html":
            args.output = f"reports/{output_name}.html"
        elif args.format == "json":
            args.output = f"reports/{output_name}.json"
        elif args.format == "text":
            args.output = f"reports/{output_name}.txt"
        else:  # Image formats
            args.output = f"reports/{output_name}.{args.format}"
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # Parse exclude and extensions
    exclude_dirs = None 
    if args.exclude:
        exclude_dirs = [dir.strip() for dir in args.exclude.split(',')]
    
    file_extensions = None 
    if args.extensions:
        file_extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    print(f"Analyzing dependencies in {args.path}...")
    
    # Initialize and run the analyzer
    analyzer = DependencyAnalyzer()
    
    if os.path.isdir(args.path):
        results = analyzer.analyze_directory(args.path, exclude_dirs, file_extensions)
    else:
        print("Single file analysis not supported. Please provide a directory.")
        return 1
    
    # Generate output
    if args.visualization_only or args.format in ['png', 'svg', 'pdf']:
        # Just generate visualization
        viz_format = args.format if args.format in ['png', 'svg', 'pdf'] else 'html'
        output_file = analyzer.visualize_dependencies(
            args.output,
            title=f"Dependency Graph: {os.path.basename(args.path)}",
            max_nodes=args.max_nodes,
            format=viz_format
        )
        print(f"Dependency visualization written to {output_file}")
        if viz_format == 'html':
            print(f"Open in your browser: file://{os.path.abspath(output_file)}")
    else:
        # Generate full report
        if args.format == 'json':
            report = json.dumps(results, indent=2, default=list)
        elif args.format == 'html':
            report = generate_html_report(results, args.path, args.threshold)
        else:  # text format
            report = generate_text_report(results, args.path, args.threshold)
        
        # Write to output file
        Path(args.output).write_text(report)
        print(f"Dependency analysis written to {args.output}")
        
        # Also generate a visualization if HTML report
        if args.format == 'html' and not args.visualization_only:
            viz_output = args.output.replace('.html', '_graph.html')
            analyzer.visualize_dependencies(
                viz_output,
                title=f"Dependency Graph: {os.path.basename(args.path)}",
                max_nodes=args.max_nodes,
                format='html'
            )
            print(f"Dependency visualization written to {viz_output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())