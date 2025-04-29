import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div>
      <div className="card">
        <div className="card-header">
          Code Pattern Analyzer
        </div>
        <div className="card-body">
          <h2>Welcome to the Code Pattern Analyzer Web UI</h2>
          <p>
            This tool helps you analyze your code for patterns, design patterns, 
            and potential code smells across multiple programming languages.
          </p>
          <p>
            Using advanced parsing techniques, the analyzer provides insights into your 
            codebase structure and helps identify opportunities for improvement.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          Get Started
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col">
              <h3>Analyze a Single File</h3>
              <p>Upload and analyze a single file to identify patterns.</p>
              <Link to="/file" className="btn">
                Analyze File
              </Link>
            </div>
            <div className="col">
              <h3>Manage Projects</h3>
              <p>Create projects to organize and analyze multiple files together.</p>
              <Link to="/projects" className="btn">
                View Projects
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          Features
        </div>
        <div className="card-body">
          <ul>
            <li>Multi-language support (Python, JavaScript, and more)</li>
            <li>Design pattern detection (Singleton, Factory Method, etc.)</li>
            <li>Code smell identification</li>
            <li>Interactive visualization of results</li>
            <li>Project-based analysis</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
