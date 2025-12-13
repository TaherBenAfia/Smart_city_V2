"""
URL routes pour l'API Smart City
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'arrondissements', views.ArrondissementViewSet)
router.register(r'proprietaires', views.ProprietaireViewSet)
router.register(r'capteurs', views.CapteurViewSet)
router.register(r'mesures', views.MesureViewSet)
router.register(r'techniciens', views.TechnicienViewSet)
router.register(r'interventions', views.InterventionViewSet)
router.register(r'citoyens', views.CitoyenViewSet)
router.register(r'consultations', views.ConsultationViewSet)
router.register(r'vehicules', views.VehiculeViewSet)
router.register(r'trajets', views.TrajetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
