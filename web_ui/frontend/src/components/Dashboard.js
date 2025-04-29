import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

// Mock data for prototype - would be fetched from API in real implementation
const mockProjectData = {
  id: 'project-123',
  name: 'Sample Project',
  description: 'A sample project for demonstration',
  files: 42,
  lastAnalyzed: '2023-09-15',
  architecturalHealth: 0.78,
  patternDistribution: {
    designPatterns: 15,
    codeSmells: 8,
    architecturalStyles: {
      layered: 0.85,
      hexagonal: 0.32,
      clean: 0.56,
      eventDriven: 0.15
    },
    architecturalIntents: {
      separationOfConcerns: 0.82,
      informationHiding: 0.74,
      dependencyInversion: 0.65
    }
  },
  layers: {
    presentation: 12,
    business: 18,
    dataAccess: 8,
    domain: 14
  },
  violations: {
    total: 7,
    byType: {
      layerViolations: 4,
      dependencyCycles: 2,
      architecturalErosion: 1
    }
  },
  recentPatterns: [
    { id: 'pattern-1', name: 'Factory Method', file: 'src/services/factory.js', confidence: 0.95 },
    { id: 'pattern-2', name: 'Observer', file: 'src/events/eventBus.js', confidence: 0.92 },
    { id: 'pattern-3', name: 'Repository', file: 'src/data/userRepository.js', confidence: 0.89 },
    { id: 'pattern-4', name: 'Singleton', file: 'src/services/logger.js', confidence: 0.97 }
  ]
};

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [project, setProject] = useState(mockProjectData);
  const [isLoading, setIsLoading] = useState(false);

  // In a real implementation, this would fetch project data from the API
  useEffect(() => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setProject(mockProjectData);
      setIsLoading(false);
    }, 500);
  }, []);

  // Helper function to generate color based on health score
  const getHealthColor = (score) => {
    if (score >= 0.8) return '#4caf50';
    if (score >= 0.6) return '#8bc34a';
    if (score >= 0.4) return '#ffc107';
    if (score >= 0.2) return '#ff9800';
    return '#f44336';
  };

  if (isLoading) {
    return <div className="dashboard-loading">Loading project data...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>{project.name}</h1>
        <p className="dashboard-description">{project.description}</p>
        <div className="dashboard-meta">
          <span>{project.files} files</span>
          <span>Last analyzed: {project.lastAnalyzed}</span>
        </div>
      </div>

      <div className="dashboard-nav">
        <button 
          className={`dashboard-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`dashboard-nav-item ${activeTab === 'architecture' ? 'active' : ''}`}
          onClick={() => setActiveTab('architecture')}
        >
          Architecture
        </button>
        <button 
          className={`dashboard-nav-item ${activeTab === 'patterns' ? 'active' : ''}`}
          onClick={() => setActiveTab('patterns')}
        >
          Patterns
        </button>
        <button 
          className={`dashboard-nav-item ${activeTab === 'violations' ? 'active' : ''}`}
          onClick={() => setActiveTab('violations')}
        >
          Violations
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="dashboard-content">
          <div className="dashboard-cards">
            <div className="dashboard-card health-card">
              <h3>Architectural Health</h3>
              <div className="health-meter">
                <div 
                  className="health-meter-fill" 
                  style={{ 
                    width: `${project.architecturalHealth * 100}%`,
                    backgroundColor: getHealthColor(project.architecturalHealth)
                  }}
                ></div>
                <span className="health-meter-score">{Math.round(project.architecturalHealth * 100)}%</span>
              </div>
              <div className="health-description">
                Your project demonstrates good architectural health with room for improvement.
              </div>
            </div>

            <div className="dashboard-card pattern-card">
              <h3>Pattern Distribution</h3>
              <div className="pattern-counts">
                <div className="pattern-count">
                  <span className="count">{project.patternDistribution.designPatterns}</span>
                  <span className="label">Design Patterns</span>
                </div>
                <div className="pattern-count">
                  <span className="count">{project.patternDistribution.codeSmells}</span>
                  <span className="label">Code Smells</span>
                </div>
                <div className="pattern-count">
                  <span className="count">{project.violations.total}</span>
                  <span className="label">Violations</span>
                </div>
              </div>
            </div>

            <div className="dashboard-card layer-card">
              <h3>Layer Composition</h3>
              <div className="layer-bars">
                {Object.entries(project.layers).map(([layer, count]) => (
                  <div className="layer-bar-container" key={layer}>
                    <div className="layer-label">{layer.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</div>
                    <div className="layer-bar">
                      <div 
                        className={`layer-bar-fill layer-${layer}`} 
                        style={{ width: `${(count / Math.max(...Object.values(project.layers))) * 100}%` }}
                      ></div>
                      <span className="layer-count">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="dashboard-row">
            <div className="dashboard-card recent-patterns-card">
              <h3>Recently Detected Patterns</h3>
              <ul className="recent-patterns-list">
                {project.recentPatterns.map(pattern => (
                  <li key={pattern.id} className="recent-pattern">
                    <div className="pattern-name">{pattern.name}</div>
                    <div className="pattern-file">{pattern.file}</div>
                    <div className="pattern-confidence" 
                      style={{ backgroundColor: getHealthColor(pattern.confidence) }}>
                      {Math.round(pattern.confidence * 100)}%
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="dashboard-card architecture-preview-card">
              <h3>Architectural Style Detection</h3>
              <div className="architecture-styles">
                {Object.entries(project.patternDistribution.architecturalStyles).map(([style, confidence]) => (
                  <div className="architecture-style" key={style}>
                    <div className="style-name">{style.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</div>
                    <div className="style-meter">
                      <div 
                        className="style-meter-fill" 
                        style={{ 
                          width: `${confidence * 100}%`,
                          backgroundColor: getHealthColor(confidence)
                        }}
                      ></div>
                      <span className="style-meter-score">{Math.round(confidence * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="dashboard-row">
            <div className="dashboard-card recommendations-card">
              <h3>Recommendations</h3>
              <ul className="recommendations-list">
                <li>Address the 4 layer violations to improve architectural integrity</li>
                <li>Break the dependency cycles in data access components</li>
                <li>Consider implementing Dependency Injection for better component isolation</li>
                <li>Improve separation of concerns in the presentation layer</li>
              </ul>
              <button className="view-all-button">View All Recommendations</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'architecture' && (
        <div className="dashboard-content">
          <div className="architecture-visualization">
            <div className="vis-controls">
              <div className="control-group">
                <label htmlFor="vis-type">Visualization Type:</label>
                <select id="vis-type" className="vis-select">
                  <option value="force-directed">Force-Directed Graph</option>
                  <option value="layered">Layered Architecture</option>
                  <option value="dependency">Dependency Matrix</option>
                </select>
              </div>
              <div className="control-group">
                <label htmlFor="group-by">Group By:</label>
                <select id="group-by" className="vis-select">
                  <option value="layer">Layer</option>
                  <option value="type">Component Type</option>
                  <option value="module">Module</option>
                </select>
              </div>
              <div className="control-group">
                <label>
                  <input type="checkbox" id="show-violations" checked />
                  Show Violations
                </label>
              </div>
              <button className="vis-button">Reset View</button>
            </div>
            
            <div className="vis-container">
              {/* This iframe would load the actual visualization from the backend */}
              <iframe 
                src="/visualizations/component_graph.html" 
                title="Component Relationship Graph"
                className="vis-frame"
              ></iframe>
            </div>
            
            <div className="vis-legend">
              <h4>Legend</h4>
              <div className="legend-items">
                <div className="legend-item">
                  <span className="legend-color presentation"></span>
                  <span className="legend-label">Presentation Layer</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color business"></span>
                  <span className="legend-label">Business Layer</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color data-access"></span>
                  <span className="legend-label">Data Access Layer</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color domain"></span>
                  <span className="legend-label">Domain Layer</span>
                </div>
                <div className="legend-item">
                  <span className="legend-line normal"></span>
                  <span className="legend-label">Dependency</span>
                </div>
                <div className="legend-item">
                  <span className="legend-line violation"></span>
                  <span className="legend-label">Violation</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'patterns' && (
        <div className="dashboard-content">
          <div className="dashboard-placeholder patterns-placeholder">
            <h3>Pattern Catalog</h3>
            <p>This will show detailed information about all detected patterns in your project.</p>
            <div className="placeholder-visual patterns-visual"></div>
          </div>
        </div>
      )}

      {activeTab === 'violations' && (
        <div className="dashboard-content">
          <div className="dashboard-placeholder violations-placeholder">
            <h3>Architectural Violations</h3>
            <p>This will show details about architectural violations and recommendations to fix them.</p>
            <div className="placeholder-visual violations-visual"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;