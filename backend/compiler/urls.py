"""
URL routes pour le module Compilateur NL → SQL
"""

from django.urls import path
from . import views

urlpatterns = [
    path('query/', views.CompilerQueryView.as_view(), name='compiler-query'),
]
