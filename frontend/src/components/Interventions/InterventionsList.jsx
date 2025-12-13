/**
 * InterventionsList - Liste interactive des interventions
 */

import React, { useState, useEffect } from 'react';
import { interventionsAPI } from '../../services/api';
import './InterventionsList.css';

const InterventionsList = () => {
    const [interventions, setInterventions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchInterventions();
    }, [filter]);

    const fetchInterventions = async () => {
        setLoading(true);
        try {
            const params = filter !== 'all' ? { statut: filter } : {};
            const response = await interventionsAPI.getAll(params);
            setInterventions(response.data.results || response.data || []);
        } catch (error) {
            console.error('Erreur:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatutBadge = (statut) => {
        const statuts = {
            'TERMINEE': 'success',
            'EN_COURS': 'warning',
            'PLANIFIEE': 'info',
            'ANNULEE': 'danger'
        };
        return statuts[statut] || 'info';
    };

    const getNatureIcon = (nature) => {
        const icons = {
            'PREDICTIVE': '🔮',
            'CORRECTIVE': '🔧',
            'CURATIVE': '🛠️'
        };
        return icons[nature] || '📋';
    };

    return (
        <div className="interventions-list card">
            <div className="list-header">
                <h3 className="card-title">🔧 Interventions de Maintenance</h3>
                <div className="filter-group">
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">Tous les statuts</option>
                        <option value="TERMINEE">Terminées</option>
                        <option value="EN_COURS">En cours</option>
                        <option value="PLANIFIEE">Planifiées</option>
                        <option value="ANNULEE">Annulées</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            ) : (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Date</th>
                                <th>Nature</th>
                                <th>Capteur</th>
                                <th>Zone</th>
                                <th>Intervenant</th>
                                <th>Validateur</th>
                                <th>Durée</th>
                                <th>Coût</th>
                                <th>CO2 Réduit</th>
                                <th>Statut</th>
                            </tr>
                        </thead>
                        <tbody>
                            {interventions.map((intervention) => (
                                <tr key={intervention.id} className="intervention-row">
                                    <td className="id-cell">#{intervention.id}</td>
                                    <td>
                                        {new Date(intervention.date_heure).toLocaleDateString('fr-FR', {
                                            day: '2-digit',
                                            month: 'short',
                                            year: 'numeric'
                                        })}
                                    </td>
                                    <td>
                                        <span className="nature-badge">
                                            {getNatureIcon(intervention.nature)} {intervention.nature}
                                        </span>
                                    </td>
                                    <td>{intervention.capteur_type}</td>
                                    <td>{intervention.capteur_arrondissement}</td>
                                    <td className="technicien-cell">{intervention.intervenant_nom}</td>
                                    <td className="technicien-cell">{intervention.validateur_nom}</td>
                                    <td>{intervention.duree_minutes} min</td>
                                    <td className="cout-cell">{parseFloat(intervention.cout).toFixed(2)} TND</td>
                                    <td className="co2-cell">
                                        {intervention.reduction_co2
                                            ? `${parseFloat(intervention.reduction_co2).toFixed(2)} kg`
                                            : '-'
                                        }
                                    </td>
                                    <td>
                                        <span className={`badge ${getStatutBadge(intervention.statut)}`}>
                                            {intervention.statut}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {interventions.length === 0 && (
                        <div className="empty-state">
                            Aucune intervention trouvée
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default InterventionsList;
