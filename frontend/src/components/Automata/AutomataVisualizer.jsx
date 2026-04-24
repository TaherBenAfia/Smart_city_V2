/**
 * AutomataVisualizer - Visualiseur et contrôleur pour les Automates à États Finis
 */

import React, { useState, useEffect } from 'react';
import { automataAPI } from '../../services/api';
import './AutomataVisualizer.css';

const AutomataVisualizer = () => {
    const [activeTab, setActiveTab] = useState('capteur');
    const [definitions, setDefinitions] = useState({});
    const [entityId, setEntityId] = useState('');
    const [currentState, setCurrentState] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Charger les définitions au montage
    useEffect(() => {
        automataAPI.getDefinitions()
            .then(res => setDefinitions(res.data))
            .catch(err => console.error("Erreur chargement des définitions", err));
    }, []);

    // Recharger l'état quand l'onglet ou l'ID change
    useEffect(() => {
        if (entityId) {
            fetchStateAndHistory();
        } else {
            setCurrentState(null);
            setHistory([]);
            setError(null);
        }
    }, [activeTab, entityId]);

    const fetchStateAndHistory = async () => {
        if (!entityId) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const [stateRes, historyRes] = await Promise.all([
                automataAPI.getState(activeTab, entityId),
                automataAPI.getHistory(activeTab, entityId)
            ]);
            
            setCurrentState(stateRes.data.current_state);
            setHistory(historyRes.data.history || []);
        } catch (err) {
            setCurrentState(null);
            setHistory([]);
            if (err.response?.status === 404) {
                // Pas encore de transition, on prend l'état initial
                const def = definitions[activeTab];
                if (def) setCurrentState(def.initial_state);
            } else {
                setError("Entité introuvable ou erreur serveur.");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleTransition = async (event) => {
        if (!entityId) return;
        
        setLoading(true);
        setError(null);
        
        try {
            await automataAPI.transition(activeTab, entityId, event);
            await fetchStateAndHistory();
        } catch (err) {
            setError(err.response?.data?.error || "Erreur lors de la transition.");
            setLoading(false);
        }
    };

    // Rendu simple de l'automate en SVG
    const renderFSMDiagram = () => {
        const def = definitions[activeTab];
        if (!def) return <div className="loading">Chargement du modèle...</div>;

        const states = def.states;
        const radius = 40;
        const padding = 120;
        const width = states.length * padding;
        const height = 200;
        const cy = height / 2;

        return (
            <div className="diagram-container">
                <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
                    <defs>
                        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                            refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
                        </marker>
                        <marker id="arrowhead-active" markerWidth="10" markerHeight="7" 
                            refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a" />
                        </marker>
                    </defs>

                    {/* Dessiner les transitions (flèches) */}
                    {states.map((sourceState, i) => {
                        const transitions = def.transitions[sourceState] || {};
                        return Object.entries(transitions).map(([evt, targetState]) => {
                            const targetIdx = states.indexOf(targetState);
                            if (targetIdx === -1) return null;

                            const isForward = targetIdx > i;
                            const isSelf = targetIdx === i;
                            
                            const x1 = i * padding + padding/2;
                            const x2 = targetIdx * padding + padding/2;
                            
                            // L'état cible est-il l'état courant ?
                            const isActiveTransition = currentState === targetState && 
                                history.length > 0 && 
                                history[history.length-1].from_state === sourceState &&
                                history[history.length-1].event === evt;

                            const strokeColor = isActiveTransition ? "#16a34a" : "#cbd5e1";
                            const markerEnd = isActiveTransition ? "url(#arrowhead-active)" : "url(#arrowhead)";

                            if (isSelf) {
                                // Boucle sur lui-même
                                return (
                                    <path 
                                        key={`${sourceState}-${evt}`}
                                        d={`M ${x1} ${cy-radius} C ${x1-30} ${cy-radius-50}, ${x1+30} ${cy-radius-50}, ${x1} ${cy-radius}`}
                                        fill="none" 
                                        stroke={strokeColor} 
                                        strokeWidth="2"
                                        markerEnd={markerEnd}
                                    />
                                );
                            }

                            // Arc pour éviter que les flèches aller-retour se superposent
                            const curve = isForward ? -30 : 30;
                            const pathD = `M ${x1 + (isForward ? radius : -radius)} ${cy} Q ${(x1+x2)/2} ${cy+curve} ${x2 + (isForward ? -radius : radius)} ${cy}`;

                            return (
                                <g key={`${sourceState}-${evt}-${targetState}`}>
                                    <path 
                                        d={pathD}
                                        fill="none" 
                                        stroke={strokeColor} 
                                        strokeWidth={isActiveTransition ? "3" : "2"}
                                        markerEnd={markerEnd}
                                        strokeDasharray={isForward ? "none" : "5,5"}
                                    />
                                    <text 
                                        x={(x1+x2)/2} 
                                        y={cy + curve/2 + (isForward ? -5 : 15)} 
                                        fontSize="10" 
                                        fill={isActiveTransition ? "#15803d" : "#64748b"}
                                        textAnchor="middle"
                                    >
                                        {evt}
                                    </text>
                                </g>
                            );
                        });
                    })}

                    {/* Dessiner les états (noeuds) */}
                    {states.map((state, i) => {
                        const cx = i * padding + padding/2;
                        const isCurrent = currentState === state || (!currentState && i === 0);
                        
                        return (
                            <g key={state}>
                                <circle 
                                    cx={cx} 
                                    cy={cy} 
                                    r={radius} 
                                    fill={isCurrent ? "#dcfce7" : "#ffffff"} 
                                    stroke={isCurrent ? "#16a34a" : "#94a3b8"} 
                                    strokeWidth={isCurrent ? "3" : "2"}
                                />
                                <text 
                                    x={cx} 
                                    y={cy} 
                                    textAnchor="middle" 
                                    alignmentBaseline="middle"
                                    fontSize="11"
                                    fontWeight={isCurrent ? "bold" : "normal"}
                                    fill={isCurrent ? "#15803d" : "#334155"}
                                >
                                    {state}
                                </text>
                            </g>
                        );
                    })}
                </svg>
            </div>
        );
    };

    const renderControls = () => {
        const def = definitions[activeTab];
        if (!def || !currentState) return null;

        const availableTransitions = def.transitions[currentState] || {};
        const events = Object.keys(availableTransitions);

        return (
            <div className="controls-section">
                <h3>Actions Possibles (Événements)</h3>
                <div className="events-grid">
                    {def.events.map(evt => {
                        const isAvailable = events.includes(evt);
                        return (
                            <button
                                key={evt}
                                className={`btn ${isAvailable ? 'btn-primary' : 'btn-outline'}`}
                                disabled={!isAvailable || loading || !entityId}
                                onClick={() => handleTransition(evt)}
                            >
                                {evt} {isAvailable && '→ ' + availableTransitions[evt]}
                            </button>
                        );
                    })}
                </div>
            </div>
        );
    };

    return (
        <div className="automata-panel">
            <div className="panel-header">
                <h2>🔄 Moteur d'Automates (FSM)</h2>
                <p>Visualisation et contrôle du cycle de vie des entités.</p>
            </div>

            <div className="card">
                <div className="tabs">
                    <button 
                        className={`tab ${activeTab === 'capteur' ? 'active' : ''}`}
                        onClick={() => setActiveTab('capteur')}
                    >Capteurs</button>
                    <button 
                        className={`tab ${activeTab === 'intervention' ? 'active' : ''}`}
                        onClick={() => setActiveTab('intervention')}
                    >Interventions</button>
                    <button 
                        className={`tab ${activeTab === 'vehicule' ? 'active' : ''}`}
                        onClick={() => setActiveTab('vehicule')}
                    >Véhicules</button>
                </div>

                <div className="entity-selector">
                    <div className="input-group">
                        <label>ID de l'entité :</label>
                        <input 
                            type="text" 
                            className="input" 
                            placeholder={`Ex: ${activeTab === 'capteur' ? 'uuid-1234' : '1'}`}
                            value={entityId}
                            onChange={e => setEntityId(e.target.value)}
                        />
                        <button className="btn btn-outline" onClick={fetchStateAndHistory} disabled={!entityId}>
                            Charger
                        </button>
                    </div>
                    {error && <div className="error-text">{error}</div>}
                </div>

                <div className="diagram-section">
                    <h3>Graphe d'États</h3>
                    {renderFSMDiagram()}
                </div>

                {renderControls()}
            </div>

            {history.length > 0 && (
                <div className="card history-card">
                    <h3 className="card-title">Historique des Transitions</h3>
                    <table className="history-table">
                        <thead>
                            <tr>
                                <th>Date/Heure</th>
                                <th>État Initial</th>
                                <th>Événement</th>
                                <th>État Final</th>
                            </tr>
                        </thead>
                        <tbody>
                            {history.slice().reverse().map(item => (
                                <tr key={item.id}>
                                    <td>{new Date(item.timestamp).toLocaleString()}</td>
                                    <td><span className="badge badge-neutral">{item.from_state}</span></td>
                                    <td><strong>{item.event}</strong></td>
                                    <td><span className="badge badge-success">{item.to_state}</span></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default AutomataVisualizer;
