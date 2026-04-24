"""
URL routes pour le module Rapports IA
"""

from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.ReportView.as_view(), name='ai-report'),
    path('suggest/', views.SuggestView.as_view(), name='ai-suggest'),
    path('history/', views.ReportHistoryView.as_view(), name='ai-history'),
]
