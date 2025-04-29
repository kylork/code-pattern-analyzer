"""
Visualization components for the code pattern analyzer.
"""

import os
import json
from typing import Dict, List, Optional, Union

class HTMLReport:
    """Generate HTML reports with interactive visualizations."""
    
    def __init__(self, 
                 title: str = "Code Pattern Analysis Report", 
                 include_charts: bool = True):
        """Initialize the HTML report generator.
        
        Args:
            title: Title for the report
            include_charts: Whether to include charts
        """
        self.title = title
        self.include_charts = include_charts
        
    def generate(self, results: List[Dict]) -> str:
        """Generate an HTML report from analysis results.
        
        Args:
            results: List of analysis results
            
        Returns:
            HTML report as a string
        """
        # Start with the HTML header
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            f'<title>{self.title}</title>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            self._get_styles(),
        ]
        
        # Add chart.js if needed
        if self.include_charts:
            html.append('<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>')
        
        html.extend([
            '</head>',
            '<body>',
            f'<h1>{self.title}</h1>',
        ])
        
        # Add summary section if more than one file
        if len(results) > 1:
            html.append(self._generate_summary_section(results))
        
        # Process each file
        for result in results:
            html.append(self._generate_file_section(result))
        
        # Add JavaScript for interactivity
        html.append(self._get_scripts())
        
        # Close the HTML
        html.extend([
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html)
    
    def _generate_summary_section(self, results: List[Dict]) -> str:
        """Generate a summary section for multiple files.
        
        Args:
            results: List of analysis results
            
        Returns:
            HTML for the summary section
        """
        # Count patterns across all files
        total_patterns = 0
        pattern_counts = {}
        type_counts = {}
        language_counts = {}
        files_count = 0
        error_count = 0
        
        for result in results:
            if "error" in result:
                error_count += 1
                continue
                
            files_count += 1
            
            if "language" in result:
                language = result["language"]
                language_counts[language] = language_counts.get(language, 0) + 1
            
            if "summary" in result:
                summary = result["summary"]
                total_patterns += summary.get("total_patterns", 0)
                
                # Update pattern counts
                for pattern, count in summary.get("pattern_counts", {}).items():
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + count
                
                # Update type counts
                for type_name, count in summary.get("type_counts", {}).items():
                    type_counts[type_name] = type_counts.get(type_name, 0) + count
        
        # Generate the summary HTML
        html = [
            '<div class="summary-section">',
            '<h2>Summary</h2>',
            '<div class="summary-stats">',
            f'<div class="stat-box"><div class="stat-value">{files_count}</div><div class="stat-label">Files Analyzed</div></div>',
            f'<div class="stat-box"><div class="stat-value">{total_patterns}</div><div class="stat-label">Patterns Detected</div></div>',
        ]
        
        if error_count > 0:
            html.append(f'<div class="stat-box error"><div class="stat-value">{error_count}</div><div class="stat-label">Errors</div></div>')
        
        html.append('</div>')  # Close summary-stats
        
        # Add charts if requested
        if self.include_charts and total_patterns > 0:
            # Add pattern distribution chart
            if pattern_counts:
                chart_id = "patternDistributionChart"
                chart_data = json.dumps({
                    "labels": list(pattern_counts.keys()),
                    "values": list(pattern_counts.values())
                })
                
                html.extend([
                    '<div class="chart-container">',
                    f'<h3>Pattern Distribution</h3>',
                    f'<canvas id="{chart_id}"></canvas>',
                    f'<script>var {chart_id}Data = {chart_data};</script>',
                    '</div>'
                ])
            
            # Add type distribution chart
            if type_counts:
                chart_id = "typeDistributionChart"
                chart_data = json.dumps({
                    "labels": list(type_counts.keys()),
                    "values": list(type_counts.values())
                })
                
                html.extend([
                    '<div class="chart-container">',
                    f'<h3>Type Distribution</h3>',
                    f'<canvas id="{chart_id}"></canvas>',
                    f'<script>var {chart_id}Data = {chart_data};</script>',
                    '</div>'
                ])
            
            # Add language distribution chart
            if language_counts:
                chart_id = "languageDistributionChart"
                chart_data = json.dumps({
                    "labels": list(language_counts.keys()),
                    "values": list(language_counts.values())
                })
                
                html.extend([
                    '<div class="chart-container">',
                    f'<h3>Language Distribution</h3>',
                    f'<canvas id="{chart_id}"></canvas>',
                    f'<script>var {chart_id}Data = {chart_data};</script>',
                    '</div>'
                ])
        
        # Close the summary section
        html.append('</div>')
        
        return '\n'.join(html)
    
    def _generate_file_section(self, result: Dict) -> str:
        """Generate a section for a single file.
        
        Args:
            result: Analysis result for a single file
            
        Returns:
            HTML for the file section
        """
        html = [f'<div class="file-section" id="file-{self._to_id(result["file"])}">']
        
        # Handle errors
        if "error" in result:
            html.extend([
                f'<h2>{result["file"]}</h2>',
                f'<div class="error-box">Error: {result["error"]}</div>',
                '</div>'  # Close file-section
            ])
            return '\n'.join(html)
        
        # File header
        html.extend([
            f'<h2>{result["file"]}</h2>',
            f'<div class="file-info">',
            f'<span class="language-badge">{result["language"]}</span>',
        ])
        
        # Add file stats
        if "summary" in result:
            summary = result["summary"]
            
            html.extend([
                f'<span class="pattern-count">{summary["total_patterns"]} patterns</span>',
                '</div>',  # Close file-info
                '<div class="file-summary">',
            ])
            
            # Add summary details
            if summary["pattern_counts"]:
                html.append('<h3>Pattern Distribution</h3>')
                html.append('<ul class="pattern-list">')
                
                for pattern, count in summary["pattern_counts"].items():
                    html.append(f'<li><span class="pattern-name">{pattern}</span>: <span class="pattern-count">{count}</span></li>')
                
                html.append('</ul>')
            
            # Add chart if requested
            if self.include_charts and summary["total_patterns"] > 0:
                file_id = self._to_id(result["file"])
                chart_id = f"chart-{file_id}"
                chart_data = json.dumps({
                    "labels": list(summary["pattern_counts"].keys()),
                    "values": list(summary["pattern_counts"].values())
                })
                
                html.extend([
                    '<div class="chart-container">',
                    f'<canvas id="{chart_id}"></canvas>',
                    f'<script>var {chart_id}Data = {chart_data};</script>',
                    '</div>'
                ])
            
            html.append('</div>')  # Close file-summary
        else:
            html.append('</div>')  # Close file-info
        
        # Show pattern details
        if "patterns" in result and result["patterns"]:
            html.append('<div class="patterns-container">')
            
            for pattern_name, matches in result["patterns"].items():
                html.extend([
                    f'<div class="pattern-group" id="pattern-{self._to_id(pattern_name)}">',
                    f'<h3 class="pattern-header" onclick="togglePattern(\'{self._to_id(pattern_name)}\')">',
                    f'<span class="expand-icon">▶</span> {pattern_name} ({len(matches)})',
                    '</h3>',
                    f'<div class="pattern-matches" id="matches-{self._to_id(pattern_name)}">',
                ])
                
                # Show the matches
                for match in matches:
                    html.extend([
                        '<div class="match">',
                        f'<div class="match-header">{match.get("name", "Unnamed")}',
                    ])
                    
                    if "type" in match:
                        html.append(f' <span class="match-type">({match["type"]})</span>')
                    
                    if "line" in match:
                        html.append(f' <span class="match-line">Line {match["line"]}</span>')
                    
                    html.append('</div>')  # Close match-header
                    
                    # Add match details
                    html.append('<div class="match-details">')
                    
                    for key, value in match.items():
                        if key in ("name", "type", "line", "column", "file"):
                            continue
                            
                        if isinstance(value, dict):
                            html.append(f'<div class="match-detail"><span class="detail-key">{key}</span>: <pre>{json.dumps(value, indent=2)}</pre></div>')
                        else:
                            html.append(f'<div class="match-detail"><span class="detail-key">{key}</span>: {value}</div>')
                    
                    html.append('</div>')  # Close match-details
                    html.append('</div>')  # Close match
                
                html.extend([
                    '</div>',  # Close pattern-matches
                    '</div>',  # Close pattern-group
                ])
            
            html.append('</div>')  # Close patterns-container
        
        html.append('</div>')  # Close file-section
        
        return '\n'.join(html)
    
    def _to_id(self, text: str) -> str:
        """Convert text to a valid HTML ID.
        
        Args:
            text: Text to convert
            
        Returns:
            Valid HTML ID
        """
        # Remove invalid characters and replace spaces
        return "".join(c if c.isalnum() else "-" for c in text)
    
    def _get_styles(self) -> str:
        """Get the CSS styles for the report.
        
        Returns:
            CSS styles as a string
        """
        return '''
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    color: #333;
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                h1 {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #eee;
                }
                h2 {
                    margin-top: 30px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }
                
                /* Summary styles */
                .summary-section {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    padding: 20px;
                    margin-bottom: 30px;
                }
                .summary-stats {
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    margin: 20px 0;
                }
                .stat-box {
                    text-align: center;
                    padding: 15px;
                    border-radius: 8px;
                    background-color: #f1f8ff;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    min-width: 150px;
                    margin: 10px;
                }
                .stat-value {
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #2980b9;
                }
                .stat-label {
                    font-size: 0.9em;
                    color: #7f8c8d;
                    text-transform: uppercase;
                }
                .error .stat-value {
                    color: #e74c3c;
                }
                
                /* File section styles */
                .file-section {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    padding: 20px;
                    margin-bottom: 30px;
                }
                .file-info {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .language-badge {
                    background-color: #3498db;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 0.9em;
                    margin-right: 15px;
                }
                .pattern-count {
                    color: #7f8c8d;
                }
                .file-summary {
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                
                /* Pattern styles */
                .pattern-group {
                    margin-bottom: 15px;
                    border: 1px solid #eee;
                    border-radius: 4px;
                }
                .pattern-header {
                    background-color: #f5f5f5;
                    padding: 10px 15px;
                    margin: 0;
                    cursor: pointer;
                    border-radius: 4px 4px 0 0;
                }
                .pattern-header:hover {
                    background-color: #ebebeb;
                }
                .expand-icon {
                    display: inline-block;
                    transition: transform 0.2s;
                    margin-right: 10px;
                }
                .pattern-matches {
                    display: none;
                    padding: 0 15px;
                }
                .pattern-list {
                    list-style-type: none;
                    padding-left: 0;
                }
                .pattern-list li {
                    padding: 5px 0;
                    border-bottom: 1px solid #f5f5f5;
                }
                .pattern-name {
                    font-weight: bold;
                }
                
                /* Match styles */
                .match {
                    margin: 15px 0;
                    padding: 10px;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                }
                .match-header {
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .match-type {
                    color: #7f8c8d;
                    font-weight: normal;
                }
                .match-line {
                    color: #e74c3c;
                    font-weight: normal;
                    float: right;
                }
                .match-details {
                    font-size: 0.9em;
                    color: #555;
                }
                .match-detail {
                    margin: 5px 0;
                }
                .detail-key {
                    color: #2980b9;
                    font-weight: bold;
                }
                .error-box {
                    background-color: #ffecec;
                    color: #e74c3c;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 15px;
                }
                
                /* Chart styles */
                .chart-container {
                    margin: 20px 0;
                    height: 300px;
                }
                
                /* Responsive styles */
                @media (max-width: 768px) {
                    .stat-box {
                        min-width: 120px;
                    }
                    .chart-container {
                        height: 250px;
                    }
                }
            </style>
        '''
    
    def _get_scripts(self) -> str:
        """Get the JavaScript for the report.
        
        Returns:
            JavaScript as a string
        """
        scripts = '''
            <script>
                // Toggle pattern matches visibility
                function togglePattern(patternId) {
                    const matches = document.getElementById('matches-' + patternId);
                    const header = document.querySelector('#pattern-' + patternId + ' .pattern-header');
                    const icon = header.querySelector('.expand-icon');
                    
                    if (matches.style.display === 'block') {
                        matches.style.display = 'none';
                        icon.style.transform = 'rotate(0deg)';
                    } else {
                        matches.style.display = 'block';
                        icon.style.transform = 'rotate(90deg)';
                    }
                }
                
                // Initialize all patterns as collapsed
                document.addEventListener('DOMContentLoaded', () => {
                    const patterns = document.querySelectorAll('.pattern-group');
                    patterns.forEach(pattern => {
                        const patternId = pattern.id.replace('pattern-', '');
                        const matches = document.getElementById('matches-' + patternId);
                        if (matches) {
                            matches.style.display = 'none';
                        }
                    });
                });
            </script>
        '''
        
        # Add chart initialization if needed
        if self.include_charts:
            scripts += '''
                <script>
                    // Initialize charts
                    document.addEventListener('DOMContentLoaded', () => {
                        // Helper function to create colors
                        function getColors(count) {
                            const colors = [
                                '#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
                                '#1abc9c', '#d35400', '#34495e', '#16a085', '#27ae60',
                                '#2980b9', '#8e44ad', '#f1c40f', '#e67e22', '#c0392b'
                            ];
                            
                            // If we need more colors than available, cycle through them
                            const result = [];
                            for (let i = 0; i < count; i++) {
                                result.push(colors[i % colors.length]);
                            }
                            return result;
                        }
                        
                        // Helper function to create a chart
                        function createChart(id, data, type = 'pie') {
                            const ctx = document.getElementById(id);
                            if (!ctx) return;
                            
                            const colors = getColors(data.labels.length);
                            
                            new Chart(ctx, {
                                type: type,
                                data: {
                                    labels: data.labels,
                                    datasets: [{
                                        data: data.values,
                                        backgroundColor: colors,
                                        borderColor: colors,
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: 'right',
                                        }
                                    }
                                }
                            });
                        }
                        
                        // Create summary charts
                        if (typeof patternDistributionChartData !== 'undefined') {
                            createChart('patternDistributionChart', patternDistributionChartData);
                        }
                        
                        if (typeof typeDistributionChartData !== 'undefined') {
                            createChart('typeDistributionChart', typeDistributionChartData);
                        }
                        
                        if (typeof languageDistributionChartData !== 'undefined') {
                            createChart('languageDistributionChart', languageDistributionChartData);
                        }
                        
                        // Create file charts
                        const fileCharts = document.querySelectorAll('[id^="chart-"]');
                        fileCharts.forEach(chart => {
                            const chartId = chart.id;
                            const dataVar = chartId + 'Data';
                            
                            if (typeof window[dataVar] !== 'undefined') {
                                createChart(chartId, window[dataVar], 'bar');
                            }
                        });
                    });
                </script>
            '''
        
        return scripts