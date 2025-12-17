
import React, { useState } from 'react';
import axios from 'axios';
import './SQLBuilder.css';

const API_URL = 'http://localhost:8000/api/sql/execute/';

// Mock Tables Schema
const DB_SCHEMA = {
    tables: [
        'arrondissement', 'capteur', 'citoyen', 'consultation',
        'intervention', 'mesure', 'proprietaire', 'technicien',
        'trajet', 'vehicule'
    ],
    columns: {
        'arrondissement': ['id', 'nom', 'code_postal', 'population', 'superficie_km2'],
        'capteur': ['uuid', 'type', 'statut', 'arrondissement_id', 'proprietaire_id'],
        'mesure': ['id', 'capteur_id', 'timestamp', 'valeurs', 'indice_pollution', 'qualite_air'],
        'intervention': ['id', 'capteur_id', 'date_heure', 'nature', 'statut', 'cout', 'reduction_co2'],
        'citoyen': ['id', 'nom', 'prenom', 'score_engagement', 'preference_mobilite'],
        'vehicule': ['id', 'plaque', 'type', 'energie', 'statut'],
        'trajet': ['id', 'vehicule_id', 'origine', 'destination', 'economie_co2', 'statut']
    }
};

const PRE_DEFINED_QUERIES = [
    {
        label: "Q1: Zones Polluées (24h)",
        sql: `SELECT a.nom, AVG(m.indice_pollution) as pollution, COUNT(*) as mesures 
FROM arrondissement a 
JOIN capteur c ON a.id = c.arrondissement_id 
JOIN mesure m ON c.uuid = m.capteur_id 
WHERE c.type = 'AIR' AND m.timestamp >= NOW() - INTERVAL 24 HOUR 
GROUP BY a.nom 
ORDER BY pollution DESC`
    },
    {
        label: "Q2: Disponibilité Capteurs",
        sql: `SELECT a.nom, COUNT(*) as total, SUM(CASE WHEN c.statut='ACTIF' THEN 1 ELSE 0 END) as actifs 
FROM arrondissement a 
JOIN capteur c ON a.id = c.arrondissement_id 
GROUP BY a.nom`
    },
    {
        label: "Q3: Citoyens Engagés",
        sql: `SELECT nom, prenom, score_engagement FROM citoyen ORDER BY score_engagement DESC LIMIT 10`
    },
    {
        label: "Q4: Interventions Prédictives",
        sql: `SELECT COUNT(*) as nb, SUM(reduction_co2) as eco_co2, SUM(cout) as cout_total 
FROM intervention 
WHERE nature='PREDICTIVE' AND statut='TERMINEE'`
    },
    {
        label: "Q5: Top Trajets CO2",
        sql: `SELECT v.plaque, t.origine, t.destination, t.economie_co2 
FROM trajet t 
JOIN vehicule v ON t.vehicule_id = v.id 
WHERE t.statut='TERMINE' 
ORDER BY t.economie_co2 DESC LIMIT 10`
    }
];

