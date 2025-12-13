
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
    Trajet
)

def populate():
    print("Creating initial data...")

    # 1. Arrondissements
    arrondissements = [
        Arrondissement(nom="Medina", code_postal="4000", superficie_km2=5.2, population=25000),
        Arrondissement(nom="Sahloul", code_postal="4054", superficie_km2=8.5, population=45000),
        Arrondissement(nom="Khezama", code_postal="4051", superficie_km2=6.3, population=35000),
        Arrondissement(nom="Erriyadh", code_postal="4023", superficie_km2=7.1, population=30000),
    ]
    for a in arrondissements:
        a.save()
    print(f"Created {len(arrondissements)} arrondissements")

    # 2. Proprietaires
    props = [
        Proprietaire(nom="Municipalité Sousse", type="MUNICIPALITE", contact_email="contact@sousse.tn"),
        Proprietaire(nom="GreenTech Solutions", type="PRIVE", contact_email="info@greentech.tn"),
    ]
    for p in props:
        p.save()
    
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
    vehicules = [
        Vehicule(plaque="SO-1234", type="BUS", energie="ELECTRIQUE"),
        Vehicule(plaque="SO-5678", type="NAVETTE", energie="HYDROGENE"),
    ]
    for v in vehicules:
        v.save()
        # Create some trips
        for i in range(5):
            Trajet.objects.create(
                vehicule=v,
                origine="Station A",
                destination="Station B",
                depart=datetime.now() - timedelta(hours=i*2),
                arrivee=datetime.now() - timedelta(hours=i*2) + timedelta(minutes=30),
                distance_km=12.5,
                economie_co2=Decimal(2.5),
                statut='TERMINE'
            )

    print("Database successfully populated!")

if __name__ == '__main__':
    populate()
