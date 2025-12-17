
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_city.settings')
django.setup()

from api.models import (
    Arrondissement, 
    Proprietaire, 
    Capteur, 
    Mesure, 
    Technicien, 
    Intervention,
    Citoyen,
    Vehicule,
    Trajet,
    Consultation
)

def populate():
    print("Creating initial data...")

    # 1. Arrondissements
    arrondissements_data = [
        {"nom": "Medina", "code_postal": "4000", "superficie_km2": 5.2, "population": 25000},
        {"nom": "Sahloul", "code_postal": "4054", "superficie_km2": 8.5, "population": 45000},
        {"nom": "Khezama", "code_postal": "4051", "superficie_km2": 6.3, "population": 35000},
        {"nom": "Erriyadh", "code_postal": "4023", "superficie_km2": 7.1, "population": 30000},
        {"nom": "Sidi Abdelhamid", "code_postal": "4061", "superficie_km2": 9.2, "population": 40000},
        {"nom": "Hammam Sousse", "code_postal": "4011", "superficie_km2": 10.5, "population": 42000},
    ]
    for data in arrondissements_data:
        Arrondissement.objects.get_or_create(code_postal=data['code_postal'], defaults=data)
    print("Checked/Created arrondissements")

    # 2. Proprietaires
    props_data = [
        {"nom": "Municipalité Sousse", "type": "MUNICIPALITE", "contact_email": "contact@sousse.tn"},
        {"nom": "GreenTech Solutions", "type": "PRIVE", "contact_email": "info@greentech.tn"},
    ]
    props = []
    for data in props_data:
        p, _ = Proprietaire.objects.get_or_create(nom=data['nom'], defaults=data)
        props.append(p)
    
    # 3. Capteurs & Mesures
    types_capteur = ['AIR', 'TRAFIC', 'ENERGIE']
    all_capteurs = []
    
    for arr in Arrondissement.objects.all():
        for _ in range(3): # 3 capteurs par arrondissement
            c = Capteur(
                type=random.choice(types_capteur),
                latitude=35.82 + random.uniform(-0.05, 0.05),
                longitude=10.63 + random.uniform(-0.05, 0.05),
                statut='ACTIF',
                date_installation='2024-01-01',
                proprietaire=props[0],
                arrondissement=arr
            )
            c.save()
            all_capteurs.append(c)

            # Generate fake measurements for last 7 days
            for d in range(7):
                Mesure.objects.create(
                    capteur=c,
                    timestamp=datetime.now() - timedelta(days=d),
                    valeurs={"value": random.randint(10, 100)},
                    indice_pollution=Decimal(random.uniform(10, 80)),
                    qualite_air=random.choice(['BON', 'MODERE'])
                )
    print(f"Created {len(all_capteurs)} capteurs sites with history")

    # 4. Vehicules & Trajets
    vehicules_data = [
        {"plaque": "SO-1234", "type": "BUS", "energie": "ELECTRIQUE", "marque": "BYD", "modele": "K9", "annee_mise_service": 2023, "capacite_passagers": 50, "autonomie_km": 300},
        {"plaque": "SO-5678", "type": "NAVETTE", "energie": "HYDROGENE", "marque": "Navya", "modele": "Autonom Shuttle", "annee_mise_service": 2024, "capacite_passagers": 15, "autonomie_km": 150},
        {"plaque": "SO-9012", "type": "BUS", "energie": "HYBRIDE", "marque": "Mercedes", "modele": "Citaro", "annee_mise_service": 2022, "capacite_passagers": 45, "autonomie_km": 600},
        {"plaque": "TR-4521", "type": "UTILITAIRE", "energie": "ELECTRIQUE", "marque": "Renault", "modele": "Kangoo ZE", "annee_mise_service": 2023, "capacite_passagers": 2, "autonomie_km": 200},
        {"plaque": "TR-8899", "type": "COLLECTE_DECHETS", "energie": "ELECTRIQUE", "marque": "Volvo", "modele": "FE Electric", "annee_mise_service": 2024, "capacite_passagers": 3, "autonomie_km": 180},
    ]
    
    for v_data in vehicules_data:
        # Use update_or_create to fix existing records with NULLs
        v, created = Vehicule.objects.update_or_create(
            plaque=v_data['plaque'],
            defaults=v_data
        )
        
        # Ensure trips exist for these vehicles
        if Trajet.objects.filter(vehicule=v).count() == 0:
             for _ in range(5):
                 depart_time = datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                 Trajet.objects.create(
                    vehicule=v,
                    origine=random.choice(["Centre Ville", "Sahloul", "Khezama", "Port El Kantaoui"]),
                    destination=random.choice(["Aeroport", "Zone Industrielle", "Campus Universitaire", "Medina"]),
                    depart=depart_time,
                    arrivee=depart_time + timedelta(minutes=random.randint(15, 60)),
                    distance_km=Decimal(random.uniform(2.0, 15.0)),
                    economie_co2=Decimal(random.uniform(0.5, 3.0)),
                    nombre_passagers=random.randint(1, 20),
                    statut='TERMINE'
                 )
    print(f"Updated/Created {len(vehicules_data)} rich vehicle records")

    # 5. Citoyens
    for i in range(20):
        ident = f"CIT-{100+i}"
        c, created = Citoyen.objects.get_or_create(
            identifiant_unique=ident,
            defaults={
                "nom": f"Citoyen{i}",
                "prenom": f"Prenom{i}",
                "email": f"citoyen{i}@test.com",
                "score_engagement": Decimal(random.uniform(10, 95)),
                "preference_mobilite": random.choice(['VELO', 'TRANSPORT_COMMUN', 'MARCHE'])
            }
        )
        # Create consultations
        for _ in range(random.randint(1, 5)):
             Consultation.objects.create(
                citoyen=c,
                type_donnee=random.choice(['Qualité Air', 'Trafic', 'Consommation']),
                zone_consultee=random.choice(['Sahloul', 'Medina', 'Khezama']),
                duree_consultation_secondes=random.randint(10, 300),
                source_consultation=random.choice(['WEB', 'MOBILE'])
             )
    print("Populated Citizens and Consultations")

    # 6. Techniciens
    techs_data = [
        Technicien(matricule="TECH-01", nom="Saleh", prenom="Karim", type_validation="HUMAIN"),
        Technicien(matricule="TECH-02", nom="System", prenom="IA", type_validation="IA"),
        Technicien(matricule="TECH-03", nom="Masmoudi", prenom="Leila", type_validation="HUMAIN"),
    ]
    techs_created = []
    for t in techs_data:
        obj, _ = Technicien.objects.get_or_create(matricule=t.matricule, defaults={
            "nom": t.nom, "prenom": t.prenom, "type_validation": t.type_validation
        })
        techs_created.append(obj)
    
    # 7. Interventions
    techs = Technicien.objects.all() # Refresh list

    # 7. Interventions
    # Need to fetch capteurs again or use the list if available
    caps = Capteur.objects.all()
    if caps.exists() and len(techs) >= 2:
        natures = ['PREDICTIVE', 'CORRECTIVE', 'CURATIVE']
        for i in range(50):
            Intervention.objects.create(
                capteur=random.choice(caps),
                date_heure=datetime.now() - timedelta(days=random.randint(0, 30)),
                nature=random.choice(natures),
                description="Intervention de maintenance standard",
                duree_minutes=random.randint(30, 120),
                cout=Decimal(random.randint(50, 500)),
                reduction_co2=Decimal(random.uniform(5, 50)),
                statut='TERMINEE',
                technicien_intervenant=techs[0], # Karim
                technicien_validateur=techs[1]   # IA
            )
        print("Created 10 interventions")

    print("Database successfully populated!")

if __name__ == '__main__':
    populate()
