#!/usr/bin/env python3
"""
Interactive Design Patterns Explorer

This script provides an interactive web-based tool for exploring and learning about
design patterns, with code examples, diagrams, and interactive simulations.

Usage:
    python explore_design_patterns.py --output ./design_patterns_explorer.html
"""

import os
import sys
import logging
import argparse
import shutil
from pathlib import Path
import webbrowser
import http.server
import socketserver
import threading
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Design pattern categories and patterns
DESIGN_PATTERNS = {
    "Creational": [
        "Factory Method",
        "Abstract Factory",
        "Builder",
        "Prototype",
        "Singleton"
    ],
    "Structural": [
        "Adapter",
        "Bridge",
        "Composite",
        "Decorator",
        "Facade",
        "Flyweight",
        "Proxy"
    ],
    "Behavioral": [
        "Chain of Responsibility",
        "Command",
        "Interpreter",
        "Iterator",
        "Mediator",
        "Memento",
        "Observer",
        "State",
        "Strategy",
        "Template Method",
        "Visitor"
    ]
}

def generate_explorer_html(output_path):
    """Generate the HTML for the design patterns explorer.
    
    Args:
        output_path: Path to save the HTML file
        
    Returns:
        Path to the generated HTML file
    """
    # Get template path
    template_path = Path(__file__).parent / "src" / "templates" / "interactive_patterns.html"
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template to output path
    shutil.copy(template_path, output_path)
    
    logger.info(f"Generated design patterns explorer at {output_path}")
    return output_path

def start_server(directory, port=8000):
    """Start a local HTTP server to serve the explorer.
    
    Args:
        directory: Directory to serve files from
        port: Port to bind the server to
        
    Returns:
        The server instance and the URL to access it
    """
    # Change to the specified directory
    os.chdir(directory)
    
    # Create a request handler
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create and start the server
    server = socketserver.TCPServer(("", port), handler)
    
    logger.info(f"Starting server at http://localhost:{port}")
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server, f"http://localhost:{port}"

def main():
    parser = argparse.ArgumentParser(
        description="Interactive Design Patterns Explorer"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./output/design_patterns_explorer.html",
        help="Path to save the explorer HTML file"
    )
    
    parser.add_argument(
        "--serve", "-s",
        action="store_true",
        help="Start a local server to serve the explorer"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port to use for the local server (default: 8000)"
    )
    
    parser.add_argument(
        "--no-browser", "-n",
        action="store_true",
        help="Don't open the browser automatically"
    )
    
    args = parser.parse_args()
    
    try:
        # Generate the explorer HTML
        output_path = Path(args.output)
        html_path = generate_explorer_html(output_path)
        
        # Start a local server if requested
        if args.serve:
            server, url = start_server(output_path.parent, args.port)
            
            # Construct the URL to the explorer HTML
            explorer_url = f"{url}/{output_path.name}"
            
            # Open the browser if not disabled
            if not args.no_browser:
                logger.info(f"Opening browser to {explorer_url}")
                webbrowser.open(explorer_url)
                
            logger.info("Press Ctrl+C to stop the server")
            
            try:
                # Wait for keyboard interrupt
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down server")
                server.shutdown()
        else:
            # Just open the HTML file directly if not serving
            if not args.no_browser:
                logger.info(f"Opening {html_path}")
                webbrowser.open(f"file://{html_path.absolute()}")
            else:
                logger.info(f"Design Patterns Explorer generated at: {html_path}")
                logger.info(f"Open this file in a browser to explore design patterns")
    
    except Exception as e:
        logger.error(f"Error generating explorer: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())