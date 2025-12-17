
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { capteursAPI, trajetsAPI, vehiculesAPI } from '../../services/api';

// Fix for default Leaflet icons in Webpack/React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom Icons
// Custom Icons using Emojis for zero-dependency visual distinction
const sensorIcon = new L.divIcon({
    html: '<div style="font-size: 24px; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">📡</div>',
    className: 'custom-sensor-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
});

const vehicleIcon = new L.divIcon({
    html: '<div style="font-size: 24px; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🚗</div>',
    className: 'custom-vehicle-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
});

const MapPage = () => {
    const [capteurs, setCapteurs] = useState([]);
    const [vehicules, setVehicules] = useState([]);
    const [loading, setLoading] = useState(true);

    const [pollutionZones, setPollutionZones] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch basic data
                const caps = await capteursAPI.getAll({ limit: 100 });
                const vehi = await vehiculesAPI.getAll();
                const traj = await trajetsAPI.getAll({ limit: 50 }); // Latest trips
                const poll = await capteursAPI.getZonesPolluees24h(); // Q1 Answer

                setCapteurs(caps.data.results || caps.data);

                // Map Pollution Data to Coordinates
                const zoneCoords = {
                    "Medina": { lat: 35.8256, lng: 10.6367 },
                    "Sahloul": { lat: 35.8450, lng: 10.5900 },
                    "Khezama": { lat: 35.8400, lng: 10.6100 },
                    "Hammam Sousse": { lat: 35.8600, lng: 10.6000 },
                    "Sidi Abdelhamid": { lat: 35.8000, lng: 10.6400 },
                    "Centre Ville": { lat: 35.8200, lng: 10.6400 }
                };

                const pZones = (poll.data.zones || []).map(z => ({
                    ...z,
                    coords: zoneCoords[z.arrondissement_nom] || zoneCoords["Centre Ville"]
                }));
                setPollutionZones(pZones);


                const mappedVehicles = (vehi.data.results || vehi.data).map(v => {
                    // Try to find last trip for this vehicle
                    const lastTrip = (traj.data.results || traj.data).find(t => t.vehicule === v.id);
                    const locationName = lastTrip ? lastTrip.destination : "Centre Ville";
                    const baseCoords = zoneCoords[locationName] || zoneCoords["Centre Ville"];

                    // Add slight random jitter to separate markers
                    return {
                        ...v,
                        lat: baseCoords.lat + (Math.random() - 0.5) * 0.01,
                        lng: baseCoords.lng + (Math.random() - 0.5) * 0.01,
                        lastLocation: locationName
                    };
                });

                setVehicules(mappedVehicles);

            } catch (err) {
                console.error("Map Data Error", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div style={{ padding: '2rem' }}>Chargement de la carte...</div>;

    return (
        <div style={{ height: 'calc(100vh - 64px)', width: '100%', position: 'relative' }}>
            <MapContainer center={[35.8256, 10.6200]} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />

                {/* Capteurs Markers */}
                {capteurs.map(c => (
                    c.latitude && c.longitude ? (
                        <Marker
                            key={c.uuid}
                            position={[c.latitude, c.longitude]}
                            icon={sensorIcon}
                        >
                            <Popup>
                                <strong>Capteur {c.type}</strong><br />
                                Statut: {c.statut}<br />
                                Installé le: {c.date_install}
                            </Popup>
                        </Marker>
                    ) : null
                ))}

                {/* Pollution Zones Overlay (Q1) */}
                {pollutionZones.map((z, idx) => (
                    <Circle
                        key={`zone-${idx}`}
                        center={[z.coords.lat, z.coords.lng]}
                        radius={800}
                        pathOptions={{
                            color: z.pollution_moyenne > 100 ? 'red' : 'orange',
                            fillColor: z.pollution_moyenne > 100 ? 'red' : 'orange',
                            fillOpacity: 0.2
                        }}
                    >
                        <Popup>
                            <strong>Zone: {z.arrondissement_nom}</strong><br />
                            Pollution Moyenne: {z.pollution_moyenne} (AQI)<br />
                            Niveau: {z.niveau}
                        </Popup>
                    </Circle>
                ))}

                {/* Véhicules Markers */}
                {vehicules.map(v => (
                    <Marker
                        key={v.id}
                        position={[v.lat, v.lng]}
                        icon={vehicleIcon}
                    >
                        <Popup>
                            <strong>Véhicule {v.plaque}</strong><br />
                            Type: {v.type} ({v.energie})<br />
                            Dernière Zone: {v.lastLocation}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {/* Legend Overlay */}
            <div style={{
                position: 'absolute', bottom: '20px', left: '20px', zIndex: 1000,
                background: 'white', padding: '10px', borderRadius: '5px', boxShadow: '0 0 10px rgba(0,0,0,0.2)'
            }}>
                <h4 style={{ margin: '0 0 10px 0' }}>Légende</h4>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                    <span style={{ fontSize: '20px', marginRight: '8px' }}>📡</span>
                    <span>Capteurs IoT</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span style={{ fontSize: '20px', marginRight: '8px' }}>🚗</span>
                    <span>Véhicules (Simulés)</span>
                </div>
            </div>
        </div>
    );
};

export default MapPage;
