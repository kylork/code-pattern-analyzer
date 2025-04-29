"""
Demo project configurations for the Code Pattern Analyzer.

This module provides sample project configurations that can be used
for demonstration purposes when users want to try the analyzer
without providing their own codebase.
"""

import os
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class DemoProject:
    """Represents a sample project for demonstration purposes."""
    
    def __init__(
        self,
        name: str,
        description: str,
        project_type: str,
        architecture_style: str,
        source_path: str,
        recommended_visualizations: List[str]
    ):
        """Initialize a demo project.
        
        Args:
            name: Name of the demo project
            description: Brief description of the project
            project_type: Type of project (e.g., "web", "cli", "library")
            architecture_style: Primary architectural style
            source_path: Path to the source code directory (relative to examples/)
            recommended_visualizations: List of visualization types that work well
        """
        self.name = name
        self.description = description
        self.project_type = project_type
        self.architecture_style = architecture_style
        self.source_path = source_path
        self.recommended_visualizations = recommended_visualizations
    
    def get_full_path(self, base_dir: Optional[str] = None) -> str:
        """Get the full path to the demo project.
        
        Args:
            base_dir: Base directory containing examples. If None,
                      uses the examples directory in the project root.
        
        Returns:
            Full path to the project directory
        """
        if base_dir is None:
            # Use the examples directory in the project root
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "examples"
            )
        
        return os.path.join(base_dir, self.source_path)
    
    def to_dict(self) -> Dict:
        """Convert the demo project to a dictionary.
        
        Returns:
            Dictionary representation of the project
        """
        return {
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "architecture_style": self.architecture_style,
            "source_path": self.source_path,
            "recommended_visualizations": self.recommended_visualizations
        }


# List of available demo projects
DEMO_PROJECTS = [
    DemoProject(
        name="Layered Architecture Example",
        description="A typical layered architecture with controllers, services, and repositories",
        project_type="web",
        architecture_style="layered",
        source_path="layered_architecture",
        recommended_visualizations=["component_visualization", "code_pattern_linkage"]
    ),
    DemoProject(
        name="Dependency Inversion Example",
        description="Demonstrates the dependency inversion principle with interfaces and implementations",
        project_type="library",
        architecture_style="clean",
        source_path="dependency_inversion",
        recommended_visualizations=["code_pattern_linkage"]
    ),
    DemoProject(
        name="Event-Driven Architecture Example",
        description="An event-driven system with publishers, subscribers, and an event bus",
        project_type="system",
        architecture_style="event_driven",
        source_path="event_driven",
        recommended_visualizations=["component_visualization", "code_pattern_linkage"]
    ),
    DemoProject(
        name="Information Hiding Example",
        description="Demonstrates information hiding principles with well-defined interfaces",
        project_type="library",
        architecture_style="clean",
        source_path="information_hiding",
        recommended_visualizations=["code_pattern_linkage"]
    )
]


def get_demo_projects() -> List[DemoProject]:
    """Get the list of available demo projects.
    
    Returns:
        List of DemoProject objects
    """
    return DEMO_PROJECTS


def get_demo_project_by_name(name: str) -> Optional[DemoProject]:
    """Get a demo project by name.
    
    Args:
        name: Name of the demo project
    
    Returns:
        The DemoProject object or None if not found
    """
    for project in DEMO_PROJECTS:
        if project.name == name:
            return project
    return None


def get_demo_project_by_style(style: str) -> Optional[DemoProject]:
    """Get a demo project that demonstrates a specific architectural style.
    
    Args:
        style: Architectural style
    
    Returns:
        The first DemoProject object matching the style, or None if not found
    """
    for project in DEMO_PROJECTS:
        if project.architecture_style == style:
            return project
    return None