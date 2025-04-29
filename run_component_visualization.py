#!/usr/bin/env python3
"""
Run component visualization with advanced visualization tools.

This script analyzes code components and their relationships, then generates an
interactive visualization showing the connections between components.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analyzer import CodeAnalyzer
from src.visualization import ForceDirectedVisualizer
from src.mock_implementation import patch_analyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Visualize components and their relationships in a project"
    )
    parser.add_argument(
        "path",
        help="Path to the directory to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file name (default: component_visualization.html)",
        default="component_visualization.html"
    )
    parser.add_argument(
        "--output-dir", "-d",
        help="Output directory (default: reports)",
        default="reports"
    )
    parser.add_argument(
        "--style", "-s",
        choices=["layered", "hexagonal", "clean", "event_driven", "microservices"],
        default="layered",
        help="Architectural style to analyze (default: layered)"
    )
    parser.add_argument(
        "--title", "-t",
        help="Title for the visualization",
        default="Component Relationship Analysis"
    )
    parser.add_argument(
        "--open", "-p",
        action="store_true",
        help="Open the visualization in a browser after generation"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock implementation for testing"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Force use of real Tree-sitter implementation"
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated list of directories to exclude",
        default="node_modules,venv,.git,__pycache__,dist,build"
    )
    parser.add_argument(
        "--extensions", "-e",
        help="Comma-separated list of file extensions to analyze (e.g. .py,.js)",
    )
    
    args = parser.parse_args()
    
    # Determine if we should use mock implementation
    use_mock = True
    if args.real:
        use_mock = False
    elif args.mock:
        use_mock = True
    else:
        # Default based on environment
        use_mock = os.environ.get('CODE_PATTERN_USE_MOCK', 'True').lower() in ('true', '1', 'yes')
    
    # Set up the mock implementation if needed
    if use_mock:
        logger.info("Using mock implementation")
        restore_original = patch_analyzer()
    else:
        logger.info("Using tree-sitter implementation")
        restore_original = lambda: None
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        output_path = os.path.join(args.output_dir, args.output)
        
        # Parse exclude directories
        exclude_dirs = args.exclude.split(',') if args.exclude else []
        
        # Parse file extensions
        file_extensions = None
        if args.extensions:
            file_extensions = args.extensions.split(',')
            # Ensure extensions start with a dot
            file_extensions = [(("." + ext) if not ext.startswith(".") else ext) for ext in file_extensions]
        
        # Initialize analyzer
        analyzer = CodeAnalyzer(use_mock=use_mock)
        logger.info(f"Analyzing components in {args.path}")
        
        # Analyze the directory
        file_results = analyzer.analyze_directory(
            args.path,
            exclude_dirs=exclude_dirs,
            file_extensions=file_extensions
        )
        
        # Analyze components and relationships based on the architectural style
        graph_data = {}
        
        if args.style == "layered":
            from src.patterns.architectural_styles import LayeredArchitectureDetector
            detector = LayeredArchitectureDetector()
            analysis_result = detector.analyze(file_results, args.path)
            graph_data = analysis_result.get('layered_architecture_graph', {})
        elif args.style == "hexagonal":
            from src.patterns.architectural_styles import HexagonalArchitectureDetector
            detector = HexagonalArchitectureDetector()
            analysis_result = detector.analyze(file_results, args.path)
            graph_data = analysis_result.get('hexagonal_architecture_graph', {})
        elif args.style == "clean":
            from src.patterns.architectural_styles import CleanArchitectureDetector
            detector = CleanArchitectureDetector()
            analysis_result = detector.analyze(file_results, args.path)
            graph_data = analysis_result.get('clean_architecture_graph', {})
        elif args.style == "event_driven":
            from src.patterns.architectural_styles import EventDrivenArchitectureDetector
            detector = EventDrivenArchitectureDetector()
            analysis_result = detector.analyze(file_results, args.path)
            graph_data = analysis_result.get('event_driven_architecture_graph', {})
        elif args.style == "microservices":
            from src.patterns.architectural_styles import MicroservicesArchitectureDetector
            detector = MicroservicesArchitectureDetector()
            analysis_result = detector.analyze(file_results, args.path)
            graph_data = analysis_result.get('microservices_architecture_graph', {})
        
        # Add components and relationships to graph data if not provided by detector
        if not graph_data or not graph_data.get('nodes'):
            logger.info("Creating graph data from file analysis")
            
            # Create a basic graph from file analysis
            graph_data = {
                "nodes": [],
                "links": []
            }
            
            # Create node for each file
            file_id_map = {}
            for i, result in enumerate(file_results):
                file_path = result.get('file', '')
                if not file_path or 'error' in result:
                    continue
                    
                # Extract components from file
                components = []
                for pattern_name, matches in result.get('patterns', {}).items():
                    if pattern_name in ['class_definition', 'function_definition']:
                        components.extend(matches)
                
                # Create a node for the file
                file_id = f"file_{i}"
                file_id_map[file_path] = file_id
                
                # Determine type based on file extension
                file_type = Path(file_path).suffix.lstrip('.')
                
                graph_data["nodes"].append({
                    "id": file_id,
                    "name": os.path.basename(file_path),
                    "file": file_path,
                    "type": file_type,
                    "components": len(components)
                })
                
                # Create links based on imports or includes
                # NOTE: This requires additional analysis in a real implementation
            
            # Add sample relationships (in a real implementation, these would be detected)
            # This is a placeholder for demonstration
            if len(graph_data["nodes"]) > 1:
                for i in range(min(len(graph_data["nodes"]) - 1, 10)):
                    graph_data["links"].append({
                        "source": graph_data["nodes"][i]["id"],
                        "target": graph_data["nodes"][i+1]["id"],
                        "type": "imports"
                    })
        
        # Create visualization
        logger.info("Generating component visualization")
        visualizer = ForceDirectedVisualizer(args.output_dir)
        
        # Prepare visualization data
        visualization_data = {
            "nodes": graph_data.get("nodes", []),
            "links": graph_data.get("links", []) or graph_data.get("edges", [])
        }
        
        # Generate the visualization
        output_file = visualizer.visualize(
            visualization_data,
            title=args.title,
            description=f"Architectural style: {args.style.replace('_', ' ').title()}",
            filename=args.output
        )
        
        logger.info(f"Visualization saved to: {output_file}")
        
        # Open in browser if requested
        if args.open:
            from src.visualization.visualization_utilities import open_visualization_in_browser
            open_visualization_in_browser(output_file)
        
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Restore original implementation if patched
        restore_original()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())