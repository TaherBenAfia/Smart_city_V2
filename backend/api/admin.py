"""
Django Admin configuration pour Smart City Neo-Sousse 2030
"""

from django.contrib import admin
from .models import (
    Arrondissement, Proprietaire, Capteur, Mesure,
    Technicien, Intervention, Citoyen, Consultation,
    Vehicule, Trajet
)


@admin.register(Arrondissement)
class ArrondissementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code_postal', 'superficie_km2', 'population']
    search_fields = ['nom', 'code_postal']


@admin.register(Proprietaire)
class ProprietaireAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type', 'contact_email', 'contact_telephone']
    list_filter = ['type']
    search_fields = ['nom']


@admin.register(Capteur)
class CapteurAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'type', 'statut', 'arrondissement', 'date_installation']
    list_filter = ['type', 'statut', 'arrondissement']
    search_fields = ['uuid']
    date_hierarchy = 'date_installation'


@admin.register(Mesure)
class MesureAdmin(admin.ModelAdmin):
    list_display = ['id', 'capteur', 'timestamp', 'indice_pollution', 'qualite_air']
    list_filter = ['qualite_air', 'capteur__type']
    date_hierarchy = 'timestamp'


@admin.register(Technicien)
class TechnicienAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'nom', 'prenom', 'specialite', 'type_validation', 'actif']
    list_filter = ['type_validation', 'actif', 'specialite']
    search_fields = ['matricule', 'nom', 'prenom']


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['id', 'capteur', 'nature', 'statut', 'date_heure', 
                    'technicien_intervenant', 'technicien_validateur', 'cout']
    list_filter = ['nature', 'statut']
    search_fields = ['capteur__uuid', 'description']
    date_hierarchy = 'date_heure'
    autocomplete_fields = ['capteur', 'technicien_intervenant', 'technicien_validateur']


@admin.register(Citoyen)
class CitoyenAdmin(admin.ModelAdmin):
    list_display = ['identifiant_unique', 'nom', 'prenom', 'score_engagement', 'preference_mobilite']
    list_filter = ['preference_mobilite']
    search_fields = ['nom', 'prenom', 'email', 'identifiant_unique']
    ordering = ['-score_engagement']


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['citoyen', 'type_donnee', 'zone_consultee', 'timestamp', 'source_consultation']
    list_filter = ['type_donnee', 'source_consultation']
    date_hierarchy = 'timestamp'


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ['plaque', 'type', 'energie', 'marque', 'modele', 'statut']
    list_filter = ['type', 'energie', 'statut']
    search_fields = ['plaque', 'marque', 'modele']


@admin.register(Trajet)
class TrajetAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'origine', 'destination', 'depart', 'distance_km', 'economie_co2', 'statut']
    list_filter = ['statut', 'vehicule__type']
    search_fields = ['origine', 'destination']
    date_hierarchy = 'depart'
