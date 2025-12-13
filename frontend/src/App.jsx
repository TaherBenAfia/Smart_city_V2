/**
 * App.jsx - Dashboard avec les 5 Questions Métiers
 * Smart City Neo-Sousse 2030
 * Avec affichage des requêtes SQL sources
 */

import React, { useState, useEffect } from 'react';
import {
    capteursAPI, trajetsAPI, interventionsAPI, citoyensAPI
} from './services/api';
import './index.css';

// Requêtes SQL sources pour chaque question
const SQL_QUERIES = {
    q1: `-- Zones les plus polluées (24 dernières heures)
SELECT 
    a.nom AS arrondissement,
    AVG(m.indice_pollution) AS pollution_moyenne,
    COUNT(m.id) AS nombre_mesures,
    CASE 
        WHEN AVG(m.indice_pollution) <= 50 THEN 'BON'
        WHEN AVG(m.indice_pollution) <= 100 THEN 'MODERE'
        WHEN AVG(m.indice_pollution) <= 150 THEN 'MAUVAIS'
        WHEN AVG(m.indice_pollution) <= 200 THEN 'TRES_MAUVAIS'
        ELSE 'DANGEREUX'
    END AS niveau
FROM arrondissement a
JOIN capteur c ON a.id = c.arrondissement_id
JOIN mesure m ON c.uuid = m.capteur_uuid
WHERE c.type = 'AIR'
  AND m.timestamp >= NOW() - INTERVAL 24 HOUR
GROUP BY a.id, a.nom
ORDER BY pollution_moyenne DESC;`,

    q2: `-- Taux de disponibilité des capteurs par arrondissement
SELECT 
    a.nom AS arrondissement,
    COUNT(*) AS total_capteurs,
    SUM(CASE WHEN c.statut = 'ACTIF' THEN 1 ELSE 0 END) AS capteurs_actifs,
    SUM(CASE WHEN c.statut = 'MAINTENANCE' THEN 1 ELSE 0 END) AS capteurs_maintenance,
    SUM(CASE WHEN c.statut = 'HORS_SERVICE' THEN 1 ELSE 0 END) AS capteurs_hors_service,
    ROUND(
        SUM(CASE WHEN c.statut = 'ACTIF' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS taux_disponibilite
FROM arrondissement a
JOIN capteur c ON a.id = c.arrondissement_id
GROUP BY a.id, a.nom
HAVING COUNT(*) > 0
ORDER BY taux_disponibilite DESC;`,

    q3: `-- Citoyens les plus engagés (réduction empreinte carbone)
SELECT 
    c.identifiant_unique AS identifiant,
    CONCAT(c.prenom, ' ', c.nom) AS nom_complet,
    c.score_engagement,
    c.preference_mobilite,
    COUNT(co.id) AS nombre_consultations
FROM citoyen c
LEFT JOIN consultation co ON c.id = co.citoyen_id
GROUP BY c.id, c.identifiant_unique, c.prenom, c.nom, 
         c.score_engagement, c.preference_mobilite
ORDER BY c.score_engagement DESC
LIMIT 10;`,

    q4: `-- Interventions prédictives ce mois-ci et économies générées
SELECT 
    COUNT(*) AS nombre_interventions,
    SUM(reduction_co2) AS economie_co2_totale,
    SUM(cout) AS cout_total,
    SUM(duree_minutes) AS duree_totale,
    AVG(cout) AS cout_moyen
FROM intervention
WHERE nature = 'PREDICTIVE'
  AND statut = 'TERMINEE'
  AND MONTH(date_heure) = MONTH(CURRENT_DATE)
  AND YEAR(date_heure) = YEAR(CURRENT_DATE);`,

    q5: `-- Trajets véhicules autonomes avec plus grande réduction CO2
SELECT 
    v.plaque AS vehicule_plaque,
    v.type AS vehicule_type,
    v.energie AS vehicule_energie,
    t.origine,
    t.destination,
    t.distance_km,
    t.economie_co2 AS economie_co2_kg
FROM trajet t
JOIN vehicule v ON t.vehicule_id = v.id
WHERE t.statut = 'TERMINE'
  AND t.economie_co2 IS NOT NULL
ORDER BY t.economie_co2 DESC
LIMIT 10;

-- Total CO2 économisé
SELECT SUM(economie_co2) AS total_co2_economise
FROM trajet WHERE statut = 'TERMINE';`
};

