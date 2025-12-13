"""
Commande ETL pour Smart City Neo-Sousse 2030
Simule l'importation de données et génère des rapports
Usage: python manage.py run_etl --action [generate|report|all]
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from api.models import (
    Capteur, Mesure, Intervention, Technicien,
    Citoyen, Consultation, Vehicule, Trajet
)


class Command(BaseCommand):
    help = 'ETL: Génère des données simulées et produit des rapports analytiques'
    
    def __init__(self):
        super().__init__()
        self.fake = Faker('fr_FR')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            default='all',
            choices=['generate', 'report', 'all'],
            help='Action à effectuer: generate (données), report (rapports), all (les deux)'
        )
        parser.add_argument(
            '--mesures',
            type=int,
            default=500,
            help='Nombre de mesures à générer'
        )
        parser.add_argument(
            '--interventions',
            type=int,
            default=100,
            help='Nombre d\'interventions à générer'
        )
        parser.add_argument(
            '--trajets',
            type=int,
            default=200,
            help='Nombre de trajets à générer'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'  Smart City Neo-Sousse 2030 - ETL Pipeline\n'
            f'  Date: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
            f'{"="*60}\n'
        ))
        
        if action in ['generate', 'all']:
            self.generate_mesures(options['mesures'])
            self.generate_interventions(options['interventions'])
            self.generate_trajets(options['trajets'])
            self.generate_consultations()
        
        if action in ['report', 'all']:
            self.generate_rapport_qualite_air()
            self.generate_rapport_maintenance()
            self.generate_rapport_mobilite()
        
        self.stdout.write(self.style.SUCCESS('\n✓ ETL terminé avec succès!\n'))
    
    def generate_mesures(self, count):
        """Génère des mesures simulées pour les capteurs"""
        self.stdout.write('\n📊 Génération des mesures...')
        
        capteurs = list(Capteur.objects.filter(statut='ACTIF'))
        if not capteurs:
            self.stdout.write(self.style.WARNING('  Aucun capteur actif trouvé'))
            return
        
        mesures = []
        now = timezone.now()
        
        for i in range(count):
            capteur = random.choice(capteurs)
            timestamp = now - timedelta(hours=random.randint(0, 168))  # 7 jours
            
            # Valeurs selon le type de capteur
            valeurs = self._generate_valeurs(capteur.type)
            indice = None
            qualite = None
            
            if capteur.type == 'AIR':
                indice = Decimal(str(random.uniform(20, 250)))
                qualite = self._get_qualite_air(float(indice))
            
            mesures.append(Mesure(
                capteur=capteur,
                timestamp=timestamp,
                valeurs=valeurs,
                indice_pollution=indice,
                qualite_air=qualite
            ))
        
        Mesure.objects.bulk_create(mesures, batch_size=100)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} mesures générées'))
    
    def _generate_valeurs(self, type_capteur):
        """Génère des valeurs selon le type de capteur"""
        if type_capteur == 'AIR':
            return {
                'pm25': round(random.uniform(5, 100), 1),
                'pm10': round(random.uniform(10, 150), 1),
                'co2': round(random.uniform(300, 800), 0),
                'no2': round(random.uniform(10, 80), 1),
                'o3': round(random.uniform(20, 100), 1)
            }
        elif type_capteur == 'TRAFIC':
            return {
                'vehicules_heure': random.randint(50, 500),
                'vitesse_moyenne': round(random.uniform(15, 60), 1),
                'congestion': round(random.uniform(0, 100), 1)
            }
        elif type_capteur == 'ENERGIE':
            return {
                'consommation_kwh': round(random.uniform(100, 1000), 2),
                'pic_demande': round(random.uniform(50, 200), 2)
            }
        elif type_capteur == 'DECHETS':
            return {
                'niveau_remplissage': round(random.uniform(0, 100), 1),
                'temperature': round(random.uniform(15, 35), 1)
            }
        else:  # ECLAIRAGE
            return {
                'etat': random.choice(['ON', 'OFF', 'DIM']),
                'consommation_w': round(random.uniform(20, 150), 1),
                'luminosite': round(random.uniform(0, 100), 1)
            }
    
    def _get_qualite_air(self, indice):
        """Détermine la qualité de l'air"""
        if indice <= 50:
            return 'BON'
        elif indice <= 100:
            return 'MODERE'
        elif indice <= 150:
            return 'MAUVAIS'
        elif indice <= 200:
            return 'TRES_MAUVAIS'
        return 'DANGEREUX'
    
    def generate_interventions(self, count):
        """Génère des interventions de maintenance"""
        self.stdout.write('\n🔧 Génération des interventions...')
        
        capteurs = list(Capteur.objects.all())
        techniciens = list(Technicien.objects.filter(actif=True, type_validation='HUMAIN'))
        validateurs = list(Technicien.objects.filter(actif=True))
        
        if not capteurs or len(techniciens) < 1 or len(validateurs) < 2:
            self.stdout.write(self.style.WARNING('  Données insuffisantes pour générer des interventions'))
            return
        
        natures = ['PREDICTIVE', 'CORRECTIVE', 'CURATIVE']
        statuts = ['TERMINEE', 'TERMINEE', 'TERMINEE', 'PLANIFIEE', 'EN_COURS']
        
        interventions = []
        now = timezone.now()
        
        for i in range(count):
            capteur = random.choice(capteurs)
            intervenant = random.choice(techniciens)
            
            # Validateur différent de l'intervenant
            validateur = random.choice([t for t in validateurs if t.id != intervenant.id])
            
            date_heure = now - timedelta(days=random.randint(0, 90))
            
            interventions.append(Intervention(
                capteur=capteur,
                date_heure=date_heure,
                nature=random.choice(natures),
                description=self.fake.sentence(),
                duree_minutes=random.randint(30, 240),
                cout=Decimal(str(random.uniform(50, 500))),
                reduction_co2=Decimal(str(random.uniform(0.5, 10))) if random.random() > 0.3 else None,
                statut=random.choice(statuts),
                technicien_intervenant=intervenant,
                technicien_validateur=validateur
            ))
        
        Intervention.objects.bulk_create(interventions, batch_size=50)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} interventions générées'))
    
    def generate_trajets(self, count):
        """Génère des trajets pour les véhicules"""
        self.stdout.write('\n🚌 Génération des trajets...')
        
        vehicules = list(Vehicule.objects.filter(statut='EN_SERVICE'))
        if not vehicules:
            self.stdout.write(self.style.WARNING('  Aucun véhicule en service'))
            return
        
        lieux = [
            'Gare Centrale', 'Centre-Ville', 'Université', 'Hôpital Sahloul',
            'Port de Sousse', 'Médina', 'Zone Industrielle', 'Aéroport',
            'Stade Olympique', 'Marina', 'Kantaoui', 'Centre Commercial'
        ]
        
        trajets = []
        now = timezone.now()
        
        for i in range(count):
            vehicule = random.choice(vehicules)
            origine = random.choice(lieux)
            destination = random.choice([l for l in lieux if l != origine])
            
            depart = now - timedelta(hours=random.randint(0, 720))  # 30 jours
            duree = timedelta(minutes=random.randint(10, 60))
            
            distance = round(random.uniform(2, 25), 2)
            
            # Économie CO2 basée sur distance et type de véhicule
            base_eco = distance * 0.12  # kg CO2 par km
            if vehicule.energie == 'HYDROGENE':
                base_eco *= 1.2
            elif vehicule.energie == 'HYBRIDE':
                base_eco *= 0.7
            
            trajets.append(Trajet(
                vehicule=vehicule,
                origine=origine,
                destination=destination,
                depart=depart,
                arrivee=depart + duree,
                distance_km=Decimal(str(distance)),
                economie_co2=Decimal(str(round(base_eco, 4))),
                nombre_passagers=random.randint(0, vehicule.capacite_passagers or 20),
                statut='TERMINE'
            ))
        
        Trajet.objects.bulk_create(trajets, batch_size=50)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count} trajets générés'))
    
    def generate_consultations(self):
        """Génère des consultations de données par les citoyens"""
        self.stdout.write('\n👥 Génération des consultations...')
        
        citoyens = list(Citoyen.objects.all())
        if not citoyens:
            self.stdout.write(self.style.WARNING('  Aucun citoyen trouvé'))
            return
        
        types_donnees = ['qualite_air', 'trafic', 'energie', 'dechets', 'transport']
        zones = ['Centre-Ville', 'Khezama', 'Sahloul', 'Hammam-Sousse', 'Akouda']
        sources = ['WEB', 'MOBILE', 'MOBILE', 'API']
        
        consultations = []
        now = timezone.now()
        
        for citoyen in citoyens:
            nb_consult = random.randint(1, 20)
            for _ in range(nb_consult):
                consultations.append(Consultation(
                    citoyen=citoyen,
                    timestamp=now - timedelta(days=random.randint(0, 60)),
                    type_donnee=random.choice(types_donnees),
                    zone_consultee=random.choice(zones),
                    duree_consultation_secondes=random.randint(10, 300),
                    source_consultation=random.choice(sources)
                ))
        
        Consultation.objects.bulk_create(consultations, batch_size=100)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(consultations)} consultations générées'))
    
    def generate_rapport_qualite_air(self):
        """Génère un rapport sur la qualité de l'air"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📋 RAPPORT QUALITÉ DE L\'AIR')
        self.stdout.write('='*50)
        
        depuis = timezone.now() - timedelta(hours=24)
        mesures = Mesure.objects.filter(
            capteur__type='AIR',
            timestamp__gte=depuis
        ).select_related('capteur__arrondissement')
        
        if not mesures:
            self.stdout.write('  Aucune mesure disponible')
            return
        
        # Stats par qualité
        from django.db.models import Count
        stats = mesures.values('qualite_air').annotate(count=Count('id'))
        
        self.stdout.write(f'\nMesures des dernières 24h: {mesures.count()}')
        self.stdout.write('\nRépartition par qualité:')
        for s in stats:
            self.stdout.write(f'  • {s["qualite_air"]}: {s["count"]}')
    
    def generate_rapport_maintenance(self):
        """Génère un rapport de maintenance"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📋 RAPPORT MAINTENANCE')
        self.stdout.write('='*50)
        
        from django.db.models import Sum, Count, Avg
        
        stats = Intervention.objects.filter(statut='TERMINEE').aggregate(
            total=Count('id'),
            reduction_co2=Sum('reduction_co2'),
            cout_total=Sum('cout'),
            duree_moyenne=Avg('duree_minutes')
        )
        
        self.stdout.write(f'\nInterventions terminées: {stats["total"]}')
        self.stdout.write(f'Réduction CO2 totale: {stats["reduction_co2"] or 0:.2f} kg')
        self.stdout.write(f'Coût total: {stats["cout_total"] or 0:.2f} TND')
        self.stdout.write(f'Durée moyenne: {stats["duree_moyenne"] or 0:.0f} min')
    
    def generate_rapport_mobilite(self):
        """Génère un rapport de mobilité durable"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📋 RAPPORT MOBILITÉ DURABLE')
        self.stdout.write('='*50)
        
        from django.db.models import Sum, Count
        
        stats = Trajet.objects.filter(statut='TERMINE').aggregate(
            total=Count('id'),
            distance=Sum('distance_km'),
            co2=Sum('economie_co2'),
            passagers=Sum('nombre_passagers')
        )
        
        self.stdout.write(f'\nTrajets effectués: {stats["total"]}')
        self.stdout.write(f'Distance totale: {stats["distance"] or 0:.2f} km')
        self.stdout.write(f'CO2 économisé: {stats["co2"] or 0:.2f} kg')
        self.stdout.write(f'Passagers transportés: {stats["passagers"] or 0}')
