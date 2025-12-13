"""
API Views pour Smart City Neo-Sousse 2030
ViewSets avec actions personnalisées pour les analytics
"""

from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Arrondissement, Proprietaire, Capteur, Mesure,
    Technicien, Intervention, Citoyen, Consultation,
    Vehicule, Trajet
)
from .serializers import (
    ArrondissementSerializer, ProprietaireSerializer,
    CapteurSerializer, CapteurListSerializer, MesureSerializer,
    TechnicienSerializer, InterventionSerializer, InterventionListSerializer,
    CitoyenSerializer, CitoyenListSerializer, ConsultationSerializer,
    VehiculeSerializer, TrajetSerializer, TrajetListSerializer
)


class ArrondissementViewSet(viewsets.ModelViewSet):
    """ViewSet pour les arrondissements"""
    queryset = Arrondissement.objects.all()
    serializer_class = ArrondissementSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nom', 'code_postal']
    ordering_fields = ['nom', 'population']


class ProprietaireViewSet(viewsets.ModelViewSet):
    """ViewSet pour les propriétaires"""
    queryset = Proprietaire.objects.all()
    serializer_class = ProprietaireSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type']
    search_fields = ['nom', 'contact_email']


class CapteurViewSet(viewsets.ModelViewSet):
    """ViewSet pour les capteurs avec analytics"""
    queryset = Capteur.objects.select_related('arrondissement', 'proprietaire')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'statut', 'arrondissement', 'proprietaire']
    search_fields = ['uuid', 'description']
    ordering_fields = ['date_installation', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CapteurListSerializer
        return CapteurSerializer
    
    @action(detail=False, methods=['get'])
    def zones_polluees_24h(self, request):
        """
        Endpoint: Quelles sont les zones les plus polluées (24 dernières heures)?
        Retourne les arrondissements classés par indice de pollution moyen
        """
        depuis = timezone.now() - timedelta(hours=24)
        
        zones = Arrondissement.objects.annotate(
            pollution_moyenne=Avg(
                'capteurs__mesures__indice_pollution',
                filter=Q(
                    capteurs__type='AIR',
                    capteurs__mesures__timestamp__gte=depuis
                )
            ),
            nombre_mesures=Count(
                'capteurs__mesures',
                filter=Q(
                    capteurs__type='AIR',
                    capteurs__mesures__timestamp__gte=depuis
                )
            )
        ).filter(
            pollution_moyenne__isnull=False
        ).order_by('-pollution_moyenne')
        
        data = [{
            'arrondissement_id': z.id,
            'arrondissement_nom': z.nom,
            'code_postal': z.code_postal,
            'pollution_moyenne': round(z.pollution_moyenne, 2) if z.pollution_moyenne else None,
            'nombre_mesures': z.nombre_mesures,
            'niveau': self._get_niveau_pollution(z.pollution_moyenne)
        } for z in zones]
        
        return Response({
            'periode': '24 dernières heures',
            'depuis': depuis.isoformat(),
            'zones': data
        })
    
    def _get_niveau_pollution(self, indice):
        """Détermine le niveau de pollution selon l'indice"""
        if indice is None:
            return 'INCONNU'
        if indice <= 50:
            return 'BON'
        if indice <= 100:
            return 'MODERE'
        if indice <= 150:
            return 'MAUVAIS'
        if indice <= 200:
            return 'TRES_MAUVAIS'
        return 'DANGEREUX'
    
    @action(detail=False, methods=['get'])
    def disponibilite_par_arrondissement(self, request):
        """
        Endpoint: Quel est le taux de disponibilité des capteurs par arrondissement?
        """
        stats = Arrondissement.objects.annotate(
            total_capteurs=Count('capteurs'),
            capteurs_actifs=Count('capteurs', filter=Q(capteurs__statut='ACTIF')),
            capteurs_maintenance=Count('capteurs', filter=Q(capteurs__statut='MAINTENANCE')),
            capteurs_hors_service=Count('capteurs', filter=Q(capteurs__statut='HORS_SERVICE'))
        ).filter(total_capteurs__gt=0)
        
        data = [{
            'arrondissement_id': s.id,
            'arrondissement_nom': s.nom,
            'total_capteurs': s.total_capteurs,
            'capteurs_actifs': s.capteurs_actifs,
            'capteurs_maintenance': s.capteurs_maintenance,
            'capteurs_hors_service': s.capteurs_hors_service,
            'taux_disponibilite': round((s.capteurs_actifs / s.total_capteurs) * 100, 2)
        } for s in stats]
        
        # Taux global
        totaux = {
            'total': sum(d['total_capteurs'] for d in data),
            'actifs': sum(d['capteurs_actifs'] for d in data)
        }
        taux_global = round((totaux['actifs'] / totaux['total']) * 100, 2) if totaux['total'] > 0 else 0
        
        return Response({
            'taux_disponibilite_global': taux_global,
            'arrondissements': data
        })
    
    @action(detail=False, methods=['get'])
    def stats_par_type(self, request):
        """Statistiques des capteurs par type"""
        stats = Capteur.objects.values('type').annotate(
            total=Count('uuid'),
            actifs=Count('uuid', filter=Q(statut='ACTIF')),
            maintenance=Count('uuid', filter=Q(statut='MAINTENANCE')),
            hors_service=Count('uuid', filter=Q(statut='HORS_SERVICE'))
        ).order_by('type')
        
        return Response(list(stats))


class MesureViewSet(viewsets.ModelViewSet):
    """ViewSet pour les mesures"""
    queryset = Mesure.objects.select_related('capteur')
    serializer_class = MesureSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['capteur', 'qualite_air']
    ordering_fields = ['timestamp', 'indice_pollution']


class TechnicienViewSet(viewsets.ModelViewSet):
    """ViewSet pour les techniciens"""
    queryset = Technicien.objects.all()
    serializer_class = TechnicienSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type_validation', 'actif', 'specialite']
    search_fields = ['matricule', 'nom', 'prenom']


class InterventionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les interventions"""
    queryset = Intervention.objects.select_related(
        'capteur', 'capteur__arrondissement',
        'technicien_intervenant', 'technicien_validateur'
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['nature', 'statut', 'capteur', 'technicien_intervenant']
    search_fields = ['description']
    ordering_fields = ['date_heure', 'cout', 'reduction_co2']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InterventionListSerializer
        return InterventionSerializer
    
    @action(detail=False, methods=['get'])
    def stats_impact_environnemental(self, request):
        """Statistiques sur l'impact environnemental des interventions"""
        stats = Intervention.objects.filter(
            statut='TERMINEE'
        ).aggregate(
            total_interventions=Count('id'),
            total_reduction_co2=Sum('reduction_co2'),
            cout_total=Sum('cout'),
            duree_moyenne=Avg('duree_minutes')
        )
        
        par_nature = Intervention.objects.filter(
            statut='TERMINEE'
        ).values('nature').annotate(
            count=Count('id'),
            reduction_co2=Sum('reduction_co2'),
            cout_moyen=Avg('cout')
        )
        
        return Response({
            'global': stats,
            'par_nature': list(par_nature)
        })
    
    @action(detail=False, methods=['get'])
    def interventions_predictives_mois(self, request):
        """
        Question 4: Combien d'interventions prédictives ont été réalisées 
        ce mois-ci, et quelle économie ont-elles générée?
        """
        from datetime import date
        
        # Début du mois actuel
        today = date.today()
        debut_mois = today.replace(day=1)
        
        # Filtrer les interventions prédictives terminées ce mois
        interventions = Intervention.objects.filter(
            nature='PREDICTIVE',
            statut='TERMINEE',
            date_heure__date__gte=debut_mois,
            date_heure__date__lte=today
        )
        
        stats = interventions.aggregate(
            nombre_interventions=Count('id'),
            economie_co2_totale=Sum('reduction_co2'),
            cout_total=Sum('cout'),
            duree_totale=Sum('duree_minutes'),
            cout_moyen=Avg('cout')
        )
        
        # Détails par semaine
        from django.db.models.functions import TruncWeek
        par_semaine = interventions.annotate(
            semaine=TruncWeek('date_heure')
        ).values('semaine').annotate(
            count=Count('id'),
            economie_co2=Sum('reduction_co2')
        ).order_by('semaine')
        
        return Response({
            'periode': f'{debut_mois.isoformat()} à {today.isoformat()}',
            'mois': today.strftime('%B %Y'),
            'statistiques': {
                'nombre_interventions': stats['nombre_interventions'] or 0,
                'economie_co2_kg': float(stats['economie_co2_totale'] or 0),
                'cout_total_tnd': float(stats['cout_total'] or 0),
                'duree_totale_minutes': stats['duree_totale'] or 0,
                'cout_moyen_tnd': float(stats['cout_moyen'] or 0)
            },
            'par_semaine': list(par_semaine)
        })


class CitoyenViewSet(viewsets.ModelViewSet):
    """ViewSet pour les citoyens"""
    queryset = Citoyen.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['preference_mobilite']
    search_fields = ['nom', 'prenom', 'email', 'identifiant_unique']
    ordering_fields = ['score_engagement', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CitoyenListSerializer
        return CitoyenSerializer
    
    @action(detail=False, methods=['get'])
    def top_engages(self, request):
        """Top 10 des citoyens les plus engagés"""
        limit = int(request.query_params.get('limit', 10))
        citoyens = Citoyen.objects.annotate(
            nombre_consultations=Count('consultations')
        ).order_by('-score_engagement')[:limit]
        
        data = [{
            'id': c.id,
            'identifiant': c.identifiant_unique,
            'nom_complet': f"{c.prenom} {c.nom}",
            'score_engagement': float(c.score_engagement),
            'preference_mobilite': c.preference_mobilite,
            'nombre_consultations': c.nombre_consultations
        } for c in citoyens]
        
        return Response(data)


class ConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les consultations"""
    queryset = Consultation.objects.select_related('citoyen')
    serializer_class = ConsultationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['citoyen', 'type_donnee', 'source_consultation']
    ordering_fields = ['timestamp']


class VehiculeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les véhicules"""
    queryset = Vehicule.objects.all()
    serializer_class = VehiculeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type', 'energie', 'statut']
    search_fields = ['plaque', 'marque', 'modele']


class TrajetViewSet(viewsets.ModelViewSet):
    """ViewSet pour les trajets avec analytics CO2"""
    queryset = Trajet.objects.select_related('vehicule')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicule', 'statut']
    search_fields = ['origine', 'destination']
    ordering_fields = ['depart', 'economie_co2', 'distance_km']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TrajetListSerializer
        return TrajetSerializer
    
    @action(detail=False, methods=['get'])
    def top_trajets_co2(self, request):
        """
        Endpoint: Quels trajets ont le plus réduit le CO2?
        Retourne les trajets classés par économie CO2
        """
        limit = int(request.query_params.get('limit', 20))
        
        trajets = Trajet.objects.filter(
            statut='TERMINE',
            economie_co2__isnull=False
        ).select_related('vehicule').order_by('-economie_co2')[:limit]
        
        data = [{
            'id': t.id,
            'vehicule_plaque': t.vehicule.plaque,
            'vehicule_type': t.vehicule.type,
            'vehicule_energie': t.vehicule.energie,
            'origine': t.origine,
            'destination': t.destination,
            'distance_km': float(t.distance_km) if t.distance_km else None,
            'economie_co2_kg': float(t.economie_co2),
            'nombre_passagers': t.nombre_passagers,
            'date': t.depart.date().isoformat()
        } for t in trajets]
        
        # Stats globales
        total_eco = Trajet.objects.filter(
            statut='TERMINE'
        ).aggregate(total=Sum('economie_co2'))['total'] or 0
        
        return Response({
            'total_economie_co2_kg': float(total_eco),
            'top_trajets': data
        })
    
    @action(detail=False, methods=['get'])
    def stats_par_vehicule(self, request):
        """Statistiques des trajets par véhicule"""
        stats = Vehicule.objects.annotate(
            nombre_trajets=Count('trajets', filter=Q(trajets__statut='TERMINE')),
            total_distance=Sum('trajets__distance_km', filter=Q(trajets__statut='TERMINE')),
            total_co2=Sum('trajets__economie_co2', filter=Q(trajets__statut='TERMINE')),
            total_passagers=Sum('trajets__nombre_passagers', filter=Q(trajets__statut='TERMINE'))
        ).filter(nombre_trajets__gt=0).order_by('-total_co2')
        
        data = [{
            'vehicule_id': v.id,
            'plaque': v.plaque,
            'type': v.type,
            'energie': v.energie,
            'nombre_trajets': v.nombre_trajets,
            'total_distance_km': float(v.total_distance) if v.total_distance else 0,
            'total_economie_co2_kg': float(v.total_co2) if v.total_co2 else 0,
            'total_passagers': v.total_passagers or 0
        } for v in stats]
        
        return Response(data)
