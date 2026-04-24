/**
 * Sidebar — Navigation latérale style Donezo
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { path: '/', label: 'Dashboard', icon: '📊' },
        { path: '/questions', label: 'Questions Métiers', icon: '❓' },
        { path: '/map', label: 'Carte Live', icon: '🗺️' },
    ];

    const moduleItems = [
        { path: '/compiler', label: 'Compilateur NL', icon: '⚡' },
        { path: '/automata', label: 'Automates FSM', icon: '🔄' },
        { path: '/ai-reports', label: 'Rapports IA', icon: '🤖' },
    ];

    const generalItems = [
        { path: '/api-docs', label: 'API Docs', icon: '📄', external: true, href: 'http://localhost:8000/api/docs/' },
    ];

    const renderNavItem = (item) => {
        const isActive = location.pathname === item.path;

        if (item.external) {
            return (
                <a
                    key={item.path}
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sidebar-item"
                >
                    <span className="sidebar-item-icon">{item.icon}</span>
                    <span className="sidebar-item-label">{item.label}</span>
                </a>
            );
        }

        return (
            <Link
                key={item.path}
                to={item.path}
                className={`sidebar-item ${isActive ? 'active' : ''}`}
            >
                <span className="sidebar-item-icon">{item.icon}</span>
                <span className="sidebar-item-label">{item.label}</span>
            </Link>
        );
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <div className="sidebar-logo">🏙️</div>
                <span className="sidebar-title">Neo-Sousse</span>
            </div>

            <nav className="sidebar-nav">
                <div className="sidebar-section">
                    <span className="sidebar-section-title">MENU</span>
                    {menuItems.map(renderNavItem)}
                </div>

                <div className="sidebar-section">
                    <span className="sidebar-section-title">MODULES</span>
                    {moduleItems.map(renderNavItem)}
                </div>

                <div className="sidebar-section">
                    <span className="sidebar-section-title">GÉNÉRAL</span>
                    {generalItems.map(renderNavItem)}
                </div>
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-version">
                    <span>Smart City v2.0</span>
                    <span className="sidebar-year">2030</span>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
