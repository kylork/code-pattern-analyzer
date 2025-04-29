"""
FastAPI application for the Code Pattern Analyzer.
"""

from fastapi import FastAPI, HTTPException, Query, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
import os
import tempfile
from pathlib import Path
import shutil
import logging
import uuid
import json

from ..analyzer import CodeAnalyzer
from ..pattern_registry import registry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(
    title="Code Pattern Analyzer API",
    description="API for analyzing code patterns in source files",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine the path to static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create the analyzer instance (default to real implementation)
analyzer = CodeAnalyzer(use_mock=False)

# In-memory storage for analysis results
analysis_storage = {}
project_storage = {}


# Models
class AnalysisRequest(BaseModel):
    file_content: str
    filename: str
    pattern_name: Optional[str] = None
    category: Optional[str] = None
    use_mock: bool = False


class DirectoryAnalysisRequest(BaseModel):
    pattern_name: Optional[str] = None
    category: Optional[str] = None
    exclude_dirs: Optional[List[str]] = None
    file_extensions: Optional[List[str]] = None
    use_mock: bool = False


class ProjectInfo(BaseModel):
    name: str
    description: Optional[str] = None


# Routes
@app.get("/", response_class=HTMLResponse)
def read_root():
    """Root endpoint that returns the API documentation page."""
    # Check if the index.html file exists
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    
    # Fallback to JSON response if the HTML file is not found
    return HTMLResponse(content="""
    <html>
        <head>
            <title>Code Pattern Analyzer API</title>
        </head>
        <body>
            <h1>Code Pattern Analyzer API</h1>
            <p>API for analyzing code patterns in source files.</p>
            <p><a href="/docs">Interactive API documentation</a></p>
        </body>
    </html>
    """)


@app.get("/patterns")
def get_patterns():
    """Get all available patterns."""
    patterns = []
    for pattern_name in analyzer.get_available_patterns():
        pattern = registry.get_pattern(pattern_name)
        if pattern:
            patterns.append({
                "name": pattern.name,
                "description": pattern.description,
                "languages": list(pattern.languages) if pattern.languages else None,
            })
    return {"patterns": patterns}


@app.get("/categories")
def get_categories():
    """Get all available pattern categories."""
    categories = analyzer.get_available_categories()
    result = {}
    
    for category in categories:
        patterns = analyzer.get_patterns_by_category(category)
        result[category] = patterns
        
    return {"categories": result}


@app.post("/analyze")
def analyze_code(request: AnalysisRequest):
    """Analyze code provided directly in the request."""
    # Set the implementation
    analyzer.set_implementation(use_mock=request.use_mock)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(request.filename)[1], 
                                     delete=False) as temp_file:
        temp_file.write(request.file_content.encode('utf-8'))
        temp_path = temp_file.name
    
    try:
        # Analyze the file
        result = analyzer.analyze_file(
            temp_path, 
            pattern_name=request.pattern_name,
            category=request.category
        )
        
        # Store the result
        analysis_id = str(uuid.uuid4())
        analysis_storage[analysis_id] = result
        
        # Add the analysis ID to the result
        result['analysis_id'] = analysis_id
        
        return result
    finally:
        # Clean up
        os.unlink(temp_path)


@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    pattern_name: Optional[str] = None,
    category: Optional[str] = None,
    use_mock: bool = False
):
    """Upload and analyze a single file."""
    # Set the implementation
    analyzer.set_implementation(use_mock=use_mock)
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save the file
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Analyze the file
        result = analyzer.analyze_file(
            temp_path, 
            pattern_name=pattern_name,
            category=category
        )
        
        # Store the result
        analysis_id = str(uuid.uuid4())
        analysis_storage[analysis_id] = result
        
        # Add the analysis ID to the result
        result['analysis_id'] = analysis_id
        
        # Clean up in the background
        background_tasks.add_task(shutil.rmtree, temp_dir)
        
        return result
    except Exception as e:
        # Clean up
        shutil.rmtree(temp_dir)
        logger.error(f"Error analyzing uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


@app.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    """Get a stored analysis result by ID."""
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail=f"Analysis ID {analysis_id} not found")
    
    return analysis_storage[analysis_id]


@app.get("/analysis/{analysis_id}/html")
def get_analysis_html(analysis_id: str):
    """Get an HTML report for a stored analysis result."""
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail=f"Analysis ID {analysis_id} not found")
    
    result = analysis_storage[analysis_id]
    html = analyzer.generate_report([result], output_format="html")
    
    return HTMLResponse(content=html)


@app.get("/analysis/{analysis_id}/json")
def get_analysis_json(analysis_id: str):
    """Get a JSON report for a stored analysis result."""
    if analysis_id not in analysis_storage:
        raise HTTPException(status_code=404, detail=f"Analysis ID {analysis_id} not found")
    
    result = analysis_storage[analysis_id]
    return result


@app.post("/projects")
def create_project(project: ProjectInfo):
    """Create a new project."""
    project_id = str(uuid.uuid4())
    project_storage[project_id] = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "files": {},
        "analyses": [],
    }
    
    return {"project_id": project_id}


@app.get("/projects")
def list_projects():
    """List all projects."""
    projects = []
    for project_id, project in project_storage.items():
        projects.append({
            "id": project_id,
            "name": project["name"],
            "description": project["description"],
        })
    
    return {"projects": projects}


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    """Get a project by ID."""
    if project_id not in project_storage:
        raise HTTPException(status_code=404, detail=f"Project ID {project_id} not found")
    
    return project_storage[project_id]


@app.post("/projects/{project_id}/files")
async def upload_project_file(
    project_id: str,
    file: UploadFile,
):
    """Upload a file to a project."""
    if project_id not in project_storage:
        raise HTTPException(status_code=404, detail=f"Project ID {project_id} not found")
    
    content = await file.read()
    file_id = str(uuid.uuid4())
    
    project_storage[project_id]["files"][file_id] = {
        "id": file_id,
        "name": file.filename,
        "content": content.decode('utf-8', errors='replace'),
    }
    
    return {"file_id": file_id}


@app.post("/projects/{project_id}/analyze")
def analyze_project(
    project_id: str,
    request: DirectoryAnalysisRequest,
):
    """Analyze all files in a project."""
    if project_id not in project_storage:
        raise HTTPException(status_code=404, detail=f"Project ID {project_id} not found")
    
    # Set the implementation
    analyzer.set_implementation(use_mock=request.use_mock)
    
    # Create a temporary directory for the project files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Write all project files to the temp directory
        for file_id, file_info in project_storage[project_id]["files"].items():
            file_path = os.path.join(temp_dir, file_info["name"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info["content"])
        
        # Analyze the directory
        results = analyzer.analyze_directory(
            temp_dir,
            pattern_name=request.pattern_name,
            category=request.category,
            exclude_dirs=request.exclude_dirs,
            file_extensions=request.file_extensions,
        )
        
        # Store the result
        analysis_id = str(uuid.uuid4())
        analysis_storage[analysis_id] = results
        
        # Add the analysis to the project
        project_storage[project_id]["analyses"].append({
            "id": analysis_id,
            "timestamp": logging.Formatter.formatTime(logging.Formatter(), logging.LogRecord(None, None, None, None, None, None, None)),
            "parameters": request.dict(),
        })
        
        return {
            "analysis_id": analysis_id,
            "results": results,
        }
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def start():
    """Start the FastAPI application using uvicorn."""
    import uvicorn
    uvicorn.run("code_pattern_analyzer.web.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
