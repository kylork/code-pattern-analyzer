import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ApiService from '../services/api';

const ProjectPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState(null);
  const [file, setFile] = useState(null);
  const [patterns, setPatterns] = useState([]);
  const [categories, setCategories] = useState({});
  const [selectedPattern, setSelectedPattern] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [excludeDirs, setExcludeDirs] = useState('');
  const [fileExtensions, setFileExtensions] = useState('');
  const [useMock, setUseMock] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  // Load project data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch project data, patterns, and categories in parallel
        const [projectResponse, patternsResponse, categoriesResponse] = await Promise.all([
          ApiService.getProject(projectId),
          ApiService.getPatterns(),
          ApiService.getCategories()
        ]);
        
        setProject(projectResponse.data);
        setPatterns(patternsResponse.data.patterns || []);
        setCategories(categoriesResponse.data.categories || {});
      } catch (err) {
        setError(`Failed to load project: ${err.message}`);
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [projectId]);

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  // Handle file drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  // Handle drag events
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  // Upload file to project
  const handleUploadFile = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      await ApiService.uploadProjectFile(projectId, file);
      
      // Refresh project data
      const response = await ApiService.getProject(projectId);
      setProject(response.data);
      setFile(null); // Reset file selection
    } catch (err) {
      setError(`Failed to upload file: ${err.message}`);
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Analyze project
  const handleAnalyzeProject = async () => {
    setIsAnalyzing(true);
    setError(null);

    try {
      // Parse exclude dirs and file extensions
      const excludeDirsArray = excludeDirs ? excludeDirs.split(',').map(dir => dir.trim()) : null;
      const fileExtensionsArray = fileExtensions ? fileExtensions.split(',').map(ext => ext.trim()) : null;
      
      const response = await ApiService.analyzeProject(
        projectId,
        selectedPattern || null,
        selectedCategory || null,
        excludeDirsArray,
        fileExtensionsArray,
        useMock
      );

      // Navigate to results page
      if (response.data && response.data.analysis_id) {
        navigate(`/results/${response.data.analysis_id}`);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      setError(`Failed to analyze project: ${err.message}`);
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isLoading && !project) {
    return <div>Loading project data...</div>;
  }

  if (error && !project) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div>
      {project && (
        <>
          {/* Project Header */}
          <div className="card">
            <div className="card-header">
              Project: {project.name}
            </div>
            <div className="card-body">
              {project.description && <p>{project.description}</p>}
              
              {/* Project Stats */}
              <div>
                <p><strong>Files:</strong> {Object.keys(project.files || {}).length}</p>
                <p><strong>Analyses:</strong> {(project.analyses || []).length}</p>
              </div>
            </div>
          </div>

          {/* File Upload */}
          <div className="card">
            <div className="card-header">
              Add File
            </div>
            <div className="card-body">
              <form onSubmit={handleUploadFile}>
                <div className="form-group">
                  <div 
                    className={`file-upload ${file ? 'active' : ''}`}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                  >
                    <input 
                      type="file" 
                      onChange={handleFileChange} 
                      style={{ display: 'none' }}
                      id="file-input"
                    />
                    {file ? (
                      <div>
                        <p>File selected: {file.name}</p>
                        <button 
                          type="button" 
                          className="btn" 
                          onClick={() => document.getElementById('file-input').click()}
                        >
                          Change File
                        </button>
                      </div>
                    ) : (
                      <div>
                        <p>Drag and drop your file here, or</p>
                        <button 
                          type="button" 
                          className="btn" 
                          onClick={() => document.getElementById('file-input').click()}
                        >
                          Select File
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                <button type="submit" className="btn" disabled={!file || isLoading}>
                  {isLoading ? 'Uploading...' : 'Upload File'}
                </button>
              </form>

              {/* Error display */}
              {error && (
                <div className="alert alert-error">
                  <p>{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Project Files */}
          <div className="card">
            <div className="card-header">
              Project Files
            </div>
            <div className="card-body">
              {Object.keys(project.files || {}).length === 0 ? (
                <p>No files in project yet. Add files to analyze patterns.</p>
              ) : (
                <div>
                  <ul className="pattern-list">
                    {Object.values(project.files).map(file => (
                      <li key={file.id} className="pattern-item">
                        {file.name}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Analysis Form */}
          {Object.keys(project.files || {}).length > 0 && (
            <div className="card">
              <div className="card-header">
                Analyze Project
              </div>
              <div className="card-body">
                <form>
                  {/* Pattern Selection */}
                  <div className="form-group">
                    <label htmlFor="pattern">Pattern (Optional)</label>
                    <select 
                      id="pattern" 
                      value={selectedPattern} 
                      onChange={(e) => setSelectedPattern(e.target.value)}
                    >
                      <option value="">All Patterns</option>
                      {patterns.map(pattern => (
                        <option key={pattern.name} value={pattern.name}>
                          {pattern.name} {pattern.description ? `- ${pattern.description}` : ''}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Category Selection */}
                  <div className="form-group">
                    <label htmlFor="category">Category (Optional)</label>
                    <select 
                      id="category" 
                      value={selectedCategory} 
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      <option value="">All Categories</option>
                      {Object.keys(categories).map(category => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Exclude Directories */}
                  <div className="form-group">
                    <label htmlFor="excludeDirs">Exclude Directories (Optional)</label>
                    <input
                      type="text"
                      id="excludeDirs"
                      value={excludeDirs}
                      onChange={(e) => setExcludeDirs(e.target.value)}
                      placeholder="e.g. node_modules, .git"
                    />
                    <small>Comma-separated list of directories to exclude</small>
                  </div>

                  {/* File Extensions */}
                  <div className="form-group">
                    <label htmlFor="fileExtensions">File Extensions (Optional)</label>
                    <input
                      type="text"
                      id="fileExtensions"
                      value={fileExtensions}
                      onChange={(e) => setFileExtensions(e.target.value)}
                      placeholder="e.g. .py, .js"
                    />
                    <small>Comma-separated list of file extensions to include</small>
                  </div>

                  {/* Implementation Toggle */}
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={useMock} 
                        onChange={(e) => setUseMock(e.target.checked)} 
                      /> 
                      Use mock implementation (faster, less accurate)
                    </label>
                  </div>

                  <button 
                    type="button" 
                    className="btn"
                    onClick={handleAnalyzeProject}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Project'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Previous Analyses */}
          {(project.analyses || []).length > 0 && (
            <div className="card">
              <div className="card-header">
                Previous Analyses
              </div>
              <div className="card-body">
                <ul className="pattern-list">
                  {project.analyses.map(analysis => (
                    <li key={analysis.id} className="pattern-item">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <p><strong>Analysis:</strong> {analysis.timestamp}</p>
                          <p><strong>Pattern:</strong> {analysis.parameters.pattern_name || 'All patterns'}</p>
                          <p><strong>Category:</strong> {analysis.parameters.category || 'All categories'}</p>
                        </div>
                        <button 
                          className="btn"
                          onClick={() => navigate(`/results/${analysis.id}`)}
                        >
                          View Results
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProjectPage;
