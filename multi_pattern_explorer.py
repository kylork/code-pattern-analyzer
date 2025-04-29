#!/usr/bin/env python3
"""
Multi-Pattern Interactive Design Patterns Explorer

This script provides an enhanced version of the design patterns explorer that supports
multiple design patterns, with the ability to select and explore different patterns
through a unified interface.

Usage:
    python multi_pattern_explorer.py --output ./design_patterns_explorer.html
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

# Pattern to template file mapping
PATTERN_TEMPLATES = {
    "Factory Method": "factory_method_pattern.html",
    "Observer": "interactive_patterns.html"  # This is the original Observer pattern template
}

def get_available_patterns():
    """Get list of patterns that have template implementations."""
    return list(PATTERN_TEMPLATES.keys())

def generate_explorer_html(output_path, pattern=None):
    """Generate the HTML for the design patterns explorer.
    
    Args:
        output_path: Path to save the HTML file
        pattern: Specific pattern to display, or None for all available patterns
        
    Returns:
        Path to the generated HTML file
    """
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which pattern template to use
    if pattern and pattern in PATTERN_TEMPLATES:
        template_filename = PATTERN_TEMPLATES[pattern]
    else:
        # If no specific pattern is requested or the pattern is not found,
        # default to the first available pattern
        available_patterns = get_available_patterns()
        if not available_patterns:
            raise ValueError("No pattern templates are available")
        
        pattern = available_patterns[0]
        template_filename = PATTERN_TEMPLATES[pattern]
    
    # Get template path
    template_path = Path(__file__).parent / "src" / "templates" / template_filename
    
    # Copy template to output path
    shutil.copy(template_path, output_path)
    
    logger.info(f"Generated {pattern} pattern explorer at {output_path}")
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
    
    # Try to find an available port if the specified one is in use
    while True:
        try:
            # Create and start the server
            server = socketserver.TCPServer(("", port), handler)
            break
        except OSError:
            logger.warning(f"Port {port} is in use, trying port {port+1}")
            port += 1
    
    logger.info(f"Starting server at http://localhost:{port}")
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server, f"http://localhost:{port}"

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Pattern Interactive Design Patterns Explorer"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./output/design_patterns_explorer.html",
        help="Path to save the explorer HTML file"
    )
    
    parser.add_argument(
        "--pattern", "-p",
        choices=get_available_patterns(),
        help="Specific pattern to display"
    )
    
    parser.add_argument(
        "--list-patterns", "-l",
        action="store_true",
        help="List available design patterns"
    )
    
    parser.add_argument(
        "--serve", "-s",
        action="store_true",
        help="Start a local server to serve the explorer"
    )
    
    parser.add_argument(
        "--port",
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
    
    # Handle --list-patterns flag
    if args.list_patterns:
        print("Available design patterns:")
        available_patterns = get_available_patterns()
        for pattern in available_patterns:
            print(f"  - {pattern}")
        return 0
    
    try:
        # Generate the explorer HTML
        output_path = Path(args.output)
        html_path = generate_explorer_html(output_path, args.pattern)
        
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