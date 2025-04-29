"""
Visualization components for architectural anti-patterns.

This module provides visualization tools specifically designed for
rendering architectural anti-patterns detected by the analyzer.
"""

import os
import json
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

from .architecture_visualizer import ArchitectureVisualizer

class AntiPatternVisualizer(ArchitectureVisualizer):
    """Visualizer for architectural anti-patterns."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the anti-pattern visualizer.
        
        Args:
            output_dir: Directory to save visualization output
        """
        super().__init__(output_dir)
    
    def generate_html(self, analysis_result: Dict[str, Any]) -> str:
        """Generate an HTML visualization for architectural anti-patterns.
        
        Args:
            analysis_result: The analysis result from the anti-pattern detector
            
        Returns:
            HTML content as a string
        """
        # Extract data from the analysis result
        overall_severity = analysis_result.get('overall_severity', 0.0)
        summary = analysis_result.get('summary', '')
        recommendations = analysis_result.get('recommendations', [])
        anti_patterns = analysis_result.get('anti_patterns', {})
        
        # Start building HTML
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<title>Architectural Anti-Pattern Analysis</title>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            self._get_styles(),
            # Include D3.js for visualization
            '<script src="https://d3js.org/d3.v7.min.js"></script>',
            '</head>',
            '<body>',
            '<div class="container">',
            '<h1>Architectural Anti-Pattern Analysis</h1>',
            
            # Overview section
            '<div class="section overview">',
            '<h2>Overview</h2>',
            f'<div class="severity-meter" title="Overall Severity: {overall_severity:.2f}">',
            f'<div class="severity-fill" style="width: {int(overall_severity * 100)}%;"></div>',
            f'<div class="severity-label">{overall_severity:.2f}</div>',
            '</div>',
            f'<div class="summary">{summary}</div>',
            '</div>',
            
            # Anti-pattern details
            '<div class="section">',
            '<h2>Anti-Pattern Analysis</h2>',
            '<div class="anti-patterns-container">',
        ]
        
        # Add each anti-pattern
        for name, pattern_results in anti_patterns.items():
            severity = pattern_results.get('severity', 0.0)
            description = pattern_results.get('description', '')
            violations = pattern_results.get('violations', [])
            pattern_display_name = name.replace('_', ' ').title()
            
            html.extend([
                f'<div class="anti-pattern-card" data-severity="{severity:.2f}">',
                f'<div class="card-header">',
                f'<h3>{pattern_display_name}</h3>',
                f'<div class="severity-badge" style="background-color: {self._get_severity_color(severity)}">',
                f'{int(severity * 100)}%',
                '</div>',
                '</div>',
                f'<div class="card-body">',
                f'<p>{description}</p>',
            ])
            
            # Add violations if present
            if violations:
                html.extend([
                    '<div class="violations-container">',
                    f'<h4>Detected Issues ({len(violations)})</h4>',
                    '<ul class="violations-list">',
                ])
                
                # Show top violations (limit to 5 for readability)
                for violation in violations[:5]:
                    severity = violation.get('severity', 0.0)
                    message = violation.get('message', 'Unknown issue')
                    location = violation.get('location', '')
                    
                    html.append(
                        f'<li class="violation-item">'
                        f'<div class="violation-severity" style="background-color: {self._get_severity_color(severity)}">'
                        f'{int(severity * 100)}%'
                        f'</div>'
                        f'<div class="violation-details">'
                        f'<div class="violation-message">{message}</div>'
                        f'<div class="violation-location">{location}</div>'
                        f'</div>'
                        f'</li>'
                    )
                
                # If there are more violations, add a "Show more" option
                if len(violations) > 5:
                    html.append(f'<li class="show-more">+ {len(violations) - 5} more issues</li>')
                
                html.append('</ul>')
                html.append('</div>')
            
            # Add a placeholder for the visualization
            html.extend([
                '<div class="anti-pattern-visualization" id="visualization-' + name.replace('_', '-') + '"></div>',
                '</div>',  # Close card-body
                '</div>',  # Close anti-pattern-card
            ])
        
        html.append('</div>')  # Close anti-patterns-container
        html.append('</div>')  # Close section
        
        # Add recommendations section
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
        
        # Add visualization data
        html.extend([
            f'<script>const antiPatternData = {json.dumps(anti_patterns)};</script>',
            self._get_visualization_script(),
            '</div>',  # Close container
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html)
    
    def visualize(self, 
                 analysis_result: Dict[str, Any], 
                 filename: str = "architectural_anti_patterns.html") -> str:
        """Generate and save a visualization for architectural anti-patterns.
        
        Args:
            analysis_result: The analysis result from the anti-pattern detector
            filename: Name of the output file
            
        Returns:
            Path to the saved HTML file
        """
        html_content = self.generate_html(analysis_result)
        return self.save_visualization(filename, html_content)
    
    def _get_severity_color(self, severity: float) -> str:
        """Get a color based on severity level.
        
        Args:
            severity: Severity value between 0.0 and 1.0
            
        Returns:
            A CSS color string
        """
        if severity >= 0.8:
            return "#d32f2f"  # Red (severe)
        elif severity >= 0.6:
            return "#f57c00"  # Orange (high)
        elif severity >= 0.4:
            return "#ffa000"  # Amber (moderate)
        elif severity >= 0.2:
            return "#689f38"  # Light green (low)
        else:
            return "#388e3c"  # Green (minimal)
    
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
                
                /* Severity meter */
                .severity-meter {
                    height: 12px;
                    background-color: #e9ecef;
                    border-radius: 6px;
                    overflow: hidden;
                    position: relative;
                    margin: 20px 0;
                }
                
                .severity-fill {
                    height: 100%;
                    border-radius: 6px;
                    transition: width 0.5s ease;
                    background: linear-gradient(90deg, #388e3c, #ffa000, #f57c00, #d32f2f);
                }
                
                .severity-label {
                    position: absolute;
                    top: 0;
                    right: 8px;
                    font-size: 0.8em;
                    font-weight: 600;
                    color: #212529;
                    line-height: 12px;
                }
                
                .summary {
                    margin: 20px 0;
                    font-size: 1.1em;
                    line-height: 1.7;
                }
                
                /* Anti-pattern cards */
                .anti-patterns-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 20px;
                }
                
                .anti-pattern-card {
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }
                
                .anti-pattern-card:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 8px 15px rgba(0,0,0,0.1);
                }
                
                .card-header {
                    padding: 15px 20px;
                    background-color: #f8f9fa;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-bottom: 1px solid #e9ecef;
                }
                
                .card-header h3 {
                    margin: 0;
                    font-size: 1.25em;
                    color: #212529;
                }
                
                .severity-badge {
                    padding: 5px 10px;
                    color: #fff;
                    font-weight: 600;
                    border-radius: 20px;
                    font-size: 0.8em;
                }
                
                .card-body {
                    padding: 20px;
                }
                
                .card-body p {
                    margin-top: 0;
                    color: #495057;
                }
                
                /* Violations list */
                .violations-container {
                    margin-top: 20px;
                }
                
                .violations-container h4 {
                    margin-bottom: 10px;
                    color: #343a40;
                    font-size: 1em;
                }
                
                .violations-list {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    overflow: hidden;
                }
                
                .violation-item {
                    display: flex;
                    padding: 10px;
                    border-bottom: 1px solid #e9ecef;
                }
                
                .violation-item:last-child {
                    border-bottom: none;
                }
                
                .violation-severity {
                    min-width: 40px;
                    height: 24px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: #fff;
                    font-size: 0.8em;
                    font-weight: 600;
                    border-radius: 4px;
                    margin-right: 10px;
                }
                
                .violation-details {
                    flex: 1;
                }
                
                .violation-message {
                    font-weight: 500;
                    color: #343a40;
                }
                
                .violation-location {
                    font-size: 0.85em;
                    color: #6c757d;
                    margin-top: 3px;
                }
                
                .show-more {
                    padding: 10px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 0.9em;
                    cursor: pointer;
                    background-color: #f8f9fa;
                }
                
                /* Anti-pattern visualization */
                .anti-pattern-visualization {
                    height: 200px;
                    background-color: #f8f9fa;
                    border-radius: 4px;
                    margin-top: 20px;
                    border: 1px dashed #dee2e6;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: #6c757d;
                    font-style: italic;
                }
                
                /* Recommendations */
                .recommendations-list {
                    padding-left: 20px;
                    margin: 0;
                }
                
                .recommendations-list li {
                    margin-bottom: 10px;
                    line-height: 1.7;
                }
                
                /* Responsive styles */
                @media (max-width: 768px) {
                    .anti-patterns-container {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        '''
    
    def _get_visualization_script(self) -> str:
        """Get the JavaScript for the anti-pattern visualizations.
        
        Returns:
            JavaScript as a string
        """
        return '''
            <script>
                // Initialize the anti-pattern visualizations
                document.addEventListener('DOMContentLoaded', () => {
                    // For each anti-pattern, create a visualization
                    for (const [name, data] of Object.entries(antiPatternData)) {
                        // Get the visualization container
                        const containerId = 'visualization-' + name.replace(/_/g, '-');
                        const container = document.getElementById(containerId);
                        
                        if (!container) continue;
                        
                        // Check for visualization data
                        if (!data.violations || data.violations.length === 0) {
                            container.textContent = 'No visualization data available';
                            continue;
                        }
                        
                        // Choose the right visualization based on the anti-pattern type
                        switch (name) {
                            case 'dependency_cycle':
                                createCycleVisualization(container, data);
                                break;
                            case 'tight_coupling':
                                createCouplingVisualization(container, data);
                                break;
                            case 'god_component':
                                createGodComponentVisualization(container, data);
                                break;
                            case 'architectural_erosion':
                                createErosionVisualization(container, data);
                                break;
                            default:
                                container.textContent = 'Visualization not implemented for this anti-pattern';
                        }
                    }
                });
                
                // Dependency cycle visualization
                function createCycleVisualization(container, data) {
                    // Placeholder for future implementation
                    container.textContent = 'Dependency cycle visualization will be displayed here';
                    
                    // Implementation would use D3.js to create a directed graph
                    // showing the cycles in the component dependencies
                }
                
                // Tight coupling visualization
                function createCouplingVisualization(container, data) {
                    // Placeholder for future implementation
                    container.textContent = 'Tight coupling visualization will be displayed here';
                    
                    // Implementation would use D3.js to create a heat map or network
                    // diagram showing component coupling
                }
                
                // God component visualization
                function createGodComponentVisualization(container, data) {
                    // Placeholder for future implementation
                    container.textContent = 'God component visualization will be displayed here';
                    
                    // Implementation would use D3.js to create a circle packing diagram
                    // or treemap showing component sizes and responsibilities
                }
                
                // Architectural erosion visualization
                function createErosionVisualization(container, data) {
                    // Placeholder for future implementation
                    container.textContent = 'Architectural erosion visualization will be displayed here';
                    
                    // Implementation would use D3.js to create a visualization showing
                    // architectural violations over different components
                }
            </script>
        '''