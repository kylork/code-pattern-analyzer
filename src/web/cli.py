"""
Command line interface for the web API server.
"""

import click
import uvicorn
import os

@click.group()
def web_cli():
    """Code Pattern Analyzer Web API server."""
    pass


@web_cli.command()
@click.option("--host", default="0.0.0.0", help="Host to run the server on")
@click.option("--port", default=8000, help="Port to run the server on")
@click.option("--reload/--no-reload", default=True, help="Enable auto-reload")
def serve(host, port, reload):
    """Start the FastAPI web server."""
    # Get the directory where the app module is located
    module_path = "code_pattern_analyzer.web.app:app"
    
    click.echo(f"Starting web server at http://{host}:{port}")
    click.echo(f"API documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        module_path,
        host=host,
        port=port,
        reload=reload
    )


def main():
    """Entry point for the web CLI."""
    web_cli()


if __name__ == "__main__":
    main()
