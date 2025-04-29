"""
Main entry point for the CLI application.

This module is responsible for setting up the command-line interface,
parsing arguments, and dispatching to the appropriate subcommand.
"""

import sys
import logging
from typing import List, Optional

from .parser import parse_args
from .subcommands import pattern_command, list_command, architecture_command, visualize_command, anti_patterns_command, complexity_command

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI application.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    # Parse arguments
    parsed_args = parse_args(args)
    
    # Configure logging verbosity
    if parsed_args.verbose > 0:
        log_level = max(logging.DEBUG, logging.WARNING - parsed_args.verbose * 10)
        logging.getLogger().setLevel(log_level)
        logger.debug(f"Set log level to {logging.getLevelName(log_level)}")
    
    # Dispatch to the appropriate subcommand
    if parsed_args.command == "pattern":
        return pattern_command(parsed_args)
    elif parsed_args.command == "list":
        return list_command(parsed_args)
    elif parsed_args.command == "architecture":
        return architecture_command(parsed_args)
    elif parsed_args.command == "visualize":
        return visualize_command(parsed_args)
    elif parsed_args.command == "anti-patterns":
        return anti_patterns_command(parsed_args)
    elif parsed_args.command == "complexity":
        return complexity_command(parsed_args)
    else:
        logger.error("No command specified")
        return 1

if __name__ == "__main__":
    sys.exit(main())