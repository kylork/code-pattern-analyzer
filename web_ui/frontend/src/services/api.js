import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API methods
const ApiService = {
  // Pattern related endpoints
  getPatterns: () => api.get('/patterns'),
  getCategories: () => api.get('/categories'),
  
  // Analysis endpoints
  analyzeCode: (fileContent, filename, patternName = null, category = null, useMock = false) => {
    return api.post('/analyze', { 
      file_content: fileContent, 
      filename, 
      pattern_name: patternName,
      category,
      use_mock: useMock 
    });
  },
  
  uploadFile: (file, patternName = null, category = null, useMock = false) => {
    const formData = new FormData();
    formData.append('file', file);
    
    if (patternName) {
      formData.append('pattern_name', patternName);
    }
    
    if (category) {
      formData.append('category', category);
    }
    
    formData.append('use_mock', useMock);
    
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getAnalysis: (analysisId) => api.get(`/analysis/${analysisId}`),
  getAnalysisHtml: (analysisId) => api.get(`/analysis/${analysisId}/html`),
  
  // Project endpoints
  createProject: (name, description = '') => api.post('/projects', { name, description }),
  getProjects: () => api.get('/projects'),
  getProject: (projectId) => api.get(`/projects/${projectId}`),
  uploadProjectFile: (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post(`/projects/${projectId}/files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  analyzeProject: (projectId, patternName = null, category = null, excludeDirs = null, fileExtensions = null, useMock = false) => {
    return api.post(`/projects/${projectId}/analyze`, {
      pattern_name: patternName,
      category,
      exclude_dirs: excludeDirs,
      file_extensions: fileExtensions,
      use_mock: useMock
    });
  },
};

export default ApiService;
