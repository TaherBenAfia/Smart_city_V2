"""
URL routes pour le module Automates
"""

from django.urls import path
from . import views

urlpatterns = [
    path('transition/', views.TransitionView.as_view(), name='automata-transition'),
    path('state/<str:entity_type>/<str:entity_id>/', views.StateView.as_view(), name='automata-state'),
    path('history/<str:entity_type>/<str:entity_id>/', views.HistoryView.as_view(), name='automata-history'),
    path('alerts/', views.AlertsView.as_view(), name='automata-alerts'),
    path('definitions/', views.FSMDefinitionsView.as_view(), name='automata-definitions'),
]
