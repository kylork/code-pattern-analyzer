#!/usr/bin/env python3
"""
Utility script to view Code Pattern Analyzer visualizations.

This script simplifies viewing visualizations by:
1. Opening HTML files directly in a browser, or
2. Starting a local web server, or
3. Creating a portable bundle of files

Examples:
    python view_visualization.py output/my_visualization.html  # Open directly
    python view_visualization.py --server output/  # Start server for directory
    python view_visualization.py --bundle output/my_visualization.html  # Create bundle
"""

import os
import sys
import logging
import argparse
import webbrowser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.visualization.visualization_utilities import (
    open_visualization_in_browser,
    start_visualization_server,
    create_visualization_bundle
)

def main():
    parser = argparse.ArgumentParser(
        description="View Code Pattern Analyzer visualizations"
    )
    
    # Define command-line arguments
    parser.add_argument(
        "path",
        help="Path to visualization HTML file or directory"
    )
    
    parser.add_argument(
        "--server", "-s",
        action="store_true",
        help="Start a local HTTP server instead of opening in browser"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to use for HTTP server (default: 8000)"
    )
    
    parser.add_argument(
        "--bundle", "-b",
        action="store_true",
        help="Create a portable bundle containing the visualization"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for bundle (default: temporary directory)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert path to absolute
    path = Path(args.path).resolve()
    
    # Create visualization bundle
    if args.bundle:
        if not path.is_file() or path.suffix.lower() != '.html':
            logger.error("Bundle option requires an HTML file path")
            return 1
            
        bundle_path = create_visualization_bundle(path, args.output_dir)
        if not bundle_path:
            logger.error("Failed to create visualization bundle")
            return 1
            
        logger.info(f"Created visualization bundle at: {bundle_path}")
        return 0
    
    # Start HTTP server
    if args.server:
        dir_path = path if path.is_dir() else path.parent
        process, url = start_visualization_server(dir_path, args.port)
        
        if not process:
            logger.error("Failed to start visualization server")
            return 1
            
        # If path is a file, append its name to the URL
        if path.is_file():
            url = f"{url}/{path.name}"
            
        logger.info(f"Opening visualization at: {url}")
        webbrowser.open(url)
        
        try:
            logger.info("Press Ctrl+C to stop the server")
            process.wait()
        except KeyboardInterrupt:
            logger.info("Stopping server...")
            process.terminate()
        finally:
            if process.poll() is None:
                process.kill()
        
        return 0
    
    # Open visualization in browser
    if not path.is_file() or path.suffix.lower() != '.html':
        logger.error("Please provide a path to an HTML visualization file")
        return 1
        
    success = open_visualization_in_browser(path)
    if not success:
        logger.error("Failed to open visualization in browser")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())