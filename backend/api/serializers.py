"""
Serializers DRF pour Smart City Neo-Sousse 2030
"""

from rest_framework import serializers
from .models import (
    Arrondissement, Proprietaire, Capteur, Mesure,
    Technicien, Intervention, Citoyen, Consultation,
    Vehicule, Trajet
)


class ArrondissementSerializer(serializers.ModelSerializer):
    """Serializer pour les arrondissements"""
    nombre_capteurs = serializers.SerializerMethodField()
    
    class Meta:
        model = Arrondissement
        fields = '__all__'
    
    def get_nombre_capteurs(self, obj):
        return obj.capteurs.count()


class ProprietaireSerializer(serializers.ModelSerializer):
    """Serializer pour les propriétaires de capteurs"""
    nombre_capteurs = serializers.SerializerMethodField()
    
    class Meta:
        model = Proprietaire
        fields = '__all__'
    
    def get_nombre_capteurs(self, obj):
        return obj.capteurs.count()


class CapteurListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des capteurs"""
    arrondissement_nom = serializers.CharField(source='arrondissement.nom', read_only=True)
    proprietaire_nom = serializers.CharField(source='proprietaire.nom', read_only=True)
    
    class Meta:
        model = Capteur
        fields = ['uuid', 'type', 'statut', 'latitude', 'longitude', 
                  'date_installation', 'arrondissement_nom', 'proprietaire_nom']


class CapteurSerializer(serializers.ModelSerializer):
    """Serializer complet pour les capteurs"""
    arrondissement_nom = serializers.CharField(source='arrondissement.nom', read_only=True)
    proprietaire_nom = serializers.CharField(source='proprietaire.nom', read_only=True)
    nombre_mesures = serializers.SerializerMethodField()
    nombre_interventions = serializers.SerializerMethodField()
    
    class Meta:
        model = Capteur
        fields = '__all__'
    
    def get_nombre_mesures(self, obj):
        return obj.mesures.count()
    
    def get_nombre_interventions(self, obj):
        return obj.interventions.count()


class MesureSerializer(serializers.ModelSerializer):
    """Serializer pour les mesures"""
    capteur_type = serializers.CharField(source='capteur.type', read_only=True)
    
    class Meta:
        model = Mesure
        fields = '__all__'


class TechnicienSerializer(serializers.ModelSerializer):
    """Serializer pour les techniciens"""
    nom_complet = serializers.ReadOnlyField()
    interventions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Technicien
        fields = '__all__'
    
    def get_interventions_count(self, obj):
        return obj.interventions_effectuees.count() + obj.interventions_validees.count()


class InterventionListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des interventions"""
    capteur_type = serializers.CharField(source='capteur.type', read_only=True)
    capteur_arrondissement = serializers.CharField(source='capteur.arrondissement.nom', read_only=True)
    intervenant_nom = serializers.CharField(source='technicien_intervenant.nom_complet', read_only=True)
    validateur_nom = serializers.CharField(source='technicien_validateur.nom_complet', read_only=True)
    
    class Meta:
        model = Intervention
        fields = ['id', 'date_heure', 'nature', 'statut', 'duree_minutes', 'cout',
                  'reduction_co2', 'capteur_type', 'capteur_arrondissement',
                  'intervenant_nom', 'validateur_nom']


class InterventionSerializer(serializers.ModelSerializer):
    """Serializer complet pour les interventions avec validation 2 techniciens"""
    capteur_type = serializers.CharField(source='capteur.type', read_only=True)
    intervenant_nom = serializers.CharField(source='technicien_intervenant.nom_complet', read_only=True)
    validateur_nom = serializers.CharField(source='technicien_validateur.nom_complet', read_only=True)
    
    class Meta:
        model = Intervention
        fields = '__all__'
    
    def validate(self, data):
        """Validation: les deux techniciens doivent être différents"""
        intervenant = data.get('technicien_intervenant')
        validateur = data.get('technicien_validateur')
        
        if intervenant and validateur and intervenant.id == validateur.id:
            raise serializers.ValidationError({
                'technicien_validateur': "L'intervenant et le validateur doivent être différents."
            })
        return data


class CitoyenListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des citoyens"""
    nom_complet = serializers.SerializerMethodField()
    
    class Meta:
        model = Citoyen
        fields = ['id', 'identifiant_unique', 'nom_complet', 'email', 
                  'score_engagement', 'preference_mobilite']
    
    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"


class CitoyenSerializer(serializers.ModelSerializer):
    """Serializer complet pour les citoyens"""
    nombre_consultations = serializers.SerializerMethodField()
    
    class Meta:
        model = Citoyen
        fields = '__all__'
    
    def get_nombre_consultations(self, obj):
        return obj.consultations.count()


class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer pour les consultations"""
    citoyen_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = '__all__'
    
    def get_citoyen_nom(self, obj):
        return f"{obj.citoyen.prenom} {obj.citoyen.nom}"


class VehiculeSerializer(serializers.ModelSerializer):
    """Serializer pour les véhicules"""
    nombre_trajets = serializers.SerializerMethodField()
    total_economie_co2 = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicule
        fields = '__all__'
    
    def get_nombre_trajets(self, obj):
        return obj.trajets.filter(statut='TERMINE').count()
    
    def get_total_economie_co2(self, obj):
        from django.db.models import Sum
        result = obj.trajets.filter(statut='TERMINE').aggregate(total=Sum('economie_co2'))
        return result['total'] or 0


class TrajetListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des trajets"""
    vehicule_plaque = serializers.CharField(source='vehicule.plaque', read_only=True)
    vehicule_type = serializers.CharField(source='vehicule.type', read_only=True)
    duree_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Trajet
        fields = ['id', 'vehicule_plaque', 'vehicule_type', 'origine', 'destination',
                  'depart', 'arrivee', 'distance_km', 'economie_co2', 'duree_minutes', 'statut']


class TrajetSerializer(serializers.ModelSerializer):
    """Serializer complet pour les trajets"""
    vehicule_info = VehiculeSerializer(source='vehicule', read_only=True)
    duree_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Trajet
        fields = '__all__'
