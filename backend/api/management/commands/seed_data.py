"""
Commande pour créer les données initiales de base
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from api.models import (
    Arrondissement, Proprietaire, Capteur, Technicien,
    Citoyen, Vehicule
)
import uuid
from datetime import date
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Crée les données initiales de la base de données'
    
    def handle(self, *args, **options):
        self.stdout.write('🏗️ Création des données initiales...\n')
        
        # Arrondissements
        arrondissements = [
            ('Centre-Ville', '4000', 8.5, 45000),
            ('Khezama', '4051', 12.3, 32000),
            ('Sahloul', '4054', 15.7, 28000),
            ('Hammam-Sousse', '4011', 18.2, 38000),
            ('Akouda', '4022', 22.5, 25000),
        ]
        
        arr_objs = []
        for nom, code, superficie, pop in arrondissements:
            arr, _ = Arrondissement.objects.get_or_create(
                code_postal=code,
                defaults={'nom': nom, 'superficie_km2': superficie, 'population': pop}
            )
            arr_objs.append(arr)
        self.stdout.write(f'  ✓ {len(arr_objs)} arrondissements')
        
        # Propriétaires
        props = [
            ('Municipalité Neo-Sousse', 'MUNICIPALITE', 'contact@neosousse.tn'),
            ('TechnoGreen Solutions', 'PRIVE', 'info@technogreen.tn'),
            ('EcoSmart Tunisia', 'PRIVE', 'contact@ecosmart.tn'),
            ('SmartGrid Africa', 'PRIVE', 'info@smartgrid.africa'),
        ]
        
        prop_objs = []
        for nom, type_p, email in props:
            prop, _ = Proprietaire.objects.get_or_create(
                nom=nom,
                defaults={'type': type_p, 'contact_email': email}
            )
            prop_objs.append(prop)
        self.stdout.write(f'  ✓ {len(prop_objs)} propriétaires')
        
        # Techniciens
        techs = [
            ('TECH001', 'Ben Ali', 'Mohamed', 'Capteurs Air', 'HUMAIN'),
            ('TECH002', 'Trabelsi', 'Fatma', 'Trafic', 'HUMAIN'),
            ('TECH003', 'Gharbi', 'Ahmed', 'Énergie', 'HUMAIN'),
            ('TECH004', 'Mejri', 'Sonia', 'Déchets', 'HUMAIN'),
            ('TECH005', 'Hamdi', 'Karim', 'Éclairage', 'HUMAIN'),
            ('TECH006', 'Bouazizi', 'Leila', 'Multi-capteurs', 'HUMAIN'),
            ('TECH007', 'Saidi', 'Omar', 'Capteurs Air', 'HUMAIN'),
            ('TECH008', 'Nasr', 'Amira', 'Trafic', 'HUMAIN'),
            ('AI-VAL01', 'Système', 'IA-Validator-1', 'Validation IA', 'IA'),
            ('AI-VAL02', 'Système', 'IA-Validator-2', 'Validation IA', 'IA'),
        ]
        
        tech_objs = []
        for matricule, nom, prenom, specialite, type_v in techs:
            tech, _ = Technicien.objects.get_or_create(
                matricule=matricule,
                defaults={'nom': nom, 'prenom': prenom, 'specialite': specialite, 'type_validation': type_v}
            )
            tech_objs.append(tech)
        self.stdout.write(f'  ✓ {len(tech_objs)} techniciens')
        
        # Capteurs (50)
        types_capteur = ['AIR', 'TRAFIC', 'ENERGIE', 'DECHETS', 'ECLAIRAGE']
        capteur_count = 0
        for i in range(50):
            type_c = types_capteur[i % 5]
            arr = arr_objs[i % 5]
            prop = prop_objs[i % 4]
            
            Capteur.objects.get_or_create(
                uuid=uuid.uuid4(),
                defaults={
                    'type': type_c,
                    'latitude': Decimal('35.82') + Decimal(str(random.uniform(-0.02, 0.02))),
                    'longitude': Decimal('10.59') + Decimal(str(random.uniform(-0.02, 0.02))),
                    'statut': random.choice(['ACTIF', 'ACTIF', 'ACTIF', 'MAINTENANCE', 'HORS_SERVICE']),
                    'date_installation': date(2024, random.randint(1, 12), random.randint(1, 28)),
                    'proprietaire': prop,
                    'arrondissement': arr
                }
            )
            capteur_count += 1
        self.stdout.write(f'  ✓ {capteur_count} capteurs')
        
        # Citoyens (30)
        prenoms = ['Yassine', 'Nadia', 'Rami', 'Ines', 'Hatem', 'Salma', 'Mehdi', 'Rim', 'Tarek', 'Mariem']
        noms = ['Mansouri', 'Khelifi', 'Bouzid', 'Selmi', 'Chaabane', 'Ferchichi', 'Jebali', 'Ammar', 'Haddad', 'Dridi']
        mobilites = ['VELO', 'TRANSPORT_COMMUN', 'COVOITURAGE', 'MARCHE', 'VEHICULE_ELECTRIQUE']
        
        citoyen_count = 0
        for i in range(30):
            prenom = prenoms[i % len(prenoms)]
            nom = noms[i % len(noms)]
            Citoyen.objects.get_or_create(
                identifiant_unique=f'CIT-2024-{i+1:03d}',
                defaults={
                    'nom': nom,
                    'prenom': prenom,
                    'email': f'{prenom.lower()}{i}@email.tn',
                    'score_engagement': Decimal(str(random.uniform(50, 98))),
                    'preference_mobilite': random.choice(mobilites)
                }
            )
            citoyen_count += 1
        self.stdout.write(f'  ✓ {citoyen_count} citoyens')
        
        # Véhicules (20)
        vehicules = [
            ('TN-SMART-001', 'BUS', 'ELECTRIQUE', 'BYD', 'K9', 45, 250),
            ('TN-SMART-002', 'BUS', 'ELECTRIQUE', 'BYD', 'K9', 45, 250),
            ('TN-SMART-003', 'BUS', 'HYDROGENE', 'Toyota', 'Sora', 40, 300),
            ('TN-SMART-004', 'NAVETTE', 'ELECTRIQUE', 'Navya', 'Autonom', 15, 100),
            ('TN-SMART-005', 'NAVETTE', 'ELECTRIQUE', 'Navya', 'Autonom', 15, 100),
            ('TN-SMART-006', 'NAVETTE', 'ELECTRIQUE', 'EasyMile', 'EZ10', 12, 80),
            ('TN-SMART-007', 'UTILITAIRE', 'ELECTRIQUE', 'Renault', 'Master E-Tech', 3, 180),
            ('TN-SMART-008', 'UTILITAIRE', 'ELECTRIQUE', 'Mercedes', 'eSprinter', 3, 160),
            ('TN-SMART-009', 'COLLECTE_DECHETS', 'HYDROGENE', 'Hyzon', 'Class 8', 2, 400),
            ('TN-SMART-010', 'COLLECTE_DECHETS', 'ELECTRIQUE', 'Volvo', 'FE Electric', 2, 200),
            ('TN-SMART-011', 'BUS', 'HYBRIDE', 'Volvo', '7900 Hybrid', 50, 350),
            ('TN-SMART-012', 'NAVETTE', 'ELECTRIQUE', 'Local Motors', 'Olli', 8, 60),
            ('TN-SMART-013', 'UTILITAIRE', 'ELECTRIQUE', 'Ford', 'E-Transit', 3, 200),
            ('TN-SMART-014', 'BUS', 'ELECTRIQUE', 'Yutong', 'E12', 42, 280),
            ('TN-SMART-015', 'NAVETTE', 'ELECTRIQUE', 'Navya', 'Autonom', 15, 100),
            ('TN-SMART-016', 'BUS', 'ELECTRIQUE', 'BYD', 'K9', 45, 250),
            ('TN-SMART-017', 'UTILITAIRE', 'HYBRIDE', 'Toyota', 'Proace', 3, 200),
            ('TN-SMART-018', 'NAVETTE', 'ELECTRIQUE', 'EasyMile', 'EZ10', 12, 80),
            ('TN-SMART-019', 'COLLECTE_DECHETS', 'ELECTRIQUE', 'Mack', 'LR Electric', 2, 250),
            ('TN-SMART-020', 'BUS', 'HYDROGENE', 'Van Hool', 'A330', 40, 350),
        ]
        
        veh_count = 0
        for plaque, type_v, energie, marque, modele, cap, auto in vehicules:
            Vehicule.objects.get_or_create(
                plaque=plaque,
                defaults={
                    'type': type_v,
                    'energie': energie,
                    'marque': marque,
                    'modele': modele,
                    'capacite_passagers': cap,
                    'autonomie_km': Decimal(str(auto)),
                    'annee_mise_service': 2024
                }
            )
            veh_count += 1
        self.stdout.write(f'  ✓ {veh_count} véhicules')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Données initiales créées avec succès!'))