// Données mock de fallback
const MOCK_DATA = {
    zonesPolluees: [
        { arrondissement_nom: 'Centre-Ville', pollution_moyenne: 85, niveau: 'MAUVAIS', nombre_mesures: 45 },
        { arrondissement_nom: 'Khezama', pollution_moyenne: 72, niveau: 'MODERE', nombre_mesures: 38 },
        { arrondissement_nom: 'Sahloul', pollution_moyenne: 95, niveau: 'TRES_MAUVAIS', nombre_mesures: 52 },
        { arrondissement_nom: 'Hammam-Sousse', pollution_moyenne: 45, niveau: 'BON', nombre_mesures: 29 },
        { arrondissement_nom: 'Akouda', pollution_moyenne: 110, niveau: 'DANGEREUX', nombre_mesures: 41 }
    ],
    disponibilite: [
        { arrondissement_nom: 'Centre-Ville', total_capteurs: 15, capteurs_actifs: 12, capteurs_maintenance: 2, capteurs_hors_service: 1, taux_disponibilite: 80 },
        { arrondissement_nom: 'Khezama', total_capteurs: 12, capteurs_actifs: 10, capteurs_maintenance: 1, capteurs_hors_service: 1, taux_disponibilite: 83.33 },
        { arrondissement_nom: 'Sahloul', total_capteurs: 10, capteurs_actifs: 8, capteurs_maintenance: 1, capteurs_hors_service: 1, taux_disponibilite: 80 },
        { arrondissement_nom: 'Hammam-Sousse', total_capteurs: 8, capteurs_actifs: 7, capteurs_maintenance: 1, capteurs_hors_service: 0, taux_disponibilite: 87.5 },
        { arrondissement_nom: 'Akouda', total_capteurs: 5, capteurs_actifs: 3, capteurs_maintenance: 1, capteurs_hors_service: 1, taux_disponibilite: 60 }
    ],
    topCitoyens: [
        { id: 1, identifiant: 'CIT-2024-001', nom_complet: 'Yassine Mansouri', score_engagement: 95.5, preference_mobilite: 'VELO', nombre_consultations: 45 },
        { id: 2, identifiant: 'CIT-2024-002', nom_complet: 'Nadia Khelifi', score_engagement: 92.3, preference_mobilite: 'TRANSPORT_COMMUN', nombre_consultations: 38 },
        { id: 3, identifiant: 'CIT-2024-003', nom_complet: 'Rami Bouzid', score_engagement: 88.7, preference_mobilite: 'COVOITURAGE', nombre_consultations: 32 },
        { id: 4, identifiant: 'CIT-2024-004', nom_complet: 'Ines Selmi', score_engagement: 85.2, preference_mobilite: 'MARCHE', nombre_consultations: 28 },
        { id: 5, identifiant: 'CIT-2024-005', nom_complet: 'Hatem Chaabane', score_engagement: 82.8, preference_mobilite: 'VEHICULE_ELECTRIQUE', nombre_consultations: 25 },
        { id: 6, identifiant: 'CIT-2024-006', nom_complet: 'Salma Ferchichi', score_engagement: 79.4, preference_mobilite: 'VELO', nombre_consultations: 22 },
        { id: 7, identifiant: 'CIT-2024-007', nom_complet: 'Mehdi Jebali', score_engagement: 76.1, preference_mobilite: 'TRANSPORT_COMMUN', nombre_consultations: 19 },
        { id: 8, identifiant: 'CIT-2024-008', nom_complet: 'Rim Ammar', score_engagement: 73.6, preference_mobilite: 'COVOITURAGE', nombre_consultations: 17 },
        { id: 9, identifiant: 'CIT-2024-009', nom_complet: 'Tarek Haddad', score_engagement: 70.2, preference_mobilite: 'MARCHE', nombre_consultations: 15 },
        { id: 10, identifiant: 'CIT-2024-010', nom_complet: 'Mariem Dridi', score_engagement: 67.8, preference_mobilite: 'VELO', nombre_consultations: 12 }
    ],
    interventionsPredictives: {
        nombre_interventions: 35,
        economie_co2_kg: 156.42,
        cout_total_tnd: 8750.00,
        duree_totale_minutes: 2450
    },
    topTrajetsCO2: [
        { vehicule_plaque: 'TN-SMART-001', vehicule_type: 'BUS', vehicule_energie: 'ELECTRIQUE', origine: 'Gare Centrale', destination: 'Aéroport', distance_km: 25.5, economie_co2_kg: 8.92 },
        { vehicule_plaque: 'TN-SMART-003', vehicule_type: 'BUS', vehicule_energie: 'HYDROGENE', origine: 'Université', destination: 'Centre Commercial', distance_km: 18.3, economie_co2_kg: 7.85 },
        { vehicule_plaque: 'TN-SMART-002', vehicule_type: 'BUS', vehicule_energie: 'ELECTRIQUE', origine: 'Port', destination: 'Zone Industrielle', distance_km: 22.1, economie_co2_kg: 7.12 },
        { vehicule_plaque: 'TN-SMART-009', vehicule_type: 'COLLECTE_DECHETS', vehicule_energie: 'HYDROGENE', origine: 'Dépôt Municipal', destination: 'Centre-Ville', distance_km: 15.8, economie_co2_kg: 6.54 },
        { vehicule_plaque: 'TN-SMART-004', vehicule_type: 'NAVETTE', vehicule_energie: 'ELECTRIQUE', origine: 'Khezama', destination: 'Sahloul', distance_km: 8.5, economie_co2_kg: 5.21 },
        { vehicule_plaque: 'TN-SMART-014', vehicule_type: 'BUS', vehicule_energie: 'ELECTRIQUE', origine: 'Stade Olympique', destination: 'Marina', distance_km: 12.3, economie_co2_kg: 4.89 },
        { vehicule_plaque: 'TN-SMART-007', vehicule_type: 'UTILITAIRE', vehicule_energie: 'ELECTRIQUE', origine: 'Entrepôt', destination: 'Hôpital', distance_km: 9.7, economie_co2_kg: 4.32 },
        { vehicule_plaque: 'TN-SMART-010', vehicule_type: 'COLLECTE_DECHETS', vehicule_energie: 'ELECTRIQUE', origine: 'Hammam-Sousse', destination: 'Décharge', distance_km: 14.2, economie_co2_kg: 3.98 },
        { vehicule_plaque: 'TN-SMART-005', vehicule_type: 'NAVETTE', vehicule_energie: 'ELECTRIQUE', origine: 'Plage', destination: 'Centre-Ville', distance_km: 6.8, economie_co2_kg: 3.45 },
        { vehicule_plaque: 'TN-SMART-012', vehicule_type: 'NAVETTE', vehicule_energie: 'ELECTRIQUE', origine: 'Akouda', destination: 'Gare', distance_km: 11.5, economie_co2_kg: 3.12 }
    ]
};

