-- ============================================================================
-- SMART CITY ANALYTICS PLATFORM - Neo-Sousse 2030
-- Script DML - Données de test réalistes
-- ============================================================================

USE smart_city_db;

-- Arrondissements de Neo-Sousse
INSERT INTO arrondissement (nom, code_postal, superficie_km2, population) VALUES
('Centre-Ville', '4000', 8.5, 45000),
('Khezama', '4051', 12.3, 32000),
('Sahloul', '4054', 15.7, 28000),
('Hammam-Sousse', '4011', 18.2, 38000),
('Akouda', '4022', 22.5, 25000);

-- Propriétaires
INSERT INTO proprietaire (nom, type, contact_email, contact_telephone) VALUES
('Municipalité Neo-Sousse', 'MUNICIPALITE', 'contact@neosousse.tn', '+216 73 123 456'),
('TechnoGreen Solutions', 'PRIVE', 'info@technogreen.tn', '+216 73 234 567'),
('EcoSmart Tunisia', 'PRIVE', 'contact@ecosmart.tn', '+216 73 345 678'),
('SmartGrid Africa', 'PRIVE', 'info@smartgrid.africa', '+216 73 456 789');

-- Techniciens (20 techniciens)
INSERT INTO technicien (matricule, nom, prenom, email, specialite, type_validation) VALUES
('TECH001', 'Ben Ali', 'Mohamed', 'mali@neosousse.tn', 'Capteurs Air', 'HUMAIN'),
('TECH002', 'Trabelsi', 'Fatma', 'ftrabelsi@neosousse.tn', 'Trafic', 'HUMAIN'),
('TECH003', 'Gharbi', 'Ahmed', 'agharbi@neosousse.tn', 'Énergie', 'HUMAIN'),
('TECH004', 'Mejri', 'Sonia', 'smejri@neosousse.tn', 'Déchets', 'HUMAIN'),
('TECH005', 'Hamdi', 'Karim', 'khamdi@neosousse.tn', 'Éclairage', 'HUMAIN'),
('TECH006', 'Bouazizi', 'Leila', 'lbouazizi@neosousse.tn', 'Multi-capteurs', 'HUMAIN'),
('TECH007', 'Saidi', 'Omar', 'osaidi@neosousse.tn', 'Capteurs Air', 'HUMAIN'),
('TECH008', 'Nasr', 'Amira', 'anasr@neosousse.tn', 'Trafic', 'HUMAIN'),
('AI-VAL01', 'Système', 'IA-Validator-1', 'ai1@neosousse.tn', 'Validation IA', 'IA'),
('AI-VAL02', 'Système', 'IA-Validator-2', 'ai2@neosousse.tn', 'Validation IA', 'IA');

