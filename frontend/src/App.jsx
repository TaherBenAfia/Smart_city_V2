/**
 * App.jsx - Smart City Educational Platform
 * Main entry point with Routing
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import Dashboard from './components/Dashboard/Dashboard';
import BusinessQuestions from './components/Questions/BusinessQuestions';
import MapPage from './components/Map/MapPage';
import NLQueryPanel from './components/Compiler/NLQueryPanel';
import AutomataVisualizer from './components/Automata/AutomataVisualizer';
import AIReportsPanel from './components/AIReports/AIReportsPanel';
import './index.css';

function App() {
    return (
        <Router>
            <div className="app-container">
                <Sidebar />
                <Navbar />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/questions" element={<BusinessQuestions />} />
                        <Route path="/map" element={<MapPage />} />
                        <Route path="/compiler" element={<NLQueryPanel />} />
                        <Route path="/automata" element={<AutomataVisualizer />} />
                        <Route path="/ai-reports" element={<AIReportsPanel />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