const SQLBuilder = () => {
    // Builder State
    const [selectColumns, setSelectColumns] = useState([{ col: '*', alias: '', agg: '' }]);
    const [fromTable, setFromTable] = useState('arrondissement');
    const [joins, setJoins] = useState([]);
    const [wheres, setWheres] = useState([]);
    const [groupBy, setGroupBy] = useState('');
    const [having, setHaving] = useState('');
    const [orderBy, setOrderBy] = useState('');
    const [limit, setLimit] = useState('');

    // Execution State
    const [rawSql, setRawSql] = useState('');
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // --- Builder Actions ---
    const addSelectColumn = () => setSelectColumns([...selectColumns, { col: '', alias: '', agg: '' }]);
    const updateSelect = (idx, field, val) => {
        const newCols = [...selectColumns];
        newCols[idx][field] = val;
        setSelectColumns(newCols);
    };

    const addJoin = () => setJoins([...joins, { type: 'JOIN', table: '', on: '' }]);
    const updateJoin = (idx, field, val) => {
        const newJoins = [...joins];
        newJoins[idx][field] = val;
        setJoins(newJoins);
    };

    const addWhere = () => setWheres([...wheres, { col: '', op: '=', val: '', logic: 'AND' }]);
    const updateWhere = (idx, field, val) => {
        const newWheres = [...wheres];
        newWheres[idx][field] = val;
        setWheres(newWheres);
    };

    // --- SQL Generation ---
    const generateSQL = () => {
        let sql = 'SELECT ';

        // SELECT
        const cols = selectColumns.map(c => {
            let parts = c.col || '*';
            if (c.agg) parts = `${c.agg}(${parts})`;
            if (c.alias) parts += ` AS ${c.alias}`;
            return parts;
        }).join(', ');
        sql += cols;

        // FROM
        sql += `\nFROM ${fromTable}`;

        // JOIN
        joins.forEach(j => {
            if (j.table && j.on) {
                sql += `\n${j.type} ${j.table} ON ${j.on}`;
            }
        });

        // WHERE
        if (wheres.length > 0) {
            const validWheres = wheres.filter(w => w.col && w.val);
            if (validWheres.length > 0) {
                sql += '\nWHERE ';
                sql += validWheres.map((w, i) => {
                    const prefix = i > 0 ? `${w.logic} ` : '';
                    const val = isNaN(w.val) && !w.val.startsWith("'") ? `'${w.val}'` : w.val;
                    return `${prefix}${w.col} ${w.op} ${val}`;
                }).join(' ');
            }
        }

        // GROUP BY
        if (groupBy) sql += `\nGROUP BY ${groupBy}`;

        // HAVING
        if (having) sql += `\nHAVING ${having}`;

        // ORDER BY
        if (orderBy) sql += `\nORDER BY ${orderBy}`;

        // LIMIT
        if (limit) sql += `\nLIMIT ${limit}`;

        setRawSql(sql);
    };

    // --- Execution ---
    const executeQuery = async () => {
        if (!rawSql) return;
        setLoading(true);
        setError(null);
        setResults(null);
        try {
            const res = await axios.post(API_URL, { query: rawSql });
            setResults(res.data);
        } catch (err) {
            setError(err.response?.data?.error || err.message);
        }
        setLoading(false);
    };

    const loadQuickAction = (sql) => {
        setRawSql(sql);
        // executing immediately is optional, let's let user click run
    };

    return (
        <div className="sql-builder-container">
            <div className="sidebar-quick-actions">
                <h3>⚡ Quick Actions</h3>
                {PRE_DEFINED_QUERIES.map((q, i) => (
                    <button key={i} className="quick-btn" onClick={() => loadQuickAction(q.sql)}>
                        {q.label}
                    </button>
                ))}
            </div>

            <div className="main-panel">
                <h2>🛠️ Interactive SQL Builder</h2>

                {/* Visual Builder */}
                <div className="builder-box">
                    <div className="builder-row">
                        <span className="keyword">SELECT</span>
                        <div className="cols-container">
                            {selectColumns.map((c, i) => (
                                <div key={i} className="col-input-group">
                                    <select value={c.agg} onChange={(e) => updateSelect(i, 'agg', e.target.value)}>
                                        <option value="">(Agg)</option>
                                        <option value="COUNT">COUNT</option>
                                        <option value="SUM">SUM</option>
                                        <option value="AVG">AVG</option>
                                        <option value="MAX">MAX</option>
                                        <option value="MIN">MIN</option>
                                    </select>
                                    <input
                                        type="text"
                                        placeholder="Column (*)"
                                        value={c.col}
                                        onChange={(e) => updateSelect(i, 'col', e.target.value)}
                                        list="columns-list"
                                    />
                                    <span className="keyword">AS</span>
                                    <input
                                        type="text"
                                        placeholder="Alias"
                                        value={c.alias}
                                        onChange={(e) => updateSelect(i, 'alias', e.target.value)}
                                    />
                                </div>
                            ))}
                            <button className="add-btn" onClick={addSelectColumn}>+</button>
                        </div>
                    </div>

                    <div className="builder-row">
                        <span className="keyword">FROM</span>
                        <select value={fromTable} onChange={(e) => setFromTable(e.target.value)}>
                            {DB_SCHEMA.tables.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>

                    {/* JOINs */}
                    {joins.map((j, i) => (
                        <div key={i} className="builder-row">
                            <select value={j.type} onChange={(e) => updateJoin(i, 'type', e.target.value)}>
                                <option value="JOIN">JOIN</option>
                                <option value="LEFT JOIN">LEFT JOIN</option>
                                <option value="RIGHT JOIN">RIGHT JOIN</option>
                            </select>
                            <select value={j.table} onChange={(e) => updateJoin(i, 'table', e.target.value)}>
                                <option value="">Select Table...</option>
                                {DB_SCHEMA.tables.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                            <span className="keyword">ON</span>
                            <input
                                type="text"
                                placeholder="t1.id = t2.ref_id"
                                value={j.on}
                                onChange={(e) => updateJoin(i, 'on', e.target.value)}
                            />
                        </div>
                    ))}
                    <div className="builder-row">
                        <button className="add-clause-btn" onClick={addJoin}>+ ADD JOIN</button>
                    </div>

                    {/* WHERE */}
                    {wheres.map((w, i) => (
                        <div key={i} className="builder-row">
                            <span className="keyword">{i === 0 ? 'WHERE' : w.logic}</span>
                            <input
                                type="text"
                                placeholder="Column"
                                value={w.col}
                                onChange={(e) => updateWhere(i, 'col', e.target.value)}
                            />
                            <select value={w.op} onChange={(e) => updateWhere(i, 'op', e.target.value)}>
                                <option value="=">=</option>
                                <option value=">">&gt;</option>
                                <option value="<">&lt;</option>
                                <option value="LIKE">LIKE</option>
                                <option value="IN">IN</option>
                            </select>
                            <input
                                type="text"
                                placeholder="Value"
                                value={w.val}
                                onChange={(e) => updateWhere(i, 'val', e.target.value)}
                            />
                            {i > 0 && (
                                <select value={w.logic} onChange={(e) => updateWhere(i, 'logic', e.target.value)}>
                                    <option value="AND">AND</option>
                                    <option value="OR">OR</option>
                                </select>
                            )}
                        </div>
                    ))}
                    <div className="builder-row">
                        <button className="add-clause-btn" onClick={addWhere}>+ ADD WHERE</button>
                    </div>

                    {/* GROUP BY & HAVING */}
                    <div className="builder-row">
                        <span className="keyword-small">GROUP BY</span>
                        <input type="text" value={groupBy} onChange={(e) => setGroupBy(e.target.value)} placeholder="col1, col2" />
                        <span className="keyword-small">HAVING</span>
                        <input type="text" value={having} onChange={(e) => setHaving(e.target.value)} placeholder="COUNT(*) > 5" />
                    </div>

                    {/* ORDER BY & LIMIT */}
                    <div className="builder-row">
                        <span className="keyword-small">ORDER BY</span>
                        <input type="text" value={orderBy} onChange={(e) => setOrderBy(e.target.value)} placeholder="col DESC" />
                        <span className="keyword-small">LIMIT</span>
                        <input type="number" value={limit} onChange={(e) => setLimit(e.target.value)} placeholder="10" />
                    </div>

                    <button className="generate-btn" onClick={generateSQL}>⬇️ Generate SQL</button>
                </div>

                {/* Editor Area */}
                <div className="sql-editor">
                    <textarea
                        value={rawSql}
                        onChange={(e) => setRawSql(e.target.value)}
                        placeholder="SELECT * FROM ..."
                        rows={6}
                    />
                    <button className="execute-btn" onClick={executeQuery} disabled={loading}>
                        {loading ? 'Running...' : '▶️ RUN QUERY'}
                    </button>
                </div>

                {/* Results Area */}
                {error && <div className="error-box">⚠️ {error}</div>}

                {results && (
                    <div className="results-box">
                        <div className="results-header">
                            <span>✅ Success ({results.row_count} rows)</span>
                        </div>
                        <div className="table-responsive">
                            <table>
                                <thead>
                                    <tr>
                                        {results.columns?.map(col => <th key={col}>{col}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.data?.map((row, i) => (
                                        <tr key={i}>
                                            {results.columns?.map(col => <td key={col}>{row[col]}</td>)}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>

            {/* Datalist for autocomplete */}
            <datalist id="columns-list">
                {DB_SCHEMA.columns[fromTable]?.map(c => <option key={c} value={c} />)}
            </datalist>
        </div>
    );
};

export default SQLBuilder;
