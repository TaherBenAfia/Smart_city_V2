/**
 * Navbar - Barre de recherche et profil utilisateur
 */

import React from 'react';
import './Navbar.css';

const Navbar = () => {
    return (
        <header className="navbar">
            <div className="navbar-search">
                <span className="search-icon">🔍</span>
                <input 
                    type="text" 
                    placeholder="Rechercher des capteurs, interventions, ou citoyens..." 
                    className="search-input"
                />
                <span className="search-shortcut">Ctrl+K</span>
            </div>

            <div className="navbar-actions">
                <button className="icon-btn" aria-label="Notifications">
                    <span className="icon">🔔</span>
                    <span className="notification-badge">3</span>
                </button>
                <div className="user-profile">
                    <div className="avatar">A</div>
                    <div className="user-info">
                        <span className="user-name">Admin</span>
                        <span className="user-role">Superviseur</span>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Navbar;
