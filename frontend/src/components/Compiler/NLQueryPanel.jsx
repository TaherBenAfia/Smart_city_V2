/**
 * NLQueryPanel - Composant pour le Compilateur NL → SQL
 */

import React, { useState, useEffect } from 'react';
import { compilerAPI } from '../../services/api';
import './NLQueryPanel.css';

const NLQueryPanel = () => {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [examples, setExamples] = useState([]);
    const [showAst, setShowAst] = useState(false);

    useEffect(() => {
        // Charger les exemples au montage
        compilerAPI.getExamples()
            .then(res => setExamples(res.data.examples || []))
            .catch(err => console.error("Erreur de chargement des exemples", err));
    }, []);

    const handleExampleClick = (exampleQuery) => {
        setQuery(exampleQuery);
        // Exécuter la requête immédiatement
        executeQuery(exampleQuery);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            executeQuery(query);
        }
    };

    const executeQuery = async (queryText) => {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await compilerAPI.query(queryText);
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data || { error: 'Erreur inattendue de communication avec le serveur.' });
        } finally {
            setLoading(false);
        }
    };

    const renderResultsTable = () => {
        if (!result || !result.results || result.results.length === 0) {
            return <div className="no-data">Aucun résultat trouvé pour cette requête.</div>;
        }

        const columns = Object.keys(result.results[0]);

        return (
            <div className="table-responsive">
                <table className="results-table">
                    <thead>
                        <tr>
                            {columns.map(col => <th key={col}>{col}</th>)}
                        </tr>
                    </thead>
                    <tbody>
                        {result.results.map((row, idx) => (
                            <tr key={idx}>
                                {columns.map(col => (
                                    <td key={`${idx}-${col}`}>{
                                        typeof row[col] === 'object' && row[col] !== null 
                                            ? JSON.stringify(row[col]) 
                                            : String(row[col])
                                    }</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    return (
        <div className="nl-query-panel">
            <div className="panel-header">
                <h2>⚡ Compilateur NL → SQL</h2>
                <p>Interrogez la base de données Neo-Sousse en langage naturel.</p>
            </div>

            <div className="card query-input-card">
                <form onSubmit={handleSubmit} className="query-form">
                    <div className="input-group">
                        <input
                            type="text"
                            className="input query-input"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Ex: Affiche les 5 zones les plus polluées..."
                            disabled={loading}
                        />
                        <button type="submit" className="btn btn-primary" disabled={loading || !query.trim()}>
                            {loading ? <span className="spinner-small"></span> : 'Traduire & Exécuter'}
                        </button>
                    </div>
                </form>

                {examples.length > 0 && (
                    <div className="examples-section">
                        <span className="examples-label">Essayer :</span>
                        <div className="examples-list">
                            {examples.map((ex, idx) => (
                                <button 
                                    key={idx} 
                                    className="example-chip"
                                    onClick={() => handleExampleClick(ex)}
                                    disabled={loading}
                                >
                                    {ex}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {error && (
                <div className="card error-card">
                    <div className="error-header">
                        <span className="error-icon">⚠️</span>
                        <h3>Erreur de Compilation ({error.phase || 'Serveur'})</h3>
                    </div>
                    <p className="error-message">{error.error}</p>
                </div>
            )}

            {loading && (
                <div className="loading-card">
                    <div className="spinner"></div>
                    <span>Compilation et exécution en cours...</span>
                </div>
            )}

            {result && !loading && (
                <div className="results-container">
                    <div className="card sql-card">
                        <div className="card-header-flex">
                            <h3 className="card-title">Requête SQL Générée</h3>
                            <div className="card-actions">
                                <span className="badge badge-success">Succès</span>
                            </div>
                        </div>
                        <div className="code-block sql-code">
                            {result.sql}
                        </div>
                        
                        <div className="ast-toggle">
                            <button 
                                type="button" 
                                className="btn btn-outline btn-sm"
                                onClick={() => setShowAst(!showAst)}
                            >
                                {showAst ? 'Masquer l\'AST' : 'Afficher l\'AST'}
                            </button>
                        </div>

                        {showAst && (
                            <div className="ast-viewer">
                                <div className="code-block ast-code">
                                    {JSON.stringify(result.ast, null, 2)}
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="card data-card">
                        <div className="card-header-flex">
                            <h3 className="card-title">Résultats d'Exécution</h3>
                            <span className="badge badge-neutral">{result.results_count} lignes</span>
                        </div>
                        {renderResultsTable()}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NLQueryPanel;
