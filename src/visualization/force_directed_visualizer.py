"""
Force-directed graph visualization for architectural components.

This module provides an advanced D3.js-based visualization for architectural
components and their relationships, making it easier to understand complex
dependencies and structures.
"""

import os
import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

from .architecture_visualizer import ArchitectureVisualizer

class ForceDirectedVisualizer(ArchitectureVisualizer):
    """Visualizer for component relationships using force-directed graphs."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the force-directed graph visualizer.
        
        Args:
            output_dir: Directory to save visualization output
        """
        super().__init__(output_dir)
    
    def generate_html(self, 
                     graph_data: Dict[str, Any], 
                     title: str = "Component Relationships",
                     description: str = "") -> str:
        """Generate an HTML visualization with a force-directed graph.
        
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
            '</head>',
            '<body>',
            '<div class="container">',
            f'<h1>{title}</h1>',
            
            # Description
            f'<div class="description">{description}</div>',
            
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
            
            # Component details panel
            '<div class="details-panel" id="details-panel">',
            '<div class="details-header">',
            '<h3>Component Details</h3>',
            '<button class="close-btn">&times;</button>',
            '</div>',
            '<div class="details-content">',
            '<p>Select a component to view details</p>',
            '</div>',
            '</div>',
            
            # Add the graph data
            f'<script>const graphData = {json.dumps(graph_data)};</script>',
            self._get_visualization_script(),
            
            '</div>', # Close container
            '</body>',
            '</html>'
        ]
        
        return '\n'.join(html)
    
    def visualize(self, 
                 graph_data: Dict[str, Any], 
                 title: str = "Component Relationships",
                 description: str = "",
                 filename: str = "component_graph.html") -> str:
        """Generate and save a force-directed graph visualization.
        
        Args:
            graph_data: Dictionary containing nodes and links for the graph
            title: Title for the visualization
            description: Description text for the visualization
            filename: Name of the output file
            
        Returns:
            Path to the saved HTML file
        """
        html_content = self.generate_html(graph_data, title, description)
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
                    background-color: #f9fafc;
                    color: #343a40;
                }
                
                .container {
                    max-width: 1200px;
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
                
                /* Controls */
                .controls {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    background-color: #fff;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
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
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    height: 600px;
                    margin-bottom: 20px;
                    position: relative;
                    overflow: hidden;
                }
                
                /* Legend */
                .legend {
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    padding: 15px;
                    margin-bottom: 20px;
                }
                
                .legend-title {
                    font-weight: 600;
                    margin-bottom: 10px;
                }
                
                .legend-items {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                }
                
                .legend-item {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }
                
                .legend-color {
                    width: 15px;
                    height: 15px;
                    border-radius: 3px;
                }
                
                /* Details panel */
                .details-panel {
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
                    width: 300px;
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 1000;
                    transform: translateX(350px);
                    transition: transform 0.3s ease;
                }
                
                .details-panel.visible {
                    transform: translateX(0);
                }
                
                .details-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 15px;
                    border-bottom: 1px solid #e9ecef;
                }
                
                .details-header h3 {
                    margin: 0;
                    font-size: 1.1em;
                    color: #212529;
                }
                
                .close-btn {
                    background: none;
                    border: none;
                    font-size: 1.5em;
                    color: #6c757d;
                    cursor: pointer;
                }
                
                .details-content {
                    padding: 15px;
                }
                
                .details-field {
                    margin-bottom: 10px;
                }
                
                .details-field-label {
                    font-weight: 600;
                    color: #495057;
                    font-size: 0.9em;
                }
                
                .details-field-value {
                    color: #212529;
                }
                
                /* Node and link styles (for D3) */
                .node circle {
                    stroke: #fff;
                    stroke-width: 2px;
                }
                
                .node text {
                    font-size: 10px;
                    fill: #212529;
                    text-anchor: middle;
                    pointer-events: none;
                }
                
                .node.selected circle {
                    stroke: #ffc107;
                    stroke-width: 3px;
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
                @media (max-width: 768px) {
                    .controls {
                        flex-direction: column;
                        align-items: flex-start;
                    }
                    
                    .graph-container {
                        height: 400px;
                    }
                    
                    .details-panel {
                        width: 90%;
                        max-width: 300px;
                        right: 5%;
                    }
                }
            </style>
        '''
    
    def _get_visualization_script(self) -> str:
        """Get the JavaScript for the force-directed graph visualization.
        
        Returns:
            JavaScript as a string
        """
        return '''
            <script>
                // Initialize the force-directed graph visualization
                document.addEventListener('DOMContentLoaded', () => {
                    // Check if we have data
                    if (!graphData || !graphData.nodes || !graphData.links) {
                        document.getElementById('graph').innerHTML = 
                            '<div style="text-align: center; padding: 50px;">No graph data available</div>';
                        return;
                    }
                    
                    // Initialize the visualization
                    const visualization = new ForceDirectedGraph('graph', 'legend', 'details-panel');
                    
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
                
                // Force-directed graph visualization class
                class ForceDirectedGraph {
                    constructor(containerId, legendId, detailsPanelId) {
                        // Store element IDs
                        this.containerId = containerId;
                        this.legendId = legendId;
                        this.detailsPanelId = detailsPanelId;
                        
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
                        
                        // Initialize the details panel
                        this.detailsPanel = document.getElementById(detailsPanelId);
                        this.detailsPanel.querySelector('.close-btn').addEventListener('click', () => {
                            this.hideDetailsPanel();
                        });
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
                            .on('click', this.nodeClicked.bind(this));
                        
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
                    
                    // Handle node click
                    nodeClicked(event, d) {
                        // Deselect previous node
                        if (this.selectedNode) {
                            d3.select(this.selectedNode).classed('selected', false);
                        }
                        
                        // Select this node
                        this.selectedNode = event.currentTarget;
                        d3.select(this.selectedNode).classed('selected', true);
                        
                        // Show details
                        this._showNodeDetails(d);
                    }
                    
                    // Show node details in the panel
                    _showNodeDetails(node) {
                        const content = this.detailsPanel.querySelector('.details-content');
                        
                        // Clear previous content
                        content.innerHTML = '';
                        
                        // Create fields
                        const fields = [
                            { label: 'Name', value: node.name || node.id },
                            { label: 'Type', value: node.type || 'Unknown' },
                            { label: 'Layer', value: (node.layer || 'Unknown').replace('_', ' ').toUpperCase() },
                            { label: 'File', value: node.file || 'Unknown' },
                            { label: 'Connections', value: this._getNodeConnections(node) }
                        ];
                        
                        // Add fields to content
                        fields.forEach(field => {
                            const fieldEl = document.createElement('div');
                            fieldEl.className = 'details-field';
                            
                            const labelEl = document.createElement('div');
                            labelEl.className = 'details-field-label';
                            labelEl.textContent = field.label;
                            
                            const valueEl = document.createElement('div');
                            valueEl.className = 'details-field-value';
                            valueEl.textContent = field.value;
                            
                            fieldEl.appendChild(labelEl);
                            fieldEl.appendChild(valueEl);
                            content.appendChild(fieldEl);
                        });
                        
                        // Show the panel
                        this.detailsPanel.classList.add('visible');
                    }
                    
                    // Get number of connections for a node
                    _getNodeConnections(node) {
                        let count = 0;
                        
                        this.filteredLinks.forEach(link => {
                            if (link.source.id === node.id || link.target.id === node.id) {
                                count++;
                            }
                        });
                        
                        return count.toString();
                    }
                    
                    // Hide the details panel
                    hideDetailsPanel() {
                        // Deselect the node
                        if (this.selectedNode) {
                            d3.select(this.selectedNode).classed('selected', false);
                            this.selectedNode = null;
                        }
                        
                        // Hide the panel
                        this.detailsPanel.classList.remove('visible');
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