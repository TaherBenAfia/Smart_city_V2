-- ============================================================================
-- SMART CITY ANALYTICS PLATFORM - Neo-Sousse 2030
-- Script DDL - Création de la base de données
-- ============================================================================

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS smart_city_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_city_db;

-- ============================================================================
-- TABLE: arrondissement
-- Description: Zones géographiques de la métropole
-- ============================================================================
CREATE TABLE arrondissement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    code_postal VARCHAR(10) NOT NULL,
    superficie_km2 DECIMAL(10, 2),
    population INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_arrondissement_code (code_postal)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: proprietaire
-- Description: Propriétaires des capteurs (Municipalité ou Partenaires Privés)
-- ============================================================================
CREATE TABLE proprietaire (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    type ENUM('MUNICIPALITE', 'PRIVE') NOT NULL,
    contact_email VARCHAR(255),
    contact_telephone VARCHAR(20),
    adresse TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_proprietaire_type (type)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: capteur
-- Description: Capteurs IoT déployés dans la ville
-- ============================================================================
CREATE TABLE capteur (
    uuid CHAR(36) PRIMARY KEY,
    type ENUM('AIR', 'TRAFIC', 'ENERGIE', 'DECHETS', 'ECLAIRAGE') NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    statut ENUM('ACTIF', 'MAINTENANCE', 'HORS_SERVICE') NOT NULL DEFAULT 'ACTIF',
    date_installation DATE NOT NULL,
    description TEXT,
    proprietaire_id INT NOT NULL,
    arrondissement_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_capteur_type (type),
    INDEX idx_capteur_statut (statut),
    INDEX idx_capteur_arrondissement (arrondissement_id),
    INDEX idx_capteur_localisation (latitude, longitude),
    
    CONSTRAINT fk_capteur_proprietaire 
        FOREIGN KEY (proprietaire_id) REFERENCES proprietaire(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_capteur_arrondissement 
        FOREIGN KEY (arrondissement_id) REFERENCES arrondissement(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: mesure
-- Description: Mesures collectées par les capteurs
-- ============================================================================
CREATE TABLE mesure (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    capteur_uuid CHAR(36) NOT NULL,
    timestamp DATETIME NOT NULL,
    valeurs JSON NOT NULL COMMENT 'Valeurs des mesures selon le type de capteur',
    indice_pollution DECIMAL(5, 2) COMMENT 'Indice de pollution (0-500)',
    qualite_air ENUM('BON', 'MODERE', 'MAUVAIS', 'TRES_MAUVAIS', 'DANGEREUX'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_mesure_capteur (capteur_uuid),
    INDEX idx_mesure_timestamp (timestamp),
    INDEX idx_mesure_pollution (indice_pollution),
    
    CONSTRAINT fk_mesure_capteur 
        FOREIGN KEY (capteur_uuid) REFERENCES capteur(uuid)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: technicien
-- Description: Techniciens de maintenance
-- ============================================================================
CREATE TABLE technicien (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricule VARCHAR(20) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    telephone VARCHAR(20),
    specialite VARCHAR(100),
    type_validation ENUM('IA', 'HUMAIN') NOT NULL DEFAULT 'HUMAIN',
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_technicien_matricule (matricule),
    INDEX idx_technicien_specialite (specialite)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: intervention
-- Description: Interventions de maintenance sur les capteurs
-- Contrainte métier: Nécessite 2 techniciens (intervenant + validateur)
-- ============================================================================
CREATE TABLE intervention (
    id INT AUTO_INCREMENT PRIMARY KEY,
    capteur_uuid CHAR(36) NOT NULL,
    date_heure DATETIME NOT NULL,
    nature ENUM('PREDICTIVE', 'CORRECTIVE', 'CURATIVE') NOT NULL,
    description TEXT,
    duree_minutes INT NOT NULL,
    cout DECIMAL(10, 2) NOT NULL DEFAULT 0,
    reduction_co2 DECIMAL(10, 4) COMMENT 'Réduction CO2 en kg',
    statut ENUM('PLANIFIEE', 'EN_COURS', 'TERMINEE', 'ANNULEE') DEFAULT 'PLANIFIEE',
    
    -- Contrainte: 2 techniciens obligatoires
    technicien_intervenant_id INT NOT NULL COMMENT 'Technicien qui effectue intervention',
    technicien_validateur_id INT NOT NULL COMMENT 'Technicien qui valide (IA ou Humain)',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_intervention_capteur (capteur_uuid),
    INDEX idx_intervention_date (date_heure),
    INDEX idx_intervention_nature (nature),
    INDEX idx_intervention_statut (statut),
    
    CONSTRAINT fk_intervention_capteur 
        FOREIGN KEY (capteur_uuid) REFERENCES capteur(uuid)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_intervention_intervenant 
        FOREIGN KEY (technicien_intervenant_id) REFERENCES technicien(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_intervention_validateur 
        FOREIGN KEY (technicien_validateur_id) REFERENCES technicien(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Contrainte: L'intervenant et le validateur doivent être différents
    CONSTRAINT chk_techniciens_differents 
        CHECK (technicien_intervenant_id != technicien_validateur_id)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: citoyen
-- Description: Citoyens engagés dans la démarche écologique
-- ============================================================================
CREATE TABLE citoyen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identifiant_unique VARCHAR(50) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    date_naissance DATE,
    adresse TEXT,
    score_engagement DECIMAL(5, 2) DEFAULT 0 COMMENT 'Score écologique (0-100)',
    preference_mobilite ENUM('VELO', 'TRANSPORT_COMMUN', 'COVOITURAGE', 'MARCHE', 'VEHICULE_ELECTRIQUE') DEFAULT 'TRANSPORT_COMMUN',
    notifications_actives BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_citoyen_identifiant (identifiant_unique),
    UNIQUE KEY uk_citoyen_email (email),
    INDEX idx_citoyen_score (score_engagement)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: consultation
-- Description: Historique des consultations de données par les citoyens
-- ============================================================================
CREATE TABLE consultation (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    citoyen_id INT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type_donnee VARCHAR(50) NOT NULL COMMENT 'Type de donnée consultée',
    zone_consultee VARCHAR(100) COMMENT 'Zone géographique consultée',
    duree_consultation_secondes INT,
    source_consultation ENUM('WEB', 'MOBILE', 'API') DEFAULT 'WEB',
    
    INDEX idx_consultation_citoyen (citoyen_id),
    INDEX idx_consultation_timestamp (timestamp),
    INDEX idx_consultation_type (type_donnee),
    
    CONSTRAINT fk_consultation_citoyen 
        FOREIGN KEY (citoyen_id) REFERENCES citoyen(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: vehicule
-- Description: Véhicules autonomes municipaux
-- ============================================================================
CREATE TABLE vehicule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plaque VARCHAR(20) NOT NULL,
    type ENUM('BUS', 'NAVETTE', 'UTILITAIRE', 'COLLECTE_DECHETS') NOT NULL,
    energie ENUM('ELECTRIQUE', 'HYDROGENE', 'HYBRIDE') NOT NULL,
    marque VARCHAR(100),
    modele VARCHAR(100),
    annee_mise_service INT,
    capacite_passagers INT,
    autonomie_km DECIMAL(10, 2),
    statut ENUM('EN_SERVICE', 'MAINTENANCE', 'HORS_SERVICE') DEFAULT 'EN_SERVICE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_vehicule_plaque (plaque),
    INDEX idx_vehicule_type (type),
    INDEX idx_vehicule_energie (energie),
    INDEX idx_vehicule_statut (statut)
) ENGINE=InnoDB;

-- ============================================================================
-- TABLE: trajet
-- Description: Trajets effectués par les véhicules autonomes
-- ============================================================================
CREATE TABLE trajet (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vehicule_id INT NOT NULL,
    origine VARCHAR(255) NOT NULL,
    origine_latitude DECIMAL(10, 8),
    origine_longitude DECIMAL(11, 8),
    destination VARCHAR(255) NOT NULL,
    destination_latitude DECIMAL(10, 8),
    destination_longitude DECIMAL(11, 8),
    depart DATETIME NOT NULL,
    arrivee DATETIME,
    distance_km DECIMAL(10, 2),
    economie_co2 DECIMAL(10, 4) COMMENT 'Économie CO2 en kg vs véhicule thermique',
    nombre_passagers INT DEFAULT 0,
    statut ENUM('EN_COURS', 'TERMINE', 'ANNULE') DEFAULT 'EN_COURS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_trajet_vehicule (vehicule_id),
    INDEX idx_trajet_dates (depart, arrivee),
    INDEX idx_trajet_economie (economie_co2),
    
    CONSTRAINT fk_trajet_vehicule 
        FOREIGN KEY (vehicule_id) REFERENCES vehicule(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- VUES UTILITAIRES
-- ============================================================================

-- Vue: Statistiques capteurs par arrondissement
CREATE OR REPLACE VIEW v_stats_capteurs_arrondissement AS
SELECT 
    a.id AS arrondissement_id,
    a.nom AS arrondissement_nom,
    c.type AS type_capteur,
    COUNT(*) AS total_capteurs,
    SUM(CASE WHEN c.statut = 'ACTIF' THEN 1 ELSE 0 END) AS capteurs_actifs,
    SUM(CASE WHEN c.statut = 'MAINTENANCE' THEN 1 ELSE 0 END) AS capteurs_maintenance,
    SUM(CASE WHEN c.statut = 'HORS_SERVICE' THEN 1 ELSE 0 END) AS capteurs_hors_service,
    ROUND(SUM(CASE WHEN c.statut = 'ACTIF' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS taux_disponibilite
FROM arrondissement a
LEFT JOIN capteur c ON a.id = c.arrondissement_id
GROUP BY a.id, a.nom, c.type;

-- Vue: Top citoyens engagés
CREATE OR REPLACE VIEW v_top_citoyens_engages AS
SELECT 
    c.id,
    c.identifiant_unique,
    CONCAT(c.prenom, ' ', c.nom) AS nom_complet,
    c.score_engagement,
    c.preference_mobilite,
    COUNT(co.id) AS nombre_consultations
FROM citoyen c
LEFT JOIN consultation co ON c.id = co.citoyen_id
GROUP BY c.id
ORDER BY c.score_engagement DESC;

-- Vue: Économies CO2 par véhicule
CREATE OR REPLACE VIEW v_economies_co2_vehicules AS
SELECT 
    v.id AS vehicule_id,
    v.plaque,
    v.type,
    v.energie,
    COUNT(t.id) AS nombre_trajets,
    SUM(t.distance_km) AS total_distance_km,
    SUM(t.economie_co2) AS total_economie_co2,
    AVG(t.economie_co2) AS moyenne_economie_co2_par_trajet
FROM vehicule v
LEFT JOIN trajet t ON v.id = t.vehicule_id AND t.statut = 'TERMINE'
GROUP BY v.id;

-- ============================================================================
-- FIN DU SCRIPT DDL
-- ============================================================================
