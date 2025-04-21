#!/usr/bin/env python3
"""
Script to visualize layered architecture analysis results.

This script demonstrates the visualization capabilities for the
enhanced layered architecture detector.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("visualize_layered")

# Add the source directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import required modules
from src.patterns.architectural_styles import LayeredArchitecturePattern
from src.visualization import LayeredArchitectureVisualizer

def visualize_layered_architecture():
    """Generate and save a visualization for layered architecture analysis."""
    # Run the layered architecture detector (copy logic from debug script)
    # Create the layered architecture pattern
    pattern = LayeredArchitecturePattern()
    
    # Path to the example layered architecture code
    example_path = Path("examples/layered_architecture")
    
    # Create a directed graph manually based on our example files
    example_files = {
        'controllers': [
            'examples/layered_architecture/controllers/user_controller.py',
        ],
        'services': [
            'examples/layered_architecture/services/user_service.py',
        ],
        'repositories': [
            'examples/layered_architecture/repositories/user_repository.py',
        ],
        'models': [
            'examples/layered_architecture/models/user.py',
        ]
    }
    
    # Create mock results with the appropriate structure
    results = []
    for layer, files in example_files.items():
        for file_path in files:
            # Determine the layer based on directory name
            layer_map = {
                'controllers': 'presentation',
                'services': 'business',
                'repositories': 'data_access',
                'models': 'domain'
            }
            actual_layer = layer_map.get(layer, '')
            
            # Create a mock file analysis result
            result = {
                'file': file_path,
                'patterns': {
                    'class_definition': [
                        {
                            'name': Path(file_path).stem.capitalize(),
                            'type': 'class_definition',
                            'layer': actual_layer,
                            'line': 1
                        }
                    ],
                    'function_definition': [
                        {
                            'name': f'some_method',
                            'type': 'function_definition',
                            'line': 10
                        }
                    ]
                }
            }
            results.append(result)
    
    # Build the component graph
    logger.info(f"Building component graph from {len(results)} results")
    pattern._build_component_graph(results)
    
    # Add layer dependencies manually to simulate import detection
    pattern.layer_dependencies = {
        'presentation': {'business', 'domain'},
        'business': {'data_access', 'domain'},
        'data_access': {'domain', 'business'},  # This includes an upward dependency (violation)
        'domain': {'business'}  # This is an upward dependency (violation)
    }
    
    # Add specific dependency violations for detailed reporting
    pattern.dependency_violations = [
        {
            'source_layer': 'domain',
            'target_layer': 'business',
            'source_file': 'examples/layered_architecture/models/user.py',
            'target_file': 'examples/layered_architecture/services/user_service.py',
            'line': 12,
            'message': 'Upward dependency from domain to business'
        },
        {
            'source_layer': 'data_access',
            'target_layer': 'business',
            'source_file': 'examples/layered_architecture/repositories/user_repository.py',
            'target_file': 'examples/layered_architecture/services/user_service.py',
            'line': 15,
            'message': 'Upward dependency from data_access to business'
        }
    ]
    
    # Create a more realistic component graph with edges
    for violation in pattern.dependency_violations:
        source_id = f"{violation['source_file']}::module"
        target_id = f"{violation['target_file']}::module"
        
        # Ensure nodes exist
        if not pattern.component_graph.has_node(source_id):
            pattern.component_graph.add_node(
                source_id, 
                file=violation['source_file'], 
                layer=violation['source_layer'],
                type='module'
            )
        
        if not pattern.component_graph.has_node(target_id):
            pattern.component_graph.add_node(
                target_id, 
                file=violation['target_file'], 
                layer=violation['target_layer'],
                type='module'
            )
        
        # Add edge with violation flag
        pattern.component_graph.add_edge(
            source_id, target_id, 
            type='import', 
            violation=True
        )
    
    # Add valid dependency edges
    valid_deps = [
        # Controller to Service (presentation -> business)
        ('examples/layered_architecture/controllers/user_controller.py', 'examples/layered_architecture/services/user_service.py'),
        # Controller to Model (presentation -> domain)
        ('examples/layered_architecture/controllers/user_controller.py', 'examples/layered_architecture/models/user.py'),
        # Service to Repository (business -> data_access)
        ('examples/layered_architecture/services/user_service.py', 'examples/layered_architecture/repositories/user_repository.py'),
        # Service to Model (business -> domain)
        ('examples/layered_architecture/services/user_service.py', 'examples/layered_architecture/models/user.py'),
        # Repository to Model (data_access -> domain)
        ('examples/layered_architecture/repositories/user_repository.py', 'examples/layered_architecture/models/user.py')
    ]
    
    for source_file, target_file in valid_deps:
        source_id = f"{source_file}::module"
        target_id = f"{target_file}::module"
        
        # Get layers
        source_layer = pattern._categorize_component_by_path(source_file)
        target_layer = pattern._categorize_component_by_path(target_file)
        
        # Ensure nodes exist
        if not pattern.component_graph.has_node(source_id):
            pattern.component_graph.add_node(
                source_id, 
                file=source_file, 
                layer=source_layer,
                type='module'
            )
        
        if not pattern.component_graph.has_node(target_id):
            pattern.component_graph.add_node(
                target_id, 
                file=target_file, 
                layer=target_layer,
                type='module'
            )
        
        # Add edge without violation flag
        pattern.component_graph.add_edge(
            source_id, target_id, 
            type='import', 
            violation=False
        )
    
    # Analyze the architecture
    analysis_result = pattern._analyze_graph()
    
    # Create the visualizer
    visualizer = LayeredArchitectureVisualizer()
    
    # Generate and save the visualization
    output_path = visualizer.visualize(analysis_result)
    
    logger.info(f"Layered architecture visualization saved to: {output_path}")
    
    # Print a summary of the visualization
    logger.info("=== Visualization Summary ===")
    logger.info(f"Confidence score: {analysis_result.get('confidence', 0):.2f}")
    logger.info(f"Total components: {sum(analysis_result.get('layer_counts', {}).values())}")
    logger.info(f"Dependency violations: {analysis_result.get('violation_statistics', {}).get('count', 0)}")
    
    # Print the visualization data structure
    graph_data = analysis_result.get('layered_architecture_graph', {})
    if graph_data:
        logger.info(f"Graph visualization includes {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
    
    # Recommend how to view the report
    logger.info("To view the visualization, open the HTML file in a web browser:")
    logger.info(f"  - {os.path.abspath(output_path)}")

if __name__ == "__main__":
    visualize_layered_architecture()