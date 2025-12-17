import React, { useState, useEffect } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts';
import { capteursAPI, trajetsAPI, interventionsAPI, citoyensAPI } from '../../services/api';
import './BusinessQuestions.css';

const COLORS = ['#2563eb', '#16a34a', '#d97706', '#dc2626', '#7c3aed'];

const BusinessQuestions = () => {
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState({
        pollution: [],
        disponibilite: { arrondissements: [] },
        types: [],
        citoyens: [],
        interventions: { statistiques: {} },
        impact: {},
        trajets: [],
        vehiculesStats: [],
        co2: 0
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [poll, disp, types, cit, interv, impact, traj, vStats] = await Promise.all([
                    capteursAPI.getZonesPolluees24h(),
                    capteursAPI.getDisponibiliteParArrondissement(),
                    capteursAPI.getStatsParType(),
                    citoyensAPI.getTopEngages(5),
                    interventionsAPI.getInterventionsPredictivesMois(),
                    interventionsAPI.getStatsImpact(),
                    trajetsAPI.getTopTrajetsCO2(5),
                    trajetsAPI.getStatsParVehicule()
                ]);

                setData({
                    pollution: poll.data.zones || [],
                    disponibilite: disp.data || { arrondissements: [] },
                    types: types.data || [],
                    citoyens: cit.data || [],
                    interventions: interv.data || { statistiques: { nombre_interventions: 0, economie_co2_kg: 0 } },
                    impact: impact.data?.global || {},
                    trajets: traj.data.top_trajets || [],
                    vehiculesStats: vStats.data || [],
                    co2: traj.data.total_economie_co2_kg || 0
                });
            } catch (err) {
                console.error("Error loading specific answers", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div className="loading">Chargement des réponses...</div>;

    return (
        <div className="questions-page">
            <header className="page-header">
                <h1>Questions Types Métiers</h1>
                <p>Analyse des données en temps réel </p>
            </header>

            {/* Q1: Pollution */}
            <section className="question-section">
                <h2>Les zones les plus polluées (24h) </h2>
                <div className="answer-block">
                    <div className="chart-box">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data.pollution} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis dataKey="arrondissement_nom" type="category" width={150} />
                                <Tooltip />
                                <Bar dataKey="pollution_moyenne" fill="#ef4444" name="Indice Pollution" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </section>

            {/* Q2: Disponibilité */}
            <section className="question-section">
                <h2>Le taux de disponibilité des capteurs </h2>
                <div className="answer-block">
                    <div className="chart-box">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={data.disponibilite.arrondissements}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="arrondissement_nom" />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Bar dataKey="taux_disponibilite" fill="#10b981" name="Taux Disponibilité (%)" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </section>

            {/* Q3: Citoyens */}
            <section className="question-section">
                <h2>Les citoyens les plus engagés </h2>
                <div className="answer-block">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Rang</th>
                                <th>Nom</th>
                                <th>Score (0-100)</th>
                                <th>Mobilité</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.citoyens.map((c, i) => (
                                <tr key={c.id}>
                                    <td>#{i + 1}</td>
                                    <td>{c.nom_complet}</td>
                                    <td>{c.score_engagement}</td>
                                    <td>{c.preference_mobilite}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            {/* Q4: Interventions Prédictives */}
            <section className="question-section">
                <h2>Bilan des Interventions Prédictives (Ce mois)</h2>
                <div className="answer-block kpi-answer">
                    <div className="mini-kpi">
                        <span className="label">Nombre d'interventions</span>
                        <span className="value">{data.interventions?.statistiques?.nombre_interventions || 0}</span>
                    </div>
                    <div className="mini-kpi">
                        <span className="label">Économie Générée</span>
                        <span className="value">{data.interventions?.statistiques?.economie_co2_kg || 0} kg</span>
                    </div>
                </div>
            </section>

            {/* Q5: Trajets de Véhicules Autonomes */}
            <section className="question-section">
                <h2>Trajets de véhicules autonomes ont le plus réduit le CO2 </h2>
                <div className="answer-block">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Véhicule</th>
                                <th>Origine → Destination</th>
                                <th>Distance</th>
                                <th>Économie CO2</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.trajets.map((t) => (
                                <tr key={t.id}>
                                    <td>{t.vehicule_plaque}</td>
                                    <td>{t.origine} → {t.destination}</td>
                                    <td>{t.distance_km} km</td>
                                    <td style={{ color: '#16a34a', fontWeight: 'bold' }}>{t.economie_co2_kg.toFixed(2)} kg</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    );
};

export default BusinessQuestions;
