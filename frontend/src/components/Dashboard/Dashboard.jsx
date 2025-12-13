/**
 * Dashboard - Composant principal du tableau de bord
 * Affiche les KPIs et métriques de la Smart City
 */

import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts';
import KPICard from './KPICard';
import { capteursAPI, trajetsAPI, interventionsAPI, citoyensAPI } from '../../services/api';
import './Dashboard.css';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const Dashboard = () => {
    const [loading, setLoading] = useState(true);
    const [kpis, setKpis] = useState({
        totalCapteurs: 0,
        tauxDisponibilite: 0,
        totalCO2Economise: 0,
        interventionsTerminees: 0
    });
    const [zonesPolluees, setZonesPolluees] = useState([]);
    const [statsParType, setStatsParType] = useState([]);
    const [topCitoyens, setTopCitoyens] = useState([]);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            // Récupération parallèle des données
            const [disponibilite, pollution, types, trajets, citoyens, interventions] = await Promise.all([
                capteursAPI.getDisponibiliteParArrondissement().catch(() => ({ data: { taux_disponibilite_global: 0 } })),
                capteursAPI.getZonesPolluees24h().catch(() => ({ data: { zones: [] } })),
                capteursAPI.getStatsParType().catch(() => ({ data: [] })),
                trajetsAPI.getTopTrajetsCO2().catch(() => ({ data: { total_economie_co2_kg: 0 } })),
                citoyensAPI.getTopEngages(5).catch(() => ({ data: [] })),
                interventionsAPI.getStatsImpact().catch(() => ({ data: { global: {} } }))
            ]);

            // Calcul du total des capteurs
            const totalCapteurs = disponibilite.data.arrondissements?.reduce(
                (sum, arr) => sum + arr.total_capteurs, 0
            ) || 0;

            setKpis({
                totalCapteurs,
                tauxDisponibilite: disponibilite.data.taux_disponibilite_global || 0,
                totalCO2Economise: trajets.data.total_economie_co2_kg || 0,
                interventionsTerminees: interventions.data.global?.total_interventions || 0
            });

            setZonesPolluees(pollution.data.zones || []);
            setStatsParType(types.data || []);
            setTopCitoyens(citoyens.data || []);

        } catch (error) {
            console.error('Erreur lors du chargement des données:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <header className="header">
                <div>
                    <h1>Tableau de Bord</h1>
                    <p className="header-subtitle">Smart City Neo-Sousse 2030 - Données en temps réel</p>
                </div>
                <div className="header-date">
                    {new Date().toLocaleDateString('fr-FR', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                    })}
                </div>
            </header>

            {/* KPIs Grid */}
            <div className="kpi-grid">
                <KPICard
                    title="Capteurs Actifs"
                    value={kpis.totalCapteurs}
                    change={`${kpis.tauxDisponibilite}% disponibles`}
                    changeType="positive"
                    color="blue"
                    icon="📡"
                />
                <KPICard
                    title="Taux Disponibilité"
                    value={`${kpis.tauxDisponibilite}%`}
                    change="objectif 95%"
                    changeType={kpis.tauxDisponibilite >= 95 ? 'positive' : 'neutral'}
                    color="green"
                    icon="✅"
                />
                <KPICard
                    title="CO2 Économisé"
                    value={`${kpis.totalCO2Economise.toFixed(1)} kg`}
                    change="transport durable"
                    changeType="positive"
                    color="green"
                    icon="🌱"
                />
                <KPICard
                    title="Interventions"
                    value={kpis.interventionsTerminees}
                    change="terminées"
                    changeType="positive"
                    color="orange"
                    icon="🔧"
                />
            </div>

            {/* Charts Grid */}
            <div className="data-grid">
                {/* Capteurs par Type */}
                <div className="card chart-card">
                    <h3 className="card-title">Capteurs par Type</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={statsParType}
                                    dataKey="total"
                                    nameKey="type"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={80}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                >
                                    {statsParType.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Zones Polluées */}
                <div className="card chart-card">
                    <h3 className="card-title">Qualité de l'Air par Zone (24h)</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={zonesPolluees}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#2d2d4a" />
                                <XAxis dataKey="arrondissement_nom" stroke="#94a3b8" fontSize={12} />
                                <YAxis stroke="#94a3b8" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1a1a2e',
                                        border: '1px solid #2d2d4a',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Bar dataKey="pollution_moyenne" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Top Citoyens Engagés */}
            <div className="card">
                <h3 className="card-title">🏆 Top Citoyens Engagés</h3>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Rang</th>
                                <th>Citoyen</th>
                                <th>Score Engagement</th>
                                <th>Mobilité Préférée</th>
                                <th>Consultations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topCitoyens.map((citoyen, index) => (
                                <tr key={citoyen.id}>
                                    <td>
                                        <span className="rank-badge">{index + 1}</span>
                                    </td>
                                    <td>{citoyen.nom_complet}</td>
                                    <td>
                                        <span className="score-bar">
                                            <span
                                                className="score-fill"
                                                style={{ width: `${citoyen.score_engagement}%` }}
                                            ></span>
                                            <span className="score-text">{citoyen.score_engagement}</span>
                                        </span>
                                    </td>
                                    <td>
                                        <span className="badge info">{citoyen.preference_mobilite}</span>
                                    </td>
                                    <td>{citoyen.nombre_consultations}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
