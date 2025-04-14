import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ApiService from '../services/api';

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [showNewProjectForm, setShowNewProjectForm] = useState(false);

  // Load projects
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await ApiService.getProjects();
        setProjects(response.data.projects || []);
      } catch (err) {
        setError('Failed to load projects');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewProject(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle new project submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await ApiService.createProject(newProject.name, newProject.description);
      const projectId = response.data.project_id;
      
      // Refresh projects list
      const projectsResponse = await ApiService.getProjects();
      setProjects(projectsResponse.data.projects || []);
      
      // Reset form
      setNewProject({ name: '', description: '' });
      setShowNewProjectForm(false);
    } catch (err) {
      setError('Failed to create project');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-header">
          Projects
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Your Projects</h2>
            <button 
              className="btn" 
              onClick={() => setShowNewProjectForm(!showNewProjectForm)}
            >
              {showNewProjectForm ? 'Cancel' : 'New Project'}
            </button>
          </div>

          {/* New Project Form */}
          {showNewProjectForm && (
            <div className="card" style={{ marginBottom: '20px' }}>
              <div className="card-header">Create New Project</div>
              <div className="card-body">
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label htmlFor="name">Project Name</label>
                    <input 
                      type="text" 
                      id="name" 
                      name="name" 
                      value={newProject.name} 
                      onChange={handleInputChange} 
                      required 
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="description">Description</label>
                    <textarea 
                      id="description" 
                      name="description" 
                      value={newProject.description} 
                      onChange={handleInputChange} 
                      rows="3" 
                    />
                  </div>
                  <button type="submit" className="btn" disabled={isLoading}>
                    {isLoading ? 'Creating...' : 'Create Project'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="alert alert-error">
              <p>{error}</p>
            </div>
          )}

          {/* Projects list */}
          {isLoading && !showNewProjectForm ? (
            <p>Loading projects...</p>
          ) : projects.length === 0 ? (
            <p>No projects found. Create your first project to get started.</p>
          ) : (
            <div>
              {projects.map(project => (
                <div key={project.id} className="project-card">
                  <div>
                    <h3>{project.name}</h3>
                    {project.description && <p>{project.description}</p>}
                  </div>
                  <Link to={`/projects/${project.id}`} className="btn">
                    View Project
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectsPage;
