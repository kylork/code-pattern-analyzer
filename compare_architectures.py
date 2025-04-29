#!/usr/bin/env python3
"""
Architecture Comparison Tool

This script generates an interactive comparison of different architectural styles,
with visualizations from example projects.

Usage:
    python compare_architectures.py --output architecture_comparison.html
"""

import os
import sys
import logging
import argparse
import shutil
from pathlib import Path
import tempfile
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def create_example_projects(output_dir):
    """Create example projects for all supported architectural styles.
    
    Args:
        output_dir: Directory to create the examples in
        
    Returns:
        Dictionary mapping architectural styles to project paths
    """
    # Ensure the output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get path to create_example_project.py
    script_path = Path(__file__).parent / "create_example_project.py"
    
    # Supported architectural styles
    styles = ["layered", "hexagonal", "clean"]
    projects = {}
    
    for style in styles:
        style_dir = output_path / style
        
        # Create the example project
        try:
            logger.info(f"Creating {style} architecture example...")
            
            # Run create_example_project.py
            cmd = [
                sys.executable,
                str(script_path),
                "--style", style,
                "--output", str(style_dir)
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            logger.info(f"Created {style} architecture example: {style_dir}")
            projects[style] = style_dir
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating {style} architecture example: {e.stderr}")
            logger.error(f"Command output: {e.stdout}")
            
    return projects

def analyze_projects(projects, output_dir):
    """Analyze example projects and generate visualizations.
    
    Args:
        projects: Dictionary mapping architectural styles to project paths
        output_dir: Directory to save visualizations in
        
    Returns:
        Dictionary mapping architectural styles to visualization paths
    """
    # Ensure the output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get path to run_code_pattern_linkage.py
    script_path = Path(__file__).parent / "run_code_pattern_linkage.py"
    
    visualizations = {}
    
    for style, project_dir in projects.items():
        # Generate visualization
        try:
            logger.info(f"Analyzing {style} architecture example...")
            
            # Output file name
            output_file = f"{style}_architecture_visualization.html"
            
            # Run run_code_pattern_linkage.py
            cmd = [
                sys.executable,
                str(script_path),
                str(project_dir),
                "--style", style,
                "--output", output_file,
                "--output-dir", str(output_path),
                "--mock"  # Use mock implementation to avoid tree-sitter issues
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            visualization_path = output_path / output_file
            logger.info(f"Generated visualization for {style} architecture: {visualization_path}")
            visualizations[style] = visualization_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error analyzing {style} architecture example: {e.stderr}")
            logger.error(f"Command output: {e.stdout}")
            
    return visualizations

def create_comparison_page(visualizations, output_path):
    """Create a comparison HTML page with visualizations.
    
    Args:
        visualizations: Dictionary mapping architectural styles to visualization paths
        output_path: Path to save the comparison HTML file
        
    Returns:
        Path to the generated comparison HTML file
    """
    # Get template path
    template_path = Path(__file__).parent / "src" / "templates" / "architecture_comparison.html"
    
    # Ensure the output directory exists
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a static directory for images
    static_dir = output_dir / "static" / "images"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Create screenshot images from visualizations (this would normally use a headless browser)
    # For this example, we'll just copy placeholder images
    for style, viz_path in visualizations.items():
        # In a real implementation, you would generate screenshots here
        # For now, we'll just copy the HTML files
        target_path = static_dir / f"{style}_architecture_visualization.png"
        
        # Since we can't easily generate screenshots, we'll create a placeholder
        with open(target_path, "w") as f:
            f.write(f"Placeholder for {style} architecture visualization")
    
    # Copy the template to the output location
    shutil.copy(template_path, output_path)
    
    logger.info(f"Created comparison page at {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(
        description="Generate an interactive comparison of different architectural styles"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./output/architecture_comparison.html",
        help="Path to save the comparison HTML file"
    )
    
    parser.add_argument(
        "--temp-dir", "-t",
        help="Temporary directory for example projects (default: system temp directory)"
    )
    
    parser.add_argument(
        "--keep-examples", "-k",
        action="store_true",
        help="Keep example project files after generating comparison"
    )
    
    args = parser.parse_args()
    
    try:
        # Create a temporary directory for example projects
        if args.temp_dir:
            temp_dir = Path(args.temp_dir)
            temp_dir.mkdir(parents=True, exist_ok=True)
            clean_up_temp = False
        else:
            temp_dir = Path(tempfile.mkdtemp(prefix="architecture_examples_"))
            clean_up_temp = True
        
        # Set output path
        output_path = Path(args.output)
        
        logger.info(f"Using temporary directory: {temp_dir}")
        logger.info(f"Output will be saved to: {output_path}")
        
        # Create example projects
        projects = create_example_projects(temp_dir)
        
        # Analyze projects and generate visualizations
        visualizations = analyze_projects(projects, output_path.parent / "visualizations")
        
        # Create comparison page
        comparison_path = create_comparison_page(visualizations, output_path)
        
        print(f"\nComparison page created successfully at: {comparison_path}")
        print("Open this HTML file in a browser to view the comparison.")
        
        # Clean up temporary directory
        if clean_up_temp and not args.keep_examples:
            logger.info(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir)
        
    except Exception as e:
        logger.error(f"Error creating architecture comparison: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())