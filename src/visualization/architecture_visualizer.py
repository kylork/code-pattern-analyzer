"""
Visualization components for architectural patterns.

This module provides visualization tools specifically designed for
rendering architectural patterns detected by the analyzer.
"""

import os
import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

class ArchitectureVisualizer:
    """Base class for architecture visualization components."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the architecture visualizer.
        
        Args:
            output_dir: Directory to save visualization output
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_visualization(self, filename: str, content: str) -> str:
        """Save visualization content to a file.
        
        Args:
            filename: Name of the file to save
            content: Content to save
            
        Returns:
            Full path to the saved file
        """
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w') as f:
            f.write(content)
        return output_path


class LayeredArchitectureVisualizer(ArchitectureVisualizer):
    """Visualizer for layered architecture patterns."""
    
    def generate_html(self, analysis_result: Dict[str, Any]) -> str:
        """Generate an HTML visualization for a layered architecture.
        
        Args:
            analysis_result: The analysis result from the layered architecture detector
            
        Returns:
            HTML content as a string
        """
        # Extract data from the analysis result
        confidence = analysis_result.get('confidence', 0.0)
        layer_counts = analysis_result.get('layer_counts', {})
        layer_dependencies = analysis_result.get('layer_dependencies', {})
        components = analysis_result.get('components', {})
        violation_stats = analysis_result.get('violation_statistics', {})
        violations = analysis_result.get('dependency_violations', [])
        description = analysis_result.get('description', '')
        recommendations = analysis_result.get('recommendations', [])
        graph_data = analysis_result.get('layered_architecture_graph', {})
        
        # Start building HTML
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<title>Layered Architecture Analysis</title>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            self._get_styles(),
            # Include D3.js for graph visualization
            '<script src="https://d3js.org/d3.v7.min.js"></script>',
            '</head>',
            '<body>',
            '<div class="container">',
            '<h1>Layered Architecture Analysis</h1>',
            
            # Overview section
            '<div class="section overview">',
            '<h2>Overview</h2>',
            f'<div class="confidence-meter" title="Confidence: {confidence:.2f}">',
            f'<div class="confidence-fill" style="width: {int(confidence * 100)}%;"></div>',
            f'<div class="confidence-label">{confidence:.2f}</div>',
            '</div>',
            f'<div class="description">{description}</div>',
            '</div>',
            
            # Layer composition section
            '<div class="section">',
            '<h2>Layer Composition</h2>',
            '<div class="layer-stats">',
        ]
        
        # Add layer count bars
        for layer, count in sorted(layer_counts.items(), key=lambda x: x[1], reverse=True):
            max_count = max(layer_counts.values()) if layer_counts else 1
            percentage = int((count / max_count) * 100) if max_count > 0 else 0
            layer_display = layer.replace('_', ' ').title()
            
            html.extend([
                f'<div class="layer-bar-container">',
                f'<div class="layer-label">{layer_display}</div>',
                f'<div class="layer-bar">',
                f'<div class="layer-bar-fill layer-{layer}" style="width: {percentage}%;"></div>',
                f'<div class="layer-count">{count}</div>',
                '</div>',
                '</div>'
            ])
        
        html.append('</div>')  # Close layer-stats
        
        # Add top components
        if any(components.values()):
            html.append('<h3>Key Components</h3>')
            html.append('<div class="components-grid">')
            
            for layer, comps in components.items():
                if not comps:
                    continue
                
                layer_display = layer.replace('_', ' ').title()
                
                html.extend([
                    f'<div class="component-group">',
                    f'<h4>{layer_display}</h4>',
                    '<ul>'
                ])
                
                for comp in comps:
                    name = comp.get('name', 'Unknown')
                    file_path = comp.get('file', '')
                    comp_type = comp.get('type', '')
                    
                    html.append(
                        f'<li title="{file_path}"><span class="component-name">{name}</span>'
                        f'<span class="component-type">{comp_type}</span></li>'
                    )
                
                html.extend([
                    '</ul>',
                    '</div>'
                ])
            
            html.append('</div>')  # Close components-grid
        
        html.append('</div>')  # Close section
        
        # Dependency graph section
        html.extend([
            '<div class="section">',
            '<h2>Layer Dependencies</h2>',
            '<div id="layer-graph" class="graph-container"></div>',
            f'<script>const graphData = {json.dumps(graph_data)};</script>'
        ])
        
        # Add violation statistics if any
        violation_count = violation_stats.get('count', 0)
        if violation_count > 0:
            html.extend([
                '<div class="violations-summary">',
                f'<h3>Dependency Violations ({violation_count})</h3>'
            ])
            
            # Violations by source layer
            if violation_stats.get('by_source_layer'):
                html.extend([
                    '<div class="violation-stats">',
                    '<h4>Violations by Source Layer</h4>',
                    '<ul>'
                ])
                
                for layer, count in violation_stats['by_source_layer'].items():
                    layer_display = layer.replace('_', ' ').title()
                    html.append(f'<li>{layer_display}: {count}</li>')
                
                html.extend([
                    '</ul>',
                    '</div>'
                ])
            
            # Violations by target layer
            if violation_stats.get('by_target_layer'):
                html.extend([
                    '<div class="violation-stats">',
                    '<h4>Violations by Target Layer</h4>',
                    '<ul>'
                ])
                
                for layer, count in violation_stats['by_target_layer'].items():
                    layer_display = layer.replace('_', ' ').title()
                    html.append(f'<li>{layer_display}: {count}</li>')
                
                html.extend([
                    '</ul>',
                    '</div>'
                ])
            
            # Most common violation
            most_common = violation_stats.get('most_common_violation')
            if most_common:
                source = most_common.get('source', '').replace('_', ' ').title()
                target = most_common.get('target', '').replace('_', ' ').title()
                count = most_common.get('count', 0)
                
                html.extend([
                    '<div class="most-common-violation">',
                    f'<h4>Most Common Violation</h4>',
                    f'<p>{source} → {target}: {count} instances</p>',
                    '</div>'
                ])
            
            html.append('</div>')  # Close violations-summary
            
            # List specific violations
            if violations:
                html.extend([
                    '<div class="violation-list">',
                    '<h4>Specific Violations</h4>',
                    '<table class="violations-table">',
                    '<thead>',
                    '<tr>',
                    '<th>From</th>',
                    '<th>To</th>',
                    '<th>Source File</th>',
                    '<th>Line</th>',
                    '</tr>',
                    '</thead>',
                    '<tbody>'
                ])
                
                for violation in violations:
                    source = violation.get('source_layer', '').replace('_', ' ').title()
                    target = violation.get('target_layer', '').replace('_', ' ').title()
                    source_file = os.path.basename(violation.get('source_file', ''))
                    line = violation.get('line', '')
                    
                    html.append(
                        f'<tr>'
                        f'<td>{source}</td>'
                        f'<td>{target}</td>'
                        f'<td title="{violation.get("source_file", "")}">{source_file}</td>'
                        f'<td>{line}</td>'
                        f'</tr>'
                    )
                
                html.extend([
                    '</tbody>',
                    '</table>',
                    '</div>'
                ])
        
        html.append('</div>')  # Close section
        
        # Recommendations section
        if recommendations:
            html.extend([
                '<div class="section">',
                '<h2>Recommendations</h2>',
                '<ul class="recommendations-list">'
            ])
            
            for rec in recommendations:
                html.append(f'<li>{rec}</li>')
            
            html.extend([
                '</ul>',
                '</div>'
            ])
        
        # Close containers
        html.extend([
            '</div>',  # Close container
            self._get_graph_script(),
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html)
    
    def visualize(self, analysis_result: Dict[str, Any], filename: str = "layered_architecture.html") -> str:
        """Generate and save a visualization for a layered architecture.
        
        Args:
            analysis_result: The analysis result from the layered architecture detector
            filename: Name of the output file
            
        Returns:
            Path to the saved HTML file
        """
        html_content = self.generate_html(analysis_result)
        return self.save_visualization(filename, html_content)
    
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
                    background-color: #f8f9fa;
                    color: #343a40;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                h1, h2, h3, h4 {
                    color: #212529;
                    margin-top: 0;
                }
                
                h1 {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #dee2e6;
                }
                
                /* Section styles */
                .section {
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    padding: 25px;
                    margin-bottom: 30px;
                }
                
                /* Confidence meter */
                .confidence-meter {
                    height: 30px;
                    background-color: #e9ecef;
                    border-radius: 15px;
                    overflow: hidden;
                    position: relative;
                    margin: 20px 0;
                }
                
                .confidence-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #4caf50, #8bc34a, #cddc39);
                    border-radius: 15px;
                    transition: width 0.5s ease-in-out;
                }
                
                .confidence-label {
                    position: absolute;
                    top: 0;
                    right: 10px;
                    line-height: 30px;
                    color: #495057;
                    font-weight: bold;
                }
                
                .description {
                    font-size: 1.1em;
                    margin: 20px 0;
                    line-height: 1.7;
                }
                
                /* Layer stats */
                .layer-stats {
                    margin: 20px 0;
                }
                
                .layer-bar-container {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }
                
                .layer-label {
                    width: 150px;
                    font-weight: bold;
                    color: #495057;
                }
                
                .layer-bar {
                    flex-grow: 1;
                    height: 25px;
                    background-color: #e9ecef;
                    border-radius: 5px;
                    overflow: hidden;
                    position: relative;
                }
                
                .layer-bar-fill {
                    height: 100%;
                    transition: width 0.5s ease-in-out;
                }
                
                .layer-presentation {
                    background-color: #4caf50;
                }
                
                .layer-business {
                    background-color: #2196f3;
                }
                
                .layer-data_access {
                    background-color: #ff9800;
                }
                
                .layer-domain {
                    background-color: #9c27b0;
                }
                
                .layer-count {
                    position: absolute;
                    top: 0;
                    right: 10px;
                    line-height: 25px;
                    color: #343a40;
                    font-weight: bold;
                }
                
                /* Components grid */
                .components-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                
                .component-group {
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                
                .component-group h4 {
                    margin-top: 0;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #dee2e6;
                    color: #343a40;
                }
                
                .component-group ul {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                }
                
                .component-group li {
                    padding: 8px 0;
                    border-bottom: 1px solid #f1f1f1;
                    display: flex;
                    justify-content: space-between;
                }
                
                .component-name {
                    font-weight: bold;
                }
                
                .component-type {
                    color: #6c757d;
                    font-size: 0.9em;
                }
                
                /* Graph container */
                .graph-container {
                    height: 400px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin: 20px 0;
                    position: relative;
                }
                
                /* Violations */
                .violations-summary {
                    margin-top: 30px;
                    background-color: #fff3cd;
                    border-radius: 5px;
                    padding: 15px;
                }
                
                .violation-stats {
                    margin-top: 15px;
                }
                
                .violations-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }
                
                .violations-table th, 
                .violations-table td {
                    border: 1px solid #dee2e6;
                    padding: 8px;
                    text-align: left;
                }
                
                .violations-table th {
                    background-color: #f8f9fa;
                }
                
                .violations-table tr:nth-child(even) {
                    background-color: #f1f1f1;
                }
                
                /* Recommendations */
                .recommendations-list {
                    padding-left: 20px;
                }
                
                .recommendations-list li {
                    margin-bottom: 10px;
                    line-height: 1.7;
                }
                
                /* D3 specific styles */
                .node circle {
                    stroke: #fff;
                    stroke-width: 2px;
                }
                
                .node text {
                    font-size: 12px;
                    font-weight: bold;
                }
                
                .link {
                    fill: none;
                    stroke-width: 2px;
                }
                
                .link.violation {
                    stroke-dasharray: 5;
                }
                
                /* Responsive styles */
                @media (max-width: 768px) {
                    .components-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .layer-bar-container {
                        flex-direction: column;
                        align-items: flex-start;
                    }
                    
                    .layer-label {
                        width: 100%;
                        margin-bottom: 5px;
                    }
                    
                    .layer-bar {
                        width: 100%;
                    }
                    
                    .graph-container {
                        height: 300px;
                    }
                }
            </style>
        '''
    
    def _get_graph_script(self) -> str:
        """Get the JavaScript for the dependency graph visualization.
        
        Returns:
            JavaScript as a string
        """
        return '''
            <script>
                // Initialize the layer dependency graph visualization
                document.addEventListener('DOMContentLoaded', () => {
                    if (!graphData || !graphData.nodes || !graphData.edges) {
                        document.getElementById('layer-graph').innerHTML = 
                            '<div style="text-align: center; padding: 50px;">No graph data available</div>';
                        return;
                    }
                    
                    // Set up dimensions
                    const container = document.getElementById('layer-graph');
                    const width = container.clientWidth;
                    const height = container.clientHeight;
                    
                    // Layer colors
                    const layerColors = {
                        'presentation': '#4caf50',
                        'business': '#2196f3',
                        'data_access': '#ff9800',
                        'domain': '#9c27b0'
                    };
                    
                    // Create SVG container
                    const svg = d3.select('#layer-graph')
                        .append('svg')
                        .attr('width', width)
                        .attr('height', height);
                    
                    // Create a group for the graph
                    const g = svg.append('g');
                    
                    // Add zoom behavior
                    svg.call(d3.zoom()
                        .extent([[0, 0], [width, height]])
                        .scaleExtent([0.5, 5])
                        .on('zoom', (event) => {
                            g.attr('transform', event.transform);
                        })
                    );
                    
                    // Create the simulation
                    const simulation = d3.forceSimulation(graphData.nodes)
                        .force('link', d3.forceLink(graphData.edges)
                            .id(d => d.id)
                            .distance(100))
                        .force('charge', d3.forceManyBody().strength(-300))
                        .force('center', d3.forceCenter(width / 2, height / 2))
                        .force('collision', d3.forceCollide().radius(60));
                    
                    // Add links
                    const link = g.selectAll('.link')
                        .data(graphData.edges)
                        .enter()
                        .append('path')
                        .attr('class', d => `link${d.violation ? ' violation' : ''}`)
                        .attr('marker-end', d => `url(#arrow${d.violation ? '-violation' : ''})`)
                        .style('stroke', d => d.violation ? '#e74c3c' : '#aaa');
                    
                    // Add arrow markers
                    svg.append('defs').selectAll('marker')
                        .data(['arrow', 'arrow-violation'])
                        .enter().append('marker')
                        .attr('id', d => d)
                        .attr('viewBox', '0 -5 10 10')
                        .attr('refX', 20)
                        .attr('refY', 0)
                        .attr('markerWidth', 6)
                        .attr('markerHeight', 6)
                        .attr('orient', 'auto')
                        .append('path')
                        .attr('d', 'M0,-5L10,0L0,5')
                        .style('fill', d => d === 'arrow-violation' ? '#e74c3c' : '#aaa');
                    
                    // Add nodes
                    const node = g.selectAll('.node')
                        .data(graphData.nodes)
                        .enter()
                        .append('g')
                        .attr('class', 'node')
                        .call(d3.drag()
                            .on('start', dragstarted)
                            .on('drag', dragged)
                            .on('end', dragended));
                    
                    // Add circles to nodes
                    node.append('circle')
                        .attr('r', d => 20 + (d.count ? Math.min(Math.sqrt(d.count) * 3, 20) : 0))
                        .style('fill', d => layerColors[d.id] || '#888');
                    
                    // Add labels
                    node.append('text')
                        .attr('dy', 5)
                        .attr('text-anchor', 'middle')
                        .text(d => d.label)
                        .style('fill', '#fff');
                    
                    // Add count labels
                    node.filter(d => d.count > 0)
                        .append('text')
                        .attr('dy', 20)
                        .attr('text-anchor', 'middle')
                        .text(d => `(${d.count})`)
                        .style('fill', '#fff')
                        .style('font-size', '10px');
                    
                    // Update positions on simulation tick
                    simulation.on('tick', () => {
                        link.attr('d', d => {
                            const dx = d.target.x - d.source.x;
                            const dy = d.target.y - d.source.y;
                            const dr = Math.sqrt(dx * dx + dy * dy);
                            
                            // Calculate the offset for the arrow
                            const sourceRadius = 20 + (d.source.count ? Math.min(Math.sqrt(d.source.count) * 3, 20) : 0);
                            const targetRadius = 20 + (d.target.count ? Math.min(Math.sqrt(d.target.count) * 3, 20) : 0);
                            
                            const offsetX = dx * sourceRadius / dr;
                            const offsetY = dy * sourceRadius / dr;
                            
                            const targetOffsetX = dx * targetRadius / dr;
                            const targetOffsetY = dy * targetRadius / dr;
                            
                            return `M${d.source.x + offsetX},${d.source.y + offsetY}L${d.target.x - targetOffsetX},${d.target.y - targetOffsetY}`;
                        });
                        
                        node.attr('transform', d => `translate(${d.x},${d.y})`);
                    });
                    
                    // Drag functions
                    function dragstarted(event, d) {
                        if (!event.active) simulation.alphaTarget(0.3).restart();
                        d.fx = d.x;
                        d.fy = d.y;
                    }
                    
                    function dragged(event, d) {
                        d.fx = event.x;
                        d.fy = event.y;
                    }
                    
                    function dragended(event, d) {
                        if (!event.active) simulation.alphaTarget(0);
                        d.fx = null;
                        d.fy = null;
                    }
                });
            </script>
        '''