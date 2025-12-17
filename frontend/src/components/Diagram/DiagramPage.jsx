import React from 'react';

const DiagramPage = () => {
    return (
        <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: '2rem', textAlign: 'center', color: '#1e293b' }}>
                Modèle Entité-Association (E/A)
            </h1>

            <div style={{ marginBottom: '4rem' }}>
                <h2 style={{ marginBottom: '1rem', borderLeft: '4px solid #3b82f6', paddingLeft: '1rem' }}>
                    Vue Globale
                </h2>
                <div style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '1rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    background: 'white'
                }}>
                    <img
                        src="/assets/1.png"
                        alt="Diagramme Entité Association Global"
                        style={{ width: '100%', height: 'auto', display: 'block' }}
                    />
                </div>
            </div>

            <div>
                <h2 style={{ marginBottom: '1rem', borderLeft: '4px solid #10b981', paddingLeft: '1rem' }}>
                    Détail des Relations
                </h2>
                <div style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '1rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    background: 'white'
                }}>
                    <img
                        src="/assets/2.png"
                        alt="Détails Relations"
                        style={{ width: '100%', height: 'auto', display: 'block' }}
                    />
                </div>
            </div>
        </div>
    );
};

export default DiagramPage;
