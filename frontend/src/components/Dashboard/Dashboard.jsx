/**
 * Dashboard principal - Style Neo-Sousse / Donezo
 */

import React, { useState, useEffect } from 'react';
import { 
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts';
import { capteursAPI, interventionsAPI, trajetsAPI, citoyensAPI } from '../../services/api';
import KPICard from './KPICard';
import './Dashboard.css';

const Dashboard = () => {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState({
        kpis: {},
        interventionsNature: [],
        zonesPolluees: [],
        topCitoyens: []
    });

    const COLORS = ['#16a34a', '#3b82f6', '#f59e0b', '#8b5cf6'];

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [
                    capteursRes,
                    interventionsRes,
                    trajetsRes,
                    zonesRes,
                    citoyensRes
                ] = await Promise.all([
                    capteursAPI.getStatsParType(),
                    interventionsAPI.getAll(),
                    trajetsAPI.getAll(),
                    capteursAPI.getZonesPolluees24h(),
                    citoyensAPI.getTopEngages(5)
                ]);

                // Calcul KPIs
                const capteurs = capteursRes.data || [];
                const totalCapteurs = capteurs.reduce((sum, c) => sum + c.total, 0);
                const hsCapteurs = capteurs.reduce((sum, c) => sum + c.hors_service, 0);

                const intervs = interventionsRes.data.results || [];
                const terminees = intervs.filter(i => i.statut === 'TERMINEE').length;

                // Préparer les données pour les graphiques
                const intervsParNatureMap = intervs.reduce((acc, curr) => {
                    acc[curr.nature] = (acc[curr.nature] || 0) + 1;
                    return acc;
                }, {});

                const interventionsNature = Object.keys(intervsParNatureMap).map(key => ({
                    name: key,
                    valeur: intervsParNatureMap[key]
                }));

                setData({
                    kpis: {
                        totalCapteurs,
                        hsCapteurs,
                        interventionsTerminees: terminees,
                        totalTrajets: trajetsRes.data.count || 0
                    },
                    interventionsNature,
                    zonesPolluees: zonesRes.data || [],
                    topCitoyens: citoyensRes.data || []
                });
            } catch (err) {
                console.error("Erreur chargement dashboard:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="spinner"></div>
                <h2>Chargement du Dashboard...</h2>
            </div>
        );
    }

    // Préparation des données pour le diagramme circulaire (État Capteurs)
    const pieData = [
        { name: 'Actifs', value: data.kpis.totalCapteurs - data.kpis.hsCapteurs },
        { name: 'Hors Service', value: data.kpis.hsCapteurs }
    ];
    const pieColors = ['#16a34a', '#ef4444'];
    const activePercentage = data.kpis.totalCapteurs > 0 
        ? Math.round(((data.kpis.totalCapteurs - data.kpis.hsCapteurs) / data.kpis.totalCapteurs) * 100) 
        : 0;

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <div>
                    <h1>Vue d'ensemble</h1>
                    <p>Supervision de la Smart City Neo-Sousse</p>
                </div>
                <div className="dashboard-actions">
                    <button className="btn btn-outline">Filtrer</button>
                    <button className="btn btn-primary">Générer Rapport</button>
                </div>
            </div>

            {/* Rangée de KPIs */}
            <div className="kpi-grid">
                <KPICard 
                    title="Total Capteurs" 
                    value={data.kpis.totalCapteurs} 
                    change="+12%" 
                    changeType="positive"
                    icon="📡" 
                />
                <KPICard 
                    title="Interventions Terminées" 
                    value={data.kpis.interventionsTerminees} 
                    change="+5%" 
                    changeType="positive"
                    icon="🔧" 
                />
                <KPICard 
                    title="Trajets Écologiques" 
                    value={data.kpis.totalTrajets} 
                    change="-2%" 
                    changeType="negative"
                    icon="🚌" 
                />
                <KPICard 
                    title="Alertes Critiques (HS)" 
                    value={data.kpis.hsCapteurs} 
                    change="0%" 
                    changeType="neutral"
                    icon="🚨" 
                />
            </div>

            <div className="dashboard-main-grid">
                {/* Colonne de gauche (Graphiques) */}
                <div className="dashboard-charts">
                    <div className="card chart-card">
                        <div className="card-header-flex">
                            <h3 className="card-title">Interventions par Nature</h3>
                        </div>
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={data.interventionsNature} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                    <YAxis axisLine={false} tickLine={false} />
                                    <Tooltip cursor={{fill: '#f8fafc'}} />
                                    <Bar dataKey="valeur" fill="#16a34a" radius={[4, 4, 0, 0]} barSize={40} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="card chart-card">
                        <div className="card-header-flex">
                            <h3 className="card-title">Zones les plus Polluées (24h)</h3>
                        </div>
                        <div className="chart-container">
                            {data.zonesPolluees.length > 0 ? (
                                <ResponsiveContainer width="100%" height={300}>
                                    <LineChart data={data.zonesPolluees} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                        <XAxis dataKey="nom" axisLine={false} tickLine={false} />
                                        <YAxis axisLine={false} tickLine={false} />
                                        <Tooltip />
                                        <Line type="monotone" dataKey="pollution_moyenne" stroke="#3b82f6" strokeWidth={3} dot={{r: 4}} activeDot={{r: 6}} />
                                    </LineChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="no-data">Données insuffisantes pour l'analyse</div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Colonne de droite (Listes et Progrès) */}
                <div className="dashboard-sidebar">
                    {/* Donut Chart Style */}
                    <div className="card progress-card">
                        <h3 className="card-title">Disponibilité du Parc</h3>
                        <div className="donut-container">
                            <ResponsiveContainer width="100%" height={200}>
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                        stroke="none"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="donut-center-text">
                                <span className="donut-percent">{activePercentage}%</span>
                                <span className="donut-label">Actifs</span>
                            </div>
                        </div>
                        <div className="progress-legend">
                            {pieData.map((entry, index) => (
                                <div className="legend-item" key={index}>
                                    <span className="legend-dot" style={{backgroundColor: pieColors[index]}}></span>
                                    <span className="legend-name">{entry.name}</span>
                                    <span className="legend-value">{entry.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Liste des Citoyens */}
                    <div className="card list-card">
                        <div className="card-header-flex">
                            <h3 className="card-title">Top Citoyens Engagés</h3>
                            <button className="btn-link">Voir tout</button>
                        </div>
                        <div className="citoyens-list">
                            {data.topCitoyens.map((citoyen, idx) => {
                                const initials = citoyen.nom_complet ? citoyen.nom_complet.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'U';
                                return (
                                <div className="citoyen-item" key={citoyen.id}>
                                    <div className="citoyen-avatar">
                                        {initials}
                                    </div>
                                    <div className="citoyen-info">
                                        <div className="citoyen-name">{citoyen.nom_complet}</div>
                                        <div className="citoyen-score">Score: {citoyen.score_engagement}</div>
                                    </div>
                                    <div className="citoyen-rank">#{idx + 1}</div>
                                </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
