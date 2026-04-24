/**
 * Service API centralisé pour Smart City Neo-Sousse 2030
 * Gère toutes les communications avec le backend Django
 */

import axios from 'axios';

// Configuration de base
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Intercepteur pour gérer les erreurs globalement
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// ============================================
// Services pour les différentes entités
// ============================================

// Arrondissements
export const arrondissementsAPI = {
    getAll: () => api.get('/arrondissements/'),
    getById: (id) => api.get(`/arrondissements/${id}/`),
};

// Capteurs
export const capteursAPI = {
    getAll: (params = {}) => api.get('/capteurs/', { params }),
    getById: (uuid) => api.get(`/capteurs/${uuid}/`),
    getZonesPolluees24h: () => api.get('/capteurs/zones_polluees_24h/'),
    getDisponibiliteParArrondissement: () => api.get('/capteurs/disponibilite_par_arrondissement/'),
    getStatsParType: () => api.get('/capteurs/stats_par_type/'),
};

// Interventions
export const interventionsAPI = {
    getAll: (params = {}) => api.get('/interventions/', { params }),
    getById: (id) => api.get(`/interventions/${id}/`),
    getStatsImpact: () => api.get('/interventions/stats_impact_environnemental/'),
    getInterventionsPredictivesMois: () => api.get('/interventions/interventions_predictives_mois/'),
};

// Citoyens
export const citoyensAPI = {
    getAll: (params = {}) => api.get('/citoyens/', { params }),
    getById: (id) => api.get(`/citoyens/${id}/`),
    getTopEngages: (limit = 10) => api.get('/citoyens/top_engages/', { params: { limit } }),
};

// Véhicules
export const vehiculesAPI = {
    getAll: (params = {}) => api.get('/vehicules/', { params }),
    getById: (id) => api.get(`/vehicules/${id}/`),
};

// Trajets
export const trajetsAPI = {
    getAll: (params = {}) => api.get('/trajets/', { params }),
    getById: (id) => api.get(`/trajets/${id}/`),
    getTopTrajetsCO2: (limit = 20) => api.get('/trajets/top_trajets_co2/', { params: { limit } }),
    getStatsParVehicule: () => api.get('/trajets/stats_par_vehicule/'),
};

// Techniciens
export const techniciensAPI = {
    getAll: (params = {}) => api.get('/techniciens/', { params }),
    getById: (id) => api.get(`/techniciens/${id}/`),
};

// ============================================
// Nouveaux modules académiques
// ============================================

// Compilateur NL → SQL
export const compilerAPI = {
    query: (queryText) => api.post('/compiler/query/', { query: queryText }),
    getExamples: () => api.get('/compiler/query/'),
};

// Automates à États Finis
export const automataAPI = {
    transition: (entityType, entityId, event) => api.post('/automata/transition/', {
        entity_type: entityType,
        entity_id: entityId,
        event: event,
    }),
    getState: (entityType, entityId) => api.get(`/automata/state/${entityType}/${entityId}/`),
    getHistory: (entityType, entityId) => api.get(`/automata/history/${entityType}/${entityId}/`),
    getAlerts: () => api.get('/automata/alerts/'),
    getDefinitions: () => api.get('/automata/definitions/'),
};

// Rapports IA
export const aiReportsAPI = {
    generateReport: (reportType, date) => api.post('/ai/report/', {
        report_type: reportType,
        date: date || '',
    }),
    suggest: (capteurId) => api.post('/ai/suggest/', { capteur_id: capteurId }),
    getHistory: () => api.get('/ai/history/'),
};

export default api;
