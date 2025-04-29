#!/usr/bin/env python3
"""
Run All Code Pattern Analyzer Services

This script starts all the necessary services for the full Code Pattern Analyzer experience:
- Main GUI
- Pattern Transformation GUI 
- Pattern Recommendation GUI

Usage:
    python run_all_services.py
"""

import os
import sys
import subprocess
import time
import argparse
import threading
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Path constants
ROOT_DIR = Path(__file__).parent.absolute()

# Define services to start
SERVICES = [
    {
        "name": "Pattern Transformation GUI",
        "script": "pattern_transformation_gui.py",
        "port": 8082,
        "process": None,
        "thread": None
    },
    {
        "name": "Pattern Recommendation GUI",
        "script": "pattern_recommendation_gui.py",
        "port": 8081,
        "process": None,
        "thread": None
    },
    {
        "name": "Main Code Pattern Analyzer GUI",
        "script": "code_pattern_analyzer_gui.py",
        "port": 8080,
        "process": None,
        "thread": None
    }
]

# Global flag to signal when to stop all services
stop_all = False

def run_service(service):
    """Run a service in a subprocess."""
    logger.info(f"Starting {service['name']} on port {service['port']}...")
    
    try:
        script_path = ROOT_DIR / service["script"]
        
        # Start the service
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        service["process"] = process
        
        # Log the process output
        while not stop_all:
            output = process.stdout.readline()
            if output:
                logger.info(f"[{service['name']}] {output.strip()}")
            
            error = process.stderr.readline()
            if error:
                logger.error(f"[{service['name']}] {error.strip()}")
            
            # Check if the process is still running
            if process.poll() is not None:
                remaining_output, remaining_error = process.communicate()
                if remaining_output:
                    logger.info(f"[{service['name']}] {remaining_output.strip()}")
                if remaining_error:
                    logger.error(f"[{service['name']}] {remaining_error.strip()}")
                
                logger.info(f"{service['name']} has exited with code {process.returncode}")
                break
            
            # Small sleep to prevent busy waiting
            time.sleep(0.1)
    
    except Exception as e:
        logger.error(f"Error running {service['name']}: {str(e)}")

def start_all_services():
    """Start all services."""
    for service in SERVICES:
        service["thread"] = threading.Thread(
            target=run_service,
            args=(service,),
            daemon=True
        )
        service["thread"].start()
        
        # Small delay to avoid port conflicts
        time.sleep(1)
    
    logger.info("All services started.")
    logger.info("Main GUI: http://localhost:8080")
    logger.info("Pattern Transformation: http://localhost:8082")
    logger.info("Pattern Recommendation: http://localhost:8081")

def stop_all_services():
    """Stop all services."""
    global stop_all
    stop_all = True
    
    logger.info("Stopping all services...")
    
    for service in SERVICES:
        if service["process"] and service["process"].poll() is None:
            logger.info(f"Stopping {service['name']}...")
            service["process"].terminate()
    
    # Wait for processes to terminate
    for service in SERVICES:
        if service["process"]:
            try:
                service["process"].wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"{service['name']} did not terminate gracefully, killing...")
                service["process"].kill()
    
    logger.info("All services stopped.")

def signal_handler(sig, frame):
    """Handle keyboard interrupt."""
    logger.info("Received signal to stop")
    stop_all_services()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Run all Code Pattern Analyzer services"
    )
    
    args = parser.parse_args()
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start all services
        start_all_services()
        
        # Keep running until interrupted
        logger.info("Press Ctrl+C to stop all services")
        while not stop_all:
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    finally:
        stop_all_services()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())