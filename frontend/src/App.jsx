/**
 * App.jsx - Smart City Educational Platform
 * Main entry point with Routing
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import Dashboard from './components/Dashboard/Dashboard';
import BusinessQuestions from './components/Questions/BusinessQuestions';
import MapPage from './components/Map/MapPage';
import './index.css';

function App() {
    return (
        <Router>
            <div className="app-container">
                <Navbar />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/questions" element={<BusinessQuestions />} />
                        <Route path="/map" element={<MapPage />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
