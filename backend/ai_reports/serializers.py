"""
Serializers DRF pour le module Rapports IA
"""

from rest_framework import serializers
from .models import AIReport


class AIReportSerializer(serializers.ModelSerializer):
    """Serializer pour les rapports IA"""

    class Meta:
        model = AIReport
        fields = ['id', 'report_type', 'content', 'date_range', 'generated_at']
        read_only_fields = ['id', 'generated_at']


class ReportRequestSerializer(serializers.Serializer):
    """Serializer pour les requêtes de génération de rapport"""

    report_type = serializers.ChoiceField(
        choices=['air_quality', 'interventions', 'capteurs'],
        help_text="Type de rapport"
    )
    date = serializers.CharField(
        required=False,
        default='',
        help_text="Date du rapport (YYYY-MM-DD)"
    )


class SuggestRequestSerializer(serializers.Serializer):
    """Serializer pour les requêtes de suggestion"""

    capteur_id = serializers.CharField(
        help_text="UUID du capteur"
    )
