/**
 * TopCitizens - Affichage des métriques des citoyens les plus engagés
 */

import React, { useState, useEffect } from 'react';
import { citoyensAPI } from '../../services/api';
import './TopCitizens.css';

const TopCitizens = () => {
    const [citizens, setCitizens] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTopCitizens();
    }, []);

    const fetchTopCitizens = async () => {
        try {
            const response = await citoyensAPI.getTopEngages(10);
            setCitizens(response.data || []);
        } catch (error) {
            console.error('Erreur:', error);
        } finally {
            setLoading(false);
        }
    };

    const getMobilityIcon = (mobility) => {
        const icons = {
            'VELO': '🚲',
            'TRANSPORT_COMMUN': '🚌',
            'COVOITURAGE': '🚗',
            'MARCHE': '🚶',
            'VEHICULE_ELECTRIQUE': '⚡'
        };
        return icons[mobility] || '🚶';
    };

    const getMedalEmoji = (rank) => {
        if (rank === 0) return '🥇';
        if (rank === 1) return '🥈';
        if (rank === 2) return '🥉';
        return '';
    };

    if (loading) {
        return <div className="loading"><div className="spinner"></div></div>;
    }

    return (
        <div className="top-citizens">
            <h3 className="section-title">🏆 Champions Éco-Citoyens</h3>

            {/* Podium pour les 3 premiers */}
            <div className="podium">
                {citizens.slice(0, 3).map((citizen, index) => (
                    <div key={citizen.id} className={`podium-item rank-${index + 1}`}>
                        <div className="podium-avatar">
                            {getMedalEmoji(index)}
                        </div>
                        <div className="podium-name">{citizen.nom_complet}</div>
                        <div className="podium-score">{citizen.score_engagement} pts</div>
                        <div className="podium-mobility">
                            {getMobilityIcon(citizen.preference_mobilite)}
                        </div>
                    </div>
                ))}
            </div>

            {/* Liste des autres citoyens */}
            <div className="citizens-list">
                {citizens.slice(3).map((citizen, index) => (
                    <div key={citizen.id} className="citizen-card">
                        <span className="citizen-rank">{index + 4}</span>
                        <div className="citizen-info">
                            <span className="citizen-name">{citizen.nom_complet}</span>
                            <span className="citizen-id">{citizen.identifiant}</span>
                        </div>
                        <div className="citizen-stats">
                            <span className="citizen-score">{citizen.score_engagement} pts</span>
                            <span className="citizen-mobility">
                                {getMobilityIcon(citizen.preference_mobilite)}
                            </span>
                            <span className="citizen-consultations">
                                {citizen.nombre_consultations} consultations
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TopCitizens;
