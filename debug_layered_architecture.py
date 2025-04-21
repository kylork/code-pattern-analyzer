#!/usr/bin/env python3
"""
Debug script for testing the enhanced Layered Architecture detector.

This script tests the Layered Architecture pattern detector by directly
providing component and dependency information based on our example code.
"""

import os
import sys
import json
import logging
from pathlib import Path
import networkx as nx

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug_layered")

# Add the source directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import required modules
from src.patterns.architectural_styles import LayeredArchitecturePattern

def debug_layered_architecture():
    """Debug the LayeredArchitecturePattern implementation with manual test data."""
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
    analysis = pattern._analyze_graph()
    
    # Pretty print the analysis
    logger.info("=== Layered Architecture Analysis ===")
    print(json.dumps(analysis, indent=2))
    
    # Print component graph statistics
    logger.info(f"Component graph has {len(pattern.component_graph.nodes)} nodes and {len(pattern.component_graph.edges)} edges")
    
    # Print layer counts
    for layer, count in analysis.get('layer_counts', {}).items():
        logger.info(f"Layer '{layer}': {count} components")
    
    # Print confidence score
    confidence = analysis.get('confidence', 0.0)
    logger.info(f"Confidence score: {confidence:.2f}")
    
    # Print violation statistics
    violation_stats = analysis.get('violation_statistics', {})
    logger.info(f"Detected {violation_stats.get('count', 0)} layer dependency violations")
    
    if violation_stats.get('most_common_violation'):
        source = violation_stats['most_common_violation']['source']
        target = violation_stats['most_common_violation']['target']
        count = violation_stats['most_common_violation']['count']
        logger.info(f"Most common violation: {count} dependencies from {source} to {target}")
    
    # Print dependency violations
    violations = analysis.get('dependency_violations', [])
    if violations:
        logger.info("Dependency violations:")
        for i, violation in enumerate(violations, 1):
            logger.info(f"{i}. {violation['message']} - {violation['source_file']} -> {violation['target_file']} (line {violation['line']})")
    
    # Print recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        logger.info("Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"{i}. {rec}")
    
    # Check the architecture graph data for visualization
    graph_data = analysis.get('layered_architecture_graph', {})
    if graph_data:
        logger.info(f"Layer graph contains {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
        
        # Check for violation edges
        violation_edges = [edge for edge in graph_data.get('edges', []) if edge.get('violation', False)]
        if violation_edges:
            logger.info(f"Layer graph contains {len(violation_edges)} violation edges:")
            for edge in violation_edges:
                logger.info(f"  {edge['source']} -> {edge['target']}")

if __name__ == "__main__":
    debug_layered_architecture()