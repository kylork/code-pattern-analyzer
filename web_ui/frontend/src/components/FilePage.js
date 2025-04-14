import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ApiService from '../services/api';

const FilePage = () => {
  const [file, setFile] = useState(null);
  const [code, setCode] = useState('');
  const [filename, setFilename] = useState('');
  const [patterns, setPatterns] = useState([]);
  const [categories, setCategories] = useState({});
  const [selectedPattern, setSelectedPattern] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [useMock, setUseMock] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadMethod, setUploadMethod] = useState('file'); // 'file' or 'code'
  
  const navigate = useNavigate();

  // Load patterns and categories
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [patternsResponse, categoriesResponse] = await Promise.all([
          ApiService.getPatterns(),
          ApiService.getCategories()
        ]);
        
        setPatterns(patternsResponse.data.patterns || []);
        setCategories(categoriesResponse.data.categories || {});
      } catch (err) {
        setError('Failed to load patterns and categories');
        console.error(err);
      }
    };

    fetchData();
  }, []);

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setFilename(e.target.files[0].name);
    }
  };

  // Handle file drop
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      setFilename(e.dataTransfer.files[0].name);
    }
  }, []);

  // Handle drag events
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
  }, []);

  // Handle analysis submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      let response;

      if (uploadMethod === 'file' && file) {
        // File upload method
        response = await ApiService.uploadFile(
          file, 
          selectedPattern || null, 
          selectedCategory || null, 
          useMock
        );
      } else if (uploadMethod === 'code' && code) {
        // Direct code input method
        response = await ApiService.analyzeCode(
          code,
          filename || 'untitled.txt',
          selectedPattern || null,
          selectedCategory || null,
          useMock
        );
      } else {
        throw new Error('Please provide a file or code to analyze');
      }

      // Navigate to results page with the analysis ID
      if (response.data && response.data.analysis_id) {
        navigate(`/results/${response.data.analysis_id}`);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      setError(err.message || 'Failed to analyze code');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          Analyze File
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            {/* Upload Method Selection */}
            <div className="form-group">
              <div>
                <label>
                  <input 
                    type="radio" 
                    name="uploadMethod" 
                    value="file" 
                    checked={uploadMethod === 'file'} 
                    onChange={() => setUploadMethod('file')} 
                  /> 
                  Upload File
                </label>
                <label style={{ marginLeft: '20px' }}>
                  <input 
                    type="radio" 
                    name="uploadMethod" 
                    value="code" 
                    checked={uploadMethod === 'code'} 
                    onChange={() => setUploadMethod('code')} 
                  /> 
                  Paste Code
                </label>
              </div>
            </div>

            {/* File Upload */}
            {uploadMethod === 'file' && (
              <div className="form-group">
                <label>Select File</label>
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
            )}

            {/* Code Input */}
            {uploadMethod === 'code' && (
              <>
                <div className="form-group">
                  <label htmlFor="filename">Filename</label>
                  <input 
                    type="text" 
                    id="filename" 
                    value={filename} 
                    onChange={(e) => setFilename(e.target.value)} 
                    placeholder="filename.py"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="code">Code</label>
                  <textarea 
                    id="code" 
                    value={code} 
                    onChange={(e) => setCode(e.target.value)} 
                    rows="10" 
                    placeholder="Paste your code here..."
                    required
                  />
                </div>
              </>
            )}

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

            {/* Error display */}
            {error && (
              <div className="alert alert-error">
                <p>{error}</p>
              </div>
            )}

            {/* Submit button */}
            <button 
              type="submit" 
              className="btn" 
              disabled={isLoading || (uploadMethod === 'file' && !file) || (uploadMethod === 'code' && !code)}
            >
              {isLoading ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default FilePage;
