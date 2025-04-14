import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">Code Pattern Analyzer</Link>
          <nav>
            <ul className="nav-menu">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/file">Analyze File</Link></li>
              <li><Link to="/projects">Projects</Link></li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
