#!/usr/bin/env python3
"""
Script to generate interactive component relationship visualizations.

This script analyzes a codebase and generates an interactive force-directed
graph visualization of component relationships, making it easier to understand
the architecture.
"""

import argparse
import os
import sys
import logging
from pathlib import Path

from src.analyzer import CodeAnalyzer
from src.patterns.architectural_styles.architectural_style_detector import ArchitecturalStyleDetector
from src.visualization.force_directed_visualizer import ForceDirectedVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main():
    """Generate an interactive component visualization."""
    parser = argparse.ArgumentParser(description='Generate interactive component visualizations')
    parser.add_argument('directory', help='Directory to analyze')
    parser.add_argument('--output', '-o', default='component_graph.html', help='Output HTML file')
    parser.add_argument('--output-dir', '-d', default='reports', help='Output directory')
    parser.add_argument('--title', default='Component Relationships', help='Visualization title')
    parser.add_argument('--style', choices=['layered', 'hexagonal', 'clean', 'event_driven', 'microservices'], 
                        default='layered', help='Architectural style to visualize')
    parser.add_argument('--mock', action='store_true', help='Use mock implementation')
    
    args = parser.parse_args()
    
    try:
        # Validate directory
        directory = Path(args.directory)
        if not directory.is_dir():
            logger.error(f"Directory not found: {directory}")
            return 1
        
        # Create analyzer
        logger.info(f"Analyzing directory: {directory}")
        analyzer = CodeAnalyzer(use_mock=args.mock)
        
        # Analyze directory
        results = analyzer.analyze_directory(directory)
        
        # Create style detector
        logger.info(f"Detecting {args.style} architectural style")
        style_detector = ArchitecturalStyleDetector()
        
        # Get the specific style analyzer
        style_analyzers = {
            'layered': style_detector.patterns[0],       # LayeredArchitecturePattern
            'hexagonal': style_detector.patterns[1],     # HexagonalArchitecturePattern
            'clean': style_detector.patterns[2],         # CleanArchitecturePattern
            'event_driven': style_detector.patterns[3],  # EventDrivenArchitecturePattern
            'microservices': style_detector.patterns[4], # MicroservicesArchitecturePattern
        }
        
        style_analyzer = style_analyzers.get(args.style)
        if not style_analyzer:
            logger.error(f"Style not found: {args.style}")
            return 1
        
        # Analyze architecture
        architecture_result = style_analyzer.analyze_architecture(results, {})
        
        # Get component graph from analysis
        component_graph = style_analyzer.component_graph
        
        # Prepare graph data for visualization
        graph_data = {
            'nodes': [],
            'links': []
        }
        
        # Add nodes
        for node_id, data in component_graph.nodes(data=True):
            node_data = {
                'id': node_id,
                'name': data.get('name', os.path.basename(node_id)),
                'type': data.get('type', 'unknown'),
                'layer': data.get('layer', 'unknown'),
                'file': data.get('file', '')
            }
            graph_data['nodes'].append(node_data)
        
        # Add links
        for source, target, data in component_graph.edges(data=True):
            link_data = {
                'source': source,
                'target': target,
                'type': data.get('type', 'dependency'),
                'violation': data.get('violation', False)
            }
            graph_data['links'].append(link_data)
        
        # Create description
        description = f"This visualization shows the components and their relationships in the {args.style.replace('_', ' ')} architecture detected in {directory}."
        
        # Create visualizer and ensure output directory exists
        logger.info("Generating visualization")
        visualizer = ForceDirectedVisualizer(output_dir=args.output_dir)
        
        # Make sure the output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        output_path = visualizer.visualize(
            graph_data,
            title=args.title,
            description=description,
            filename=args.output
        )
        
        logger.info(f"Visualization saved to: {output_path}")
        return 0
        
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())