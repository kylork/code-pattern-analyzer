# Web UI Implementation

## Overview

This document describes the implementation of the Code Pattern Analyzer Web UI, which provides a web-based interface for analyzing code, visualizing patterns, and managing analysis results.

## Components

### Backend API (FastAPI)

The backend API is implemented using FastAPI, a modern, high-performance web framework for building APIs with Python 3.6+. It provides the following features:

- RESTful API endpoints for code analysis
- File upload and project management
- Analysis result storage and retrieval
- Interactive API documentation using Swagger UI

#### Key Endpoints

- GET `/patterns` - List all available patterns
- GET `/categories` - List all pattern categories
- POST `/analyze` - Analyze code content
- POST `/upload` - Upload and analyze a file
- GET `/analysis/{analysis_id}` - Get analysis results
- GET `/analysis/{analysis_id}/html` - Get HTML report for analysis
- POST `/projects` - Create a new project
- POST `/projects/{project_id}/files` - Upload a file to a project
- POST `/projects/{project_id}/analyze` - Analyze all files in a project

### Frontend React Application

The frontend application is built with React and provides an intuitive user interface for interacting with the Code Pattern Analyzer.

#### Key Features

- **Home Page**: Introduction to the tool and its capabilities
- **File Analysis**: Upload files or paste code directly for analysis
- **Project Management**: Create and manage projects with multiple files
- **Results Visualization**: Interactive visualization of analysis results with charts
- **Pattern Details**: In-depth view of detected patterns

#### Key Components

- **Header**: Navigation and branding
- **HomePage**: Introduction and feature overview
- **FilePage**: File upload and code input for analysis
- **ProjectsPage**: Project management interface
- **ProjectPage**: Individual project view and file management
- **ResultsPage**: Analysis results visualization

### Getting Started

To run the web interface:

```bash
# Install dependencies
pip install -r requirements.txt
npm install # (in the web_ui/frontend directory)

# Start the backend server
python -m code_pattern_analyzer web serve

# Start the frontend development server (in a separate terminal)
cd web_ui/frontend
npm start
```

The backend API will be available at http://localhost:8000, and the interactive documentation at http://localhost:8000/docs.

The frontend will be available at http://localhost:3000.

## Implementation Details

### Backend

#### Data Models

The API uses Pydantic models for request and response validation:

- `AnalysisRequest` - Request for analyzing code content
- `DirectoryAnalysisRequest` - Request for analyzing a directory
- `ProjectInfo` - Information about a project

#### Storage

The API uses in-memory storage for simplicity, but this can be replaced with a persistent storage solution in the future:

- `analysis_storage` - Dictionary mapping analysis IDs to analysis results
- `project_storage` - Dictionary mapping project IDs to project information

#### Code Analysis

The API integrates with the existing Code Pattern Analyzer core to perform analysis:

1. For direct code analysis, the API creates a temporary file with the submitted code
2. For file uploads, the API saves the uploaded file to a temporary location
3. For project analysis, the API creates a temporary directory with all project files
4. The analysis is performed using the `CodeAnalyzer` class
5. Results are stored in memory and can be retrieved using the analysis ID

### Frontend

#### State Management

The frontend uses React hooks for state management:

- `useState` for component-level state
- `useEffect` for data fetching and side effects
- `useCallback` for performance optimization
- `useParams` and `useNavigate` for routing

#### API Integration

The `ApiService` module provides methods for communicating with the backend API:

- Pattern and category fetching
- File upload and analysis
- Project management
- Results retrieval

#### Visualization

The application uses Chart.js for visualizing analysis results:

- Pie charts for pattern distribution
- HTML reports for detailed analysis
- Interactive UI for exploring results

## Future Development

### Enhanced Visualization

- Code structure diagrams
- Interactive AST explorer
- Pattern relationship visualization

### User Authentication

- User accounts and authentication
- Saved analyses and projects
- Sharing capabilities

### Persistent Storage

- Database integration for storing:
  - User projects
  - Analysis results
  - User preferences

### Advanced Features

- Comparative analysis between files
- Pattern evolution tracking
- Code structure visualization
- Interactive AST exploration
- Custom pattern definitions

## Development Notes

### Adding New API Endpoints

1. Define any required Pydantic models
2. Add the endpoint function to `app.py`
3. Update the API documentation as needed

Example:

```python
@app.post("/new_endpoint")
def new_endpoint(request: YourRequestModel):
    """Documentation for your endpoint."""
    # Implementation
    return {"result": "Success"}
```

### Adding New Frontend Components

1. Create the component file in `src/components/`
2. Add any necessary styles
3. Add the component to the appropriate route in `App.js`

Example:

```jsx
import React from 'react';

const NewComponent = () => {
  return (
    <div className="card">
      <div className="card-header">
        New Component
      </div>
      <div className="card-body">
        <p>Component content</p>
      </div>
    </div>
  );
};

export default NewComponent;
```