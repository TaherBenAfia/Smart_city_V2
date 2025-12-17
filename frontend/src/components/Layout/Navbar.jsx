import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
    const location = useLocation();

    return (
        <nav className="navbar">
            <div className="navbar-brand">
                Smart City Neo-Sousse 2030
            </div>
            <div className="navbar-links">
                <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
                    Dashboard
                </Link>
                <Link to="/questions" className={`nav-link ${location.pathname === '/questions' ? 'active' : ''}`}>
                    Questions Métiers
                </Link>
                <Link to="/map" className={`nav-link ${location.pathname === '/map' ? 'active' : ''}`}>
                    Carte Live
                </Link>
            </div>
        </nav>
    );
};

export default Navbar;