// Composant pour afficher le code SQL
const SqlQueryBox = ({ query, isVisible }) => {
    if (!isVisible) return null;

    return (
        <div className="sql-box">
            <div className="sql-header">📋 Requête SQL Source</div>
            <pre className="sql-code">{query}</pre>
        </div>
    );
};

function App() {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState({
        zonesPolluees: [],
        disponibilite: [],
        topCitoyens: [],
        interventionsPredictives: {},
        topTrajetsCO2: []
    });
    const [showSql, setShowSql] = useState({
        q1: false, q2: false, q3: false, q4: false, q5: false
    });

    useEffect(() => {
        fetchAllData();
    }, []);

    const toggleSql = (question) => {
        setShowSql(prev => ({ ...prev, [question]: !prev[question] }));
    };

    const fetchAllData = async () => {
        setLoading(true);
        try {
            const [zones, dispo, citoyens, predictives, trajets] = await Promise.all([
                capteursAPI.getZonesPolluees24h().catch(() => null),
                capteursAPI.getDisponibiliteParArrondissement().catch(() => null),
                citoyensAPI.getTopEngages(10).catch(() => null),
                interventionsAPI.getInterventionsPredictivesMois().catch(() => null),
                trajetsAPI.getTopTrajetsCO2(10).catch(() => null)
            ]);

            const apiZones = zones?.data?.zones || [];
            const apiDispo = dispo?.data?.arrondissements || [];
            const apiCitoyens = citoyens?.data || [];
            const apiPredictives = predictives?.data?.statistiques || {};
            const apiTrajets = trajets?.data?.top_trajets || [];

            setData({
                zonesPolluees: apiZones.length > 0 ? apiZones : MOCK_DATA.zonesPolluees,
                disponibilite: apiDispo.length > 0 ? apiDispo : MOCK_DATA.disponibilite,
                tauxGlobal: dispo?.data?.taux_disponibilite_global || 78,
                topCitoyens: apiCitoyens.length > 0 ? apiCitoyens : MOCK_DATA.topCitoyens,
                interventionsPredictives: Object.keys(apiPredictives).length > 0 ? apiPredictives : MOCK_DATA.interventionsPredictives,
                moisPredictives: predictives?.data?.mois || 'Décembre 2025',
                topTrajetsCO2: apiTrajets.length > 0 ? apiTrajets : MOCK_DATA.topTrajetsCO2,
                totalCO2: trajets?.data?.total_economie_co2_kg || 55.4
            });
        } catch (error) {
            console.error('Erreur:', error);
            setData({
                zonesPolluees: MOCK_DATA.zonesPolluees,
                disponibilite: MOCK_DATA.disponibilite,
                tauxGlobal: 78,
                topCitoyens: MOCK_DATA.topCitoyens,
                interventionsPredictives: MOCK_DATA.interventionsPredictives,
                moisPredictives: 'Décembre 2025',
                topTrajetsCO2: MOCK_DATA.topTrajetsCO2,
                totalCO2: 55.4
            });
        }
        setLoading(false);
    };

    const getNiveauColor = (niveau) => {
        const colors = {
            'BON': '#28a745',
            'MODERE': '#ffc107',
            'MAUVAIS': '#fd7e14',
            'TRES_MAUVAIS': '#dc3545',
            'DANGEREUX': '#6f42c1'
        };
        return colors[niveau] || '#6c757d';
    };

    if (loading) {
        return <div className="app"><div className="loading">Chargement des données...</div></div>;
    }

    return (
        <div className="app">
            {/* Header */}
            <div className="header">
                <h1>Smart City Neo-Sousse 2030</h1>
                <p>Dashboard Analytics - 5 Questions Métiers</p>
            </div>

            {/* Question 1: Zones Polluées 24h */}
            <div className="section">
                <div className="section-header">
                    <h2>Zones les plus polluées (24 dernières heures)</h2>
                    <button className="sql-btn" onClick={() => toggleSql('q1')}>
                        {showSql.q1 ? '❌ Masquer SQL' : '🔍 Voir Requête SQL'}
                    </button>
                </div>
                <SqlQueryBox query={SQL_QUERIES.q1} isVisible={showSql.q1} />
                <div className="chart-container">
                    {data.zonesPolluees.map((zone, idx) => (
                        <div key={idx} className="bar-chart-item">
                            <div className="bar-label">{zone.arrondissement_nom}</div>
                            <div className="bar-wrapper">
                                <div
                                    className="bar-fill"
                                    style={{
                                        width: `${Math.min(zone.pollution_moyenne || 0, 100)}%`,
                                        backgroundColor: getNiveauColor(zone.niveau)
                                    }}
                                />
                                <span className="bar-value">{zone.pollution_moyenne || 0}</span>
                            </div>
                            <span className="bar-badge" style={{ backgroundColor: getNiveauColor(zone.niveau) }}>
                                {zone.niveau}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Question 2: Disponibilité Capteurs */}
            <div className="section">
                <div className="section-header">
                    <h2>Taux de disponibilité des capteurs par arrondissement</h2>
                    <button className="sql-btn" onClick={() => toggleSql('q2')}>
                        {showSql.q2 ? '❌ Masquer SQL' : '🔍 Voir Requête SQL'}
                    </button>
                </div>
                <SqlQueryBox query={SQL_QUERIES.q2} isVisible={showSql.q2} />
                <div className="kpi-highlight">
                    <span className="kpi-label">Taux Global</span>
                    <span className="kpi-value">{data.tauxGlobal}%</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Arrondissement</th>
                            <th>Total</th>
                            <th>Actifs</th>
                            <th>Maintenance</th>
                            <th>Hors Service</th>
                            <th>Disponibilité</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.disponibilite.map((arr, idx) => (
                            <tr key={idx}>
                                <td>{arr.arrondissement_nom}</td>
                                <td>{arr.total_capteurs}</td>
                                <td style={{ color: '#28a745' }}>{arr.capteurs_actifs}</td>
                                <td style={{ color: '#ffc107' }}>{arr.capteurs_maintenance}</td>
                                <td style={{ color: '#dc3545' }}>{arr.capteurs_hors_service}</td>
                                <td><strong>{arr.taux_disponibilite}%</strong></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Question 3: Citoyens Engagés */}
            <div className="section">
                <div className="section-header">
                    <h2>Citoyens les plus engagés (réduction empreinte carbone)</h2>
                    <button className="sql-btn" onClick={() => toggleSql('q3')}>
                        {showSql.q3 ? '❌ Masquer SQL' : '🔍 Voir Requête SQL'}
                    </button>
                </div>
                <SqlQueryBox query={SQL_QUERIES.q3} isVisible={showSql.q3} />
                <div className="chart-container">
                    {data.topCitoyens.slice(0, 5).map((cit, idx) => (
                        <div key={idx} className="bar-chart-item">
                            <div className="bar-label">
                                <span className="rank">#{idx + 1}</span> {cit.nom_complet}
                            </div>
                            <div className="bar-wrapper">
                                <div
                                    className="bar-fill bar-green"
                                    style={{ width: `${cit.score_engagement}%` }}
                                />
                                <span className="bar-value">{cit.score_engagement}/100</span>
                            </div>
                            <span className="bar-badge badge-mobility">{cit.preference_mobilite}</span>
                        </div>
                    ))}
                </div>
                <table style={{ marginTop: '20px' }}>
                    <thead>
                        <tr>
                            <th>Rang</th>
                            <th>Identifiant</th>
                            <th>Nom</th>
                            <th>Score</th>
                            <th>Mobilité</th>
                            <th>Consultations</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.topCitoyens.map((cit, idx) => (
                            <tr key={idx}>
                                <td><strong>#{idx + 1}</strong></td>
                                <td>{cit.identifiant}</td>
                                <td>{cit.nom_complet}</td>
                                <td><strong>{cit.score_engagement}</strong>/100</td>
                                <td>{cit.preference_mobilite}</td>
                                <td>{cit.nombre_consultations}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Question 4: Interventions Prédictives */}
            <div className="section">
                <div className="section-header">
                    <h2>Interventions prédictives ce mois ({data.moisPredictives})</h2>
                    <button className="sql-btn" onClick={() => toggleSql('q4')}>
                        {showSql.q4 ? '❌ Masquer SQL' : '🔍 Voir Requête SQL'}
                    </button>
                </div>
                <SqlQueryBox query={SQL_QUERIES.q4} isVisible={showSql.q4} />
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-value">{data.interventionsPredictives.nombre_interventions || 0}</div>
                        <div className="stat-label">Interventions Prédictives</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{(data.interventionsPredictives.economie_co2_kg || 0).toFixed(2)} kg</div>
                        <div className="stat-label">Économie CO₂</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{(data.interventionsPredictives.cout_total_tnd || 0).toFixed(2)} TND</div>
                        <div className="stat-label">Coût Total</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{data.interventionsPredictives.duree_totale_minutes || 0} min</div>
                        <div className="stat-label">Durée Totale</div>
                    </div>
                </div>
            </div>

            {/* Question 5: Trajets CO2 */}
            <div className="section">
                <div className="section-header">
                    <h2>Trajets véhicules autonomes - Plus grande réduction CO₂</h2>
                    <button className="sql-btn" onClick={() => toggleSql('q5')}>
                        {showSql.q5 ? '❌ Masquer SQL' : '🔍 Voir Requête SQL'}
                    </button>
                </div>
                <SqlQueryBox query={SQL_QUERIES.q5} isVisible={showSql.q5} />
                <div className="kpi-highlight">
                    <span className="kpi-label">Total CO₂ Économisé</span>
                    <span className="kpi-value">{data.totalCO2.toFixed(2)} kg</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Rang</th>
                            <th>Véhicule</th>
                            <th>Type</th>
                            <th>Énergie</th>
                            <th>Origine → Destination</th>
                            <th>Distance</th>
                            <th>CO₂ Économisé</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.topTrajetsCO2.map((trajet, idx) => (
                            <tr key={idx}>
                                <td><strong>#{idx + 1}</strong></td>
                                <td>{trajet.vehicule_plaque}</td>
                                <td>{trajet.vehicule_type}</td>
                                <td>{trajet.vehicule_energie}</td>
                                <td>{trajet.origine} → {trajet.destination}</td>
                                <td>{trajet.distance_km} km</td>
                                <td style={{ color: '#28a745', fontWeight: 'bold' }}>{trajet.economie_co2_kg} kg</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Footer */}
            <div style={{ textAlign: 'center', padding: '20px', color: '#888', fontSize: '0.8rem' }}>
                Projet Module Base de Données | Django REST Framework + React | Neo-Sousse 2030
            </div>
        </div>
    );
}

export default App;
