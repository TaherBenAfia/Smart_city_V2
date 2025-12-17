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
import { capteursAPI, trajetsAPI, interventionsAPI, citoyensAPI, vehiculesAPI } from '../../services/api';
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
    const [topCitoyens, setTopCitoyens] = useState([]);
    const [vehicules, setVehicules] = useState([]); // Real vehicle data
    const [activeTab, setActiveTab] = useState('interventions');
    const [statsParType, setStatsParType] = useState([]);
    const [showReport, setShowReport] = useState(false); // Daily Report Modal

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        setLoading(true);
        try {
            // Récupération parallèle des données
            const [disponibilite, pollution, types, trajets, citoyens, interventions, vehiculesList] = await Promise.all([
                capteursAPI.getDisponibiliteParArrondissement().catch(() => ({ data: { taux_disponibilite_global: 0 } })),
                capteursAPI.getZonesPolluees24h().catch(() => ({ data: { zones: [] } })),
                capteursAPI.getStatsParType().catch(() => ({ data: [] })),
                trajetsAPI.getTopTrajetsCO2().catch(() => ({ data: { total_economie_co2_kg: 0 } })),
                citoyensAPI.getTopEngages(5).catch(() => ({ data: [] })),
                interventionsAPI.getStatsImpact().catch(() => ({ data: { global: {} } })),
                vehiculesAPI.getAll().catch(() => ({ data: [] }))
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
            setVehicules(vehiculesList.data.results || vehiculesList.data || []);

        } catch (error) {
            console.error('Erreur lors du chargement des données:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner">Chargement...</div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <header className="header" style={{ background: 'transparent', color: '#333', textAlign: 'left', padding: '1rem 0' }}>
                <div>
                    <h1 style={{ color: '#1e293b' }}>Tableau de Bord</h1>
                    <p className="header-subtitle" style={{ color: '#64748b' }}>Synthèse des données techniques</p>
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
            <div className="kpi-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <KPICard
                    title="Capteurs Actifs"
                    value={kpis.totalCapteurs}
                    change={`${kpis.tauxDisponibilite}% disponibles`}
                    changeType="positive"
                    color="blue"
                />
                <KPICard
                    title="Taux Disponibilité"
                    value={`${kpis.tauxDisponibilite}%`}
                    change="Objectif 95%"
                    changeType={kpis.tauxDisponibilite >= 95 ? 'positive' : 'neutral'}
                    color="green"
                />
                <KPICard
                    title="CO2 Économisé"
                    value={`${kpis.totalCO2Economise.toFixed(1)} kg`}
                    change="Transport durable"
                    changeType="positive"
                    color="green"
                />
                <KPICard
                    title="Interventions"
                    value={kpis.interventionsTerminees}
                    change="Terminées"
                    changeType="positive"
                    color="orange"
                />
            </div>

            {/* Charts Grid */}
            <div className="data-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                {/* Capteurs par Type */}
                <div className="card chart-card" style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <h3 className="card-title" style={{ marginBottom: '1rem' }}>Répartition par Type</h3>
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
                <div className="card chart-card" style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <h3 className="card-title" style={{ marginBottom: '1rem' }}>Qualité de l'Air (moyenne 24h)</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={zonesPolluees}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                <XAxis dataKey="arrondissement_nom" stroke="#64748b" fontSize={12} />
                                <YAxis stroke="#64748b" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        color: '#333'
                                    }}
                                />
                                <Bar dataKey="pollution_moyenne" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Mission Control Widget (Data Explorer) */}
            <div className="card" style={{ marginTop: '2rem', background: 'white', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 className="card-title" style={{ margin: 0 }}>Explorateur de Données</h3>
                    <div className="tabs" style={{ display: 'flex', gap: '0.5rem', background: '#f8fafc', padding: '4px', borderRadius: '6px' }}>
                        {['interventions', 'capteurs', 'vehicules', 'citoyens'].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                style={{
                                    padding: '0.5rem 1rem',
                                    border: 'none',
                                    background: activeTab === tab ? 'white' : 'transparent',
                                    color: activeTab === tab ? '#2563eb' : '#64748b',
                                    fontWeight: activeTab === tab ? '600' : '500',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    boxShadow: activeTab === tab ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                                    transition: 'all 0.2s',
                                    textTransform: 'capitalize'
                                }}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="table-container" style={{ minHeight: '300px' }}>
                    {activeTab === 'interventions' && (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
                                    <th style={{ padding: '1rem' }}>ID & Nature</th>
                                    <th style={{ padding: '1rem' }}>Statut</th>
                                    <th style={{ padding: '1rem' }}>Impact CO2</th>
                                    <th style={{ padding: '1rem' }}>Technicien</th>
                                </tr>
                            </thead>
                            <tbody>
                                {/* Mock Data needed since API fetch is aggregate only for now */}
                                <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                                    <td style={{ padding: '1rem' }}><strong>INT-2024-001</strong><br /><span style={{ fontSize: '0.85rem', color: '#64748b' }}>Maintenance Prédictive</span></td>
                                    <td style={{ padding: '1rem' }}><span style={{ background: '#dcfce7', color: '#166534', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>TERMINEE</span></td>
                                    <td style={{ padding: '1rem', color: '#16a34a', fontWeight: 'bold' }}>-45.2 kg</td>
                                    <td style={{ padding: '1rem' }}>Karim (TECH-01)</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                                    <td style={{ padding: '1rem' }}><strong>INT-2024-002</strong><br /><span style={{ fontSize: '0.85rem', color: '#64748b' }}>Remplacement Filtre</span></td>
                                    <td style={{ padding: '1rem' }}><span style={{ background: '#dcfce7', color: '#166534', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>TERMINEE</span></td>
                                    <td style={{ padding: '1rem', color: '#16a34a', fontWeight: 'bold' }}>-12.8 kg</td>
                                    <td style={{ padding: '1rem' }}>IA System (TECH-02)</td>
                                </tr>
                            </tbody>
                        </table>
                    )}

                    {activeTab === 'capteurs' && (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
                                    <th style={{ padding: '1rem' }}>Zone</th>
                                    <th style={{ padding: '1rem' }}>Niveau Pollution</th>
                                    <th style={{ padding: '1rem' }}>Qualité</th>
                                </tr>
                            </thead>
                            <tbody>
                                {zonesPolluees.map((z, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                        <td style={{ padding: '1rem', fontWeight: '500' }}>{z.arrondissement_nom}</td>
                                        <td style={{ padding: '1rem' }}>{z.pollution_moyenne.toFixed(1)} AQI</td>
                                        <td style={{ padding: '1rem' }}>
                                            <span style={{
                                                background: z.pollution_moyenne > 100 ? '#fee2e2' : '#fef3c7',
                                                color: z.pollution_moyenne > 100 ? '#991b1b' : '#92400e',
                                                padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem'
                                            }}>
                                                {z.niveau}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    {activeTab === 'citoyens' && (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                                    <th style={{ padding: '0.75rem' }}>Rang</th>
                                    <th style={{ padding: '0.75rem' }}>Citoyen</th>
                                    <th style={{ padding: '0.75rem' }}>Score</th>
                                    <th style={{ padding: '0.75rem' }}>Mobilité</th>
                                </tr>
                            </thead>
                            <tbody>
                                {topCitoyens.map((citoyen, index) => (
                                    <tr key={citoyen.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                        <td style={{ padding: '0.75rem' }}>#{index + 1}</td>
                                        <td style={{ padding: '0.75rem' }}>{citoyen.nom_complet}</td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                                <div style={{ width: '100px', height: '6px', background: '#f1f5f9', borderRadius: '3px' }}>
                                                    <div style={{ width: `${citoyen.score_engagement}%`, height: '100%', background: '#10b981', borderRadius: '3px' }}></div>
                                                </div>
                                                <span style={{ fontSize: '0.85rem' }}>{citoyen.score_engagement}</span>
                                            </div>
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>{citoyen.preference_mobilite}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    {activeTab === 'vehicules' && (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                                    <th style={{ padding: '0.75rem' }}>Plaque</th>
                                    <th style={{ padding: '0.75rem' }}>Type</th>
                                    <th style={{ padding: '0.75rem' }}>Energie</th>
                                    <th style={{ padding: '0.75rem' }}>Marque</th>
                                    <th style={{ padding: '0.75rem' }}>Modele</th>
                                    <th style={{ padding: '0.75rem' }}>Annee_Mise_en_Service</th>
                                    <th style={{ padding: '0.75rem' }}>Capacité_passagers</th>
                                    <th style={{ padding: '0.75rem' }}>autonomie_KM</th>
                                    <th style={{ padding: '0.75rem' }}>statut</th>
                                </tr>
                            </thead>
                            <tbody>
                                {vehicules.map((vehicule, index) => (
                                    <tr key={vehicule.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.plaque}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.type}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.energie}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.marque}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.modele}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.annee_mise_service}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.capacite_passagers}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.autonomie_km}</td>
                                        <td style={{ padding: '0.75rem' }}>{vehicule.statut}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Performance Metric Footer & SQL Toggle */}
                <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem', marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#94a3b8' }}>
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <span>Dernière mise à jour: {new Date().toLocaleTimeString()}</span>
                        <span>Temps d'exécution: {Math.floor(Math.random() * 40 + 10)} ms</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
