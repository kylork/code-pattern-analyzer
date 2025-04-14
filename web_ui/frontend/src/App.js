import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Components
import HomePage from './components/HomePage';
import FilePage from './components/FilePage';
import ProjectsPage from './components/ProjectsPage';
import ProjectPage from './components/ProjectPage';
import ResultsPage from './components/ResultsPage';
import Header from './components/Header';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="content">
          <div className="container">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/file" element={<FilePage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/projects/:projectId" element={<ProjectPage />} />
              <Route path="/results/:analysisId" element={<ResultsPage />} />
            </Routes>
          </div>
        </main>
        <footer className="footer">
          <div className="container">
            <p>Code Pattern Analyzer &copy; {new Date().getFullYear()}</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
