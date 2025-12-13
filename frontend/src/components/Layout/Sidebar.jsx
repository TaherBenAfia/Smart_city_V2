/**
 * Sidebar - Navigation latérale
 */

import React from 'react';
import './Sidebar.css';

const Sidebar = ({ activeView, onViewChange }) => {
    const navItems = [
        { id: 'dashboard', label: 'Tableau de Bord', icon: '📊' },
        { id: 'interventions', label: 'Interventions', icon: '🔧' },
        { id: 'citizens', label: 'Citoyens', icon: '👥' },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <span className="logo-icon">🏙️</span>
                <h2>Neo-Sousse</h2>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <div
                        key={item.id}
                        className={`nav-item ${activeView === item.id ? 'active' : ''}`}
                        onClick={() => onViewChange(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="version-info">
                    <span>Smart City v1.0</span>
                    <span className="year">2030</span>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
