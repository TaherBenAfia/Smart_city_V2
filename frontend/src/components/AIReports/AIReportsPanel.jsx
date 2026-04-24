/**
 * AIReportsPanel - Interface pour la génération de rapports par IA
 */

import React, { useState, useEffect } from 'react';
import { aiReportsAPI } from '../../services/api';
import './AIReportsPanel.css';

const AIReportsPanel = () => {
    const [reportType, setReportType] = useState('air_quality');
    const [date, setDate] = useState('');
    const [loading, setLoading] = useState(false);
    const [report, setReport] = useState(null);
    const [error, setError] = useState(null);
    
    // Pour les suggestions
    const [capteurId, setCapteurId] = useState('');
    const [suggestion, setSuggestion] = useState(null);
    const [suggestLoading, setSuggestLoading] = useState(false);

    // Initialiser la date au jour actuel
    useEffect(() => {
        const today = new Date().toISOString().split('T')[0];
        setDate(today);
    }, []);

    const handleGenerateReport = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setReport(null);

        try {
            const response = await aiReportsAPI.generateReport(reportType, date);
            setReport(response.data);
        } catch (err) {
            setError(err.response?.data?.error || "Erreur lors de la génération du rapport.");
        } finally {
            setLoading(false);
        }
    };

    const handleSuggest = async (e) => {
        e.preventDefault();
        if (!capteurId.trim()) return;

        setSuggestLoading(true);
        setSuggestion(null);

        try {
            const response = await aiReportsAPI.suggest(capteurId);
            setSuggestion(response.data);
        } catch (err) {
            alert(err.response?.data?.error || "Erreur de suggestion");
        } finally {
            setSuggestLoading(false);
        }
    };

    return (
        <div className="ai-reports-panel">
            <div className="panel-header">
                <h2>🤖 Rapports d'Intelligence Artificielle</h2>
                <p>Générez des rapports d'analyse et des recommandations d'actions.</p>
            </div>

            <div className="ai-grid">
                {/* Colonne Principale: Génération de Rapports */}
                <div className="main-column">
                    <div className="card report-config-card">
                        <h3>Nouveau Rapport</h3>
                        <form onSubmit={handleGenerateReport} className="report-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>Type d'analyse</label>
                                    <select 
                                        className="input" 
                                        value={reportType}
                                        onChange={(e) => setReportType(e.target.value)}
                                        disabled={loading}
                                    >
                                        <option value="air_quality">Qualité de l'Air et Pollution</option>
                                        <option value="interventions">Performance de Maintenance</option>
                                        <option value="capteurs">État du Parc IoT</option>
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Date cible</label>
                                    <input 
                                        type="date" 
                                        className="input" 
                                        value={date}
                                        onChange={(e) => setDate(e.target.value)}
                                        disabled={loading}
                                    />
                                </div>
                            </div>
                            <button 
                                type="submit" 
                                className="btn btn-primary w-full"
                                disabled={loading}
                            >
                                {loading ? (
                                    <><span className="spinner-small"></span> Génération par IA en cours...</>
                                ) : (
                                    <>✨ Générer le Rapport</>
                                )}
                            </button>
                        </form>
                    </div>

                    {error && (
                        <div className="card error-card">
                            <p>⚠️ {error}</p>
                        </div>
                    )}

                    {report && !loading && (
                        <div className="card result-card">
                            <div className="card-header-flex">
                                <h3 className="card-title">Rapport d'Analyse</h3>
                                <div className="badge-group">
                                    <span className="badge badge-info">Mode: {report.mode}</span>
                                    <span className="badge badge-success">Généré avec succès</span>
                                </div>
                            </div>
                            <div className="report-content">
                                {report.content}
                            </div>
                            <div className="report-actions">
                                <button className="btn btn-outline btn-sm" onClick={() => window.print()}>🖨️ Imprimer</button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Colonne Secondaire: Suggestions Actions */}
                <div className="side-column">
                    <div className="card suggest-card">
                        <h3>Diagnostic Capteur</h3>
                        <p className="help-text">Obtenez une recommandation d'action ciblée pour un équipement spécifique.</p>
                        
                        <form onSubmit={handleSuggest} className="suggest-form">
                            <div className="form-group">
                                <input 
                                    type="text" 
                                    className="input" 
                                    placeholder="UUID du capteur..."
                                    value={capteurId}
                                    onChange={(e) => setCapteurId(e.target.value)}
                                    disabled={suggestLoading}
                                />
                            </div>
                            <button 
                                type="submit" 
                                className="btn btn-outline w-full"
                                disabled={suggestLoading || !capteurId.trim()}
                            >
                                {suggestLoading ? 'Analyse...' : '🔍 Diagnostiquer'}
                            </button>
                        </form>

                        {suggestion && !suggestLoading && (
                            <div className="suggestion-result">
                                <h4>Recommandation IA :</h4>
                                <div className="suggestion-content">
                                    {suggestion.suggestion}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AIReportsPanel;