-- Capteurs (50 capteurs)
INSERT INTO capteur (uuid, type, latitude, longitude, statut, date_installation, proprietaire_id, arrondissement_id) VALUES
-- Capteurs AIR (10)
(UUID(), 'AIR', 35.8256, 10.5967, 'ACTIF', '2024-01-15', 1, 1),
(UUID(), 'AIR', 35.8312, 10.5891, 'ACTIF', '2024-01-20', 1, 1),
(UUID(), 'AIR', 35.8189, 10.6023, 'ACTIF', '2024-02-01', 2, 2),
(UUID(), 'AIR', 35.8401, 10.5834, 'MAINTENANCE', '2024-02-15', 1, 3),
(UUID(), 'AIR', 35.8145, 10.6112, 'ACTIF', '2024-03-01', 2, 4),
(UUID(), 'AIR', 35.8278, 10.5956, 'ACTIF', '2024-03-10', 1, 5),
(UUID(), 'AIR', 35.8334, 10.5878, 'HORS_SERVICE', '2024-03-20', 3, 1),
(UUID(), 'AIR', 35.8223, 10.6001, 'ACTIF', '2024-04-01', 1, 2),
(UUID(), 'AIR', 35.8367, 10.5812, 'ACTIF', '2024-04-15', 2, 3),
(UUID(), 'AIR', 35.8198, 10.6089, 'ACTIF', '2024-05-01', 1, 4),
-- Capteurs TRAFIC (10)
(UUID(), 'TRAFIC', 35.8267, 10.5978, 'ACTIF', '2024-01-10', 1, 1),
(UUID(), 'TRAFIC', 35.8323, 10.5902, 'ACTIF', '2024-01-25', 2, 2),
(UUID(), 'TRAFIC', 35.8200, 10.6034, 'ACTIF', '2024-02-10', 1, 3),
(UUID(), 'TRAFIC', 35.8412, 10.5845, 'ACTIF', '2024-02-28', 3, 4),
(UUID(), 'TRAFIC', 35.8156, 10.6123, 'MAINTENANCE', '2024-03-15', 1, 5),
(UUID(), 'TRAFIC', 35.8289, 10.5967, 'ACTIF', '2024-03-25', 2, 1),
(UUID(), 'TRAFIC', 35.8345, 10.5889, 'ACTIF', '2024-04-05', 1, 2),
(UUID(), 'TRAFIC', 35.8234, 10.6012, 'ACTIF', '2024-04-20', 3, 3),
(UUID(), 'TRAFIC', 35.8378, 10.5823, 'HORS_SERVICE', '2024-05-05', 1, 4),
(UUID(), 'TRAFIC', 35.8209, 10.6100, 'ACTIF', '2024-05-20', 2, 5),
-- Capteurs ENERGIE (10)
(UUID(), 'ENERGIE', 35.8278, 10.5989, 'ACTIF', '2024-01-05', 4, 1),
(UUID(), 'ENERGIE', 35.8334, 10.5913, 'ACTIF', '2024-01-18', 4, 2),
(UUID(), 'ENERGIE', 35.8211, 10.6045, 'ACTIF', '2024-02-05', 4, 3),
(UUID(), 'ENERGIE', 35.8423, 10.5856, 'ACTIF', '2024-02-20', 4, 4),
(UUID(), 'ENERGIE', 35.8167, 10.6134, 'ACTIF', '2024-03-08', 4, 5),
(UUID(), 'ENERGIE', 35.8300, 10.5978, 'MAINTENANCE', '2024-03-28', 4, 1),
(UUID(), 'ENERGIE', 35.8356, 10.5900, 'ACTIF', '2024-04-10', 4, 2),
(UUID(), 'ENERGIE', 35.8245, 10.6023, 'ACTIF', '2024-04-25', 4, 3),
(UUID(), 'ENERGIE', 35.8389, 10.5834, 'ACTIF', '2024-05-10', 4, 4),
(UUID(), 'ENERGIE', 35.8220, 10.6111, 'ACTIF', '2024-05-25', 4, 5),
-- Capteurs DECHETS (10)
(UUID(), 'DECHETS', 35.8289, 10.6000, 'ACTIF', '2024-02-01', 1, 1),
(UUID(), 'DECHETS', 35.8345, 10.5924, 'ACTIF', '2024-02-12', 1, 2),
(UUID(), 'DECHETS', 35.8222, 10.6056, 'ACTIF', '2024-02-25', 2, 3),
(UUID(), 'DECHETS', 35.8434, 10.5867, 'MAINTENANCE', '2024-03-05', 1, 4),
(UUID(), 'DECHETS', 35.8178, 10.6145, 'ACTIF', '2024-03-18', 2, 5),
(UUID(), 'DECHETS', 35.8311, 10.5989, 'ACTIF', '2024-04-01', 1, 1),
(UUID(), 'DECHETS', 35.8367, 10.5911, 'ACTIF', '2024-04-15', 2, 2),
(UUID(), 'DECHETS', 35.8256, 10.6034, 'HORS_SERVICE', '2024-05-01', 1, 3),
(UUID(), 'DECHETS', 35.8400, 10.5845, 'ACTIF', '2024-05-15', 2, 4),
(UUID(), 'DECHETS', 35.8231, 10.6122, 'ACTIF', '2024-06-01', 1, 5),
-- Capteurs ECLAIRAGE (10)
(UUID(), 'ECLAIRAGE', 35.8300, 10.6011, 'ACTIF', '2024-01-08', 1, 1),
(UUID(), 'ECLAIRAGE', 35.8356, 10.5935, 'ACTIF', '2024-01-22', 1, 2),
(UUID(), 'ECLAIRAGE', 35.8233, 10.6067, 'ACTIF', '2024-02-08', 1, 3),
(UUID(), 'ECLAIRAGE', 35.8445, 10.5878, 'ACTIF', '2024-02-22', 1, 4),
(UUID(), 'ECLAIRAGE', 35.8189, 10.6156, 'ACTIF', '2024-03-10', 1, 5),
(UUID(), 'ECLAIRAGE', 35.8322, 10.6000, 'MAINTENANCE', '2024-03-25', 1, 1),
(UUID(), 'ECLAIRAGE', 35.8378, 10.5922, 'ACTIF', '2024-04-08', 1, 2),
(UUID(), 'ECLAIRAGE', 35.8267, 10.6045, 'ACTIF', '2024-04-22', 1, 3),
(UUID(), 'ECLAIRAGE', 35.8411, 10.5856, 'ACTIF', '2024-05-08', 1, 4),
(UUID(), 'ECLAIRAGE', 35.8242, 10.6133, 'ACTIF', '2024-05-22', 1, 5);

