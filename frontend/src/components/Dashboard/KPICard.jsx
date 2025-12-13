/**
 * KPICard - Composant réutilisable pour afficher les KPIs
 */

import React from 'react';
import './KPICard.css';

const KPICard = ({ title, value, change, changeType, icon, color }) => {
    return (
        <div className={`kpi-card card ${color ? `kpi-${color}` : ''}`}>
            <div className="card-header">
                <span className="card-title">{title}</span>
                {icon && <span className="kpi-icon">{icon}</span>}
            </div>
            <div className="kpi-value">{value}</div>
            {change !== undefined && (
                <span className={`kpi-change ${changeType || 'positive'}`}>
                    {changeType === 'positive' ? '↑' : changeType === 'negative' ? '↓' : '→'} {change}
                </span>
            )}
        </div>
    );
};

export default KPICard;
