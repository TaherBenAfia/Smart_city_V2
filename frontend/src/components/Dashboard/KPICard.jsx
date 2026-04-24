/**
 * KPICard - Composant réutilisable pour afficher les KPIs (Style Donezo)
 */

import React from 'react';
import './KPICard.css';

const KPICard = ({ title, value, change, changeType, icon }) => {
    return (
        <div className="kpi-card card">
            <div className="kpi-header">
                <span className="kpi-title">{title}</span>
                {icon && <span className="kpi-icon">{icon}</span>}
            </div>
            <div className="kpi-body">
                <div className="kpi-value">{value}</div>
                {change !== undefined && (
                    <div className={`kpi-change ${changeType || 'neutral'}`}>
                        <span className="change-arrow">
                            {changeType === 'positive' ? '↗' : changeType === 'negative' ? '↘' : '→'}
                        </span>
                        <span>{change} vs mois dernier</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default KPICard;