-- Citoyens (30)
INSERT INTO citoyen (identifiant_unique, nom, prenom, email, score_engagement, preference_mobilite) VALUES
('CIT-2024-001', 'Mansouri', 'Yassine', 'ymansouri@email.tn', 85.50, 'VELO'),
('CIT-2024-002', 'Khelifi', 'Nadia', 'nkhelifi@email.tn', 92.30, 'TRANSPORT_COMMUN'),
('CIT-2024-003', 'Bouzid', 'Rami', 'rbouzid@email.tn', 78.20, 'COVOITURAGE'),
('CIT-2024-004', 'Selmi', 'Ines', 'iselmi@email.tn', 88.75, 'MARCHE'),
('CIT-2024-005', 'Chaabane', 'Hatem', 'hchaabane@email.tn', 65.40, 'VEHICULE_ELECTRIQUE'),
('CIT-2024-006', 'Ferchichi', 'Salma', 'sferchichi@email.tn', 91.00, 'VELO'),
('CIT-2024-007', 'Jebali', 'Mehdi', 'mjebali@email.tn', 72.80, 'TRANSPORT_COMMUN'),
('CIT-2024-008', 'Ammar', 'Rim', 'rammar@email.tn', 86.25, 'COVOITURAGE'),
('CIT-2024-009', 'Haddad', 'Tarek', 'thaddad@email.tn', 69.50, 'MARCHE'),
('CIT-2024-010', 'Dridi', 'Mariem', 'mdridi@email.tn', 94.00, 'VELO');

-- Véhicules (20)
INSERT INTO vehicule (plaque, type, energie, marque, modele, annee_mise_service, capacite_passagers, autonomie_km) VALUES
('TN-SMART-001', 'BUS', 'ELECTRIQUE', 'BYD', 'K9', 2024, 45, 250),
('TN-SMART-002', 'BUS', 'ELECTRIQUE', 'BYD', 'K9', 2024, 45, 250),
('TN-SMART-003', 'BUS', 'HYDROGENE', 'Toyota', 'Sora', 2024, 40, 300),
('TN-SMART-004', 'NAVETTE', 'ELECTRIQUE', 'Navya', 'Autonom', 2024, 15, 100),
('TN-SMART-005', 'NAVETTE', 'ELECTRIQUE', 'Navya', 'Autonom', 2024, 15, 100),
('TN-SMART-006', 'NAVETTE', 'ELECTRIQUE', 'EasyMile', 'EZ10', 2024, 12, 80),
('TN-SMART-007', 'UTILITAIRE', 'ELECTRIQUE', 'Renault', 'Master E-Tech', 2024, 3, 180),
('TN-SMART-008', 'UTILITAIRE', 'ELECTRIQUE', 'Mercedes', 'eSprinter', 2024, 3, 160),
('TN-SMART-009', 'COLLECTE_DECHETS', 'HYDROGENE', 'Hyzon', 'Class 8', 2024, 2, 400),
('TN-SMART-010', 'COLLECTE_DECHETS', 'ELECTRIQUE', 'Volvo', 'FE Electric', 2024, 2, 200),
('TN-SMART-011', 'BUS', 'HYBRIDE', 'Volvo', '7900 Hybrid', 2023, 50, 350),
('TN-SMART-012', 'NAVETTE', 'ELECTRIQUE', 'Local Motors', 'Olli', 2024, 8, 60),
('TN-SMART-013', 'UTILITAIRE', 'ELECTRIQUE', 'Ford', 'E-Transit', 2024, 3, 200),
('TN-SMART-014', 'BUS', 'ELECTRIQUE', 'Yutong', 'E12', 2024, 42, 280),
('TN-SMART-015', 'NAVETTE', 'ELECTRIQUE', 'Navya', 'Autonom', 2024, 15, 100);

-- Note: Interventions et mesures seront générées par l'ETL Django
