"""
Service de données pour le module Rapports IA
Récupère les données agrégées depuis les modèles existants
pour alimenter le contexte du LLM.
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q

from api.models import (
    Capteur, Mesure, Intervention, Arrondissement,
    Vehicule, Trajet, Citoyen
)


class DataService:
    """Fournit les données agrégées pour les rapports IA"""

    @staticmethod
    def get_air_quality_data(date_str=None):
        """
        Récupère les données de qualité de l'air.
        """
        depuis = timezone.now() - timedelta(hours=24)

        # Stats globales
        mesures = Mesure.objects.filter(
            capteur__type='AIR',
            timestamp__gte=depuis
        )

        total_mesures = mesures.count()

        # Répartition par qualité
        qualite_stats = list(
            mesures.values('qualite_air')
            .annotate(count=Count('id'))
            .order_by('qualite_air')
        )

        # Zones les plus polluées
        zones = list(
            Arrondissement.objects.annotate(
                pollution_moyenne=Avg(
                    'capteurs__mesures__indice_pollution',
                    filter=Q(
                        capteurs__type='AIR',
                        capteurs__mesures__timestamp__gte=depuis
                    )
                ),
                nb_mesures=Count(
                    'capteurs__mesures',
                    filter=Q(
                        capteurs__type='AIR',
                        capteurs__mesures__timestamp__gte=depuis
                    )
                )
            ).filter(pollution_moyenne__isnull=False)
            .order_by('-pollution_moyenne')
            .values('nom', 'pollution_moyenne', 'nb_mesures')[:5]
        )

        # Capteurs hors service
        capteurs_hs = Capteur.objects.filter(
            type='AIR', statut='HORS_SERVICE'
        ).count()

        return {
            'date': date_str or timezone.now().strftime('%Y-%m-%d'),
            'periode': 'Dernières 24 heures',
            'total_mesures': total_mesures,
            'qualite_repartition': qualite_stats,
            'zones_polluees': [
                {
                    'zone': z['nom'],
                    'pollution': round(float(z['pollution_moyenne']), 2) if z['pollution_moyenne'] else 0,
                    'mesures': z['nb_mesures']
                }
                for z in zones
            ],
            'capteurs_air_hs': capteurs_hs,
            'total_capteurs_air': Capteur.objects.filter(type='AIR').count(),
        }

    @staticmethod
    def get_interventions_data(date_str=None):
        """
        Récupère les données d'interventions de maintenance.
        """
        stats = Intervention.objects.filter(
            statut='TERMINEE'
        ).aggregate(
            total=Count('id'),
            reduction_co2=Sum('reduction_co2'),
            cout_total=Sum('cout'),
            duree_moyenne=Avg('duree_minutes')
        )

        par_nature = list(
            Intervention.objects.filter(statut='TERMINEE')
            .values('nature')
            .annotate(
                count=Count('id'),
                co2=Sum('reduction_co2'),
                cout=Sum('cout')
            )
        )

        en_cours = Intervention.objects.filter(statut='EN_COURS').count()
        planifiees = Intervention.objects.filter(statut='PLANIFIEE').count()

        return {
            'date': date_str or timezone.now().strftime('%Y-%m-%d'),
            'terminees': stats['total'] or 0,
            'reduction_co2_kg': round(float(stats['reduction_co2'] or 0), 2),
            'cout_total_tnd': round(float(stats['cout_total'] or 0), 2),
            'duree_moyenne_min': round(float(stats['duree_moyenne'] or 0), 0),
            'en_cours': en_cours,
            'planifiees': planifiees,
            'par_nature': [
                {
                    'nature': n['nature'],
                    'count': n['count'],
                    'co2_kg': round(float(n['co2'] or 0), 2),
                    'cout_tnd': round(float(n['cout'] or 0), 2),
                }
                for n in par_nature
            ],
        }

    @staticmethod
    def get_capteurs_data(date_str=None):
        """
        Récupère les données sur l'état des capteurs.
        """
        total = Capteur.objects.count()
        par_statut = list(
            Capteur.objects.values('statut')
            .annotate(count=Count('uuid'))
        )
        par_type = list(
            Capteur.objects.values('type')
            .annotate(
                count=Count('uuid'),
                actifs=Count('uuid', filter=Q(statut='ACTIF')),
                hs=Count('uuid', filter=Q(statut='HORS_SERVICE'))
            )
        )

        taux_dispo = 0
        actifs = sum(s['count'] for s in par_statut if s['statut'] == 'ACTIF')
        if total > 0:
            taux_dispo = round((actifs / total) * 100, 1)

        return {
            'date': date_str or timezone.now().strftime('%Y-%m-%d'),
            'total_capteurs': total,
            'taux_disponibilite': taux_dispo,
            'par_statut': [
                {'statut': s['statut'], 'count': s['count']}
                for s in par_statut
            ],
            'par_type': [
                {
                    'type': t['type'],
                    'total': t['count'],
                    'actifs': t['actifs'],
                    'hors_service': t['hs'],
                }
                for t in par_type
            ],
        }

    @staticmethod
    def get_capteur_detail(capteur_id):
        """
        Récupère les détails d'un capteur spécifique pour les suggestions.
        """
        try:
            capteur = Capteur.objects.select_related(
                'arrondissement', 'proprietaire'
            ).get(uuid=capteur_id)
        except Capteur.DoesNotExist:
            return None

        # Dernières mesures
        derniere_mesure = capteur.mesures.order_by('-timestamp').first()

        # Interventions récentes
        interventions_recentes = capteur.interventions.order_by('-date_heure')[:5]
        nb_interventions = capteur.interventions.count()

        # Taux d'erreur simulé basé sur le nombre d'interventions
        taux_erreur = min(round((nb_interventions / max(1, 10)) * 100, 1), 100)

        return {
            'capteur_id': capteur.uuid,
            'type': capteur.type,
            'statut': capteur.statut,
            'arrondissement': capteur.arrondissement.nom,
            'proprietaire': capteur.proprietaire.nom,
            'date_installation': capteur.date_installation.isoformat(),
            'derniere_mesure': {
                'timestamp': derniere_mesure.timestamp.isoformat() if derniere_mesure else None,
                'indice_pollution': float(derniere_mesure.indice_pollution) if derniere_mesure and derniere_mesure.indice_pollution else None,
                'qualite_air': derniere_mesure.qualite_air if derniere_mesure else None,
            },
            'nb_interventions': nb_interventions,
            'taux_erreur': taux_erreur,
            'interventions_recentes': [
                {
                    'date': i.date_heure.isoformat(),
                    'nature': i.nature,
                    'statut': i.statut,
                }
                for i in interventions_recentes
            ],
        }
