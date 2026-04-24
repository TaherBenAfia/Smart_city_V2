"""
API Views pour le module Rapports IA
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import AIReport
from .serializers import ReportRequestSerializer, SuggestRequestSerializer
from .data_service import DataService
from .llm_service import LLMService


class ReportView(APIView):
    """
    POST /api/ai/report/
    Génère un rapport IA basé sur les données réelles.

    Body: {"report_type": "air_quality", "date": "2026-03-15"}
    """

    def post(self, request):
        serializer = ReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        report_type = serializer.validated_data['report_type']
        date_str = serializer.validated_data.get('date', '')

        try:
            # 1. Récupérer les données agrégées
            if report_type == 'air_quality':
                data_context = DataService.get_air_quality_data(date_str)
            elif report_type == 'interventions':
                data_context = DataService.get_interventions_data(date_str)
            elif report_type == 'capteurs':
                data_context = DataService.get_capteurs_data(date_str)
            else:
                return Response(
                    {'error': f"Type de rapport '{report_type}' non supporté."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Générer le rapport via LLM
            llm = LLMService()
            content = llm.generate_report(report_type, data_context)

            # 3. Sauvegarder en base
            report = AIReport.objects.create(
                report_type=report_type,
                content=content,
                date_range=date_str or None,
            )

            return Response({
                'id': report.id,
                'report_type': report_type,
                'content': content,
                'generated_at': report.generated_at.isoformat(),
                'mode': llm.mode,
                'data_context': data_context,
            })

        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SuggestView(APIView):
    """
    POST /api/ai/suggest/
    Génère une suggestion d'action pour un capteur spécifique.

    Body: {"capteur_id": "abc-123-uuid"}
    """

    def post(self, request):
        serializer = SuggestRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        capteur_id = serializer.validated_data['capteur_id']

        try:
            # 1. Récupérer les données du capteur
            capteur_data = DataService.get_capteur_detail(capteur_id)

            if not capteur_data:
                return Response(
                    {'error': f"Capteur '{capteur_id}' non trouvé."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 2. Générer la suggestion
            llm = LLMService()
            suggestion = llm.generate_suggestion(capteur_data)

            return Response({
                'capteur_id': capteur_id,
                'suggestion': suggestion,
                'mode': llm.mode,
                'capteur_data': capteur_data,
            })

        except Exception as e:
            return Response(
                {'error': f'Erreur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportHistoryView(APIView):
    """
    GET /api/ai/history/
    Retourne l'historique des rapports générés.
    """

    def get(self, request):
        reports = AIReport.objects.all()[:20]
        data = [
            {
                'id': r.id,
                'report_type': r.report_type,
                'date_range': r.date_range,
                'generated_at': r.generated_at.isoformat(),
                'content_preview': r.content[:200] + '...' if len(r.content) > 200 else r.content,
            }
            for r in reports
        ]
        return Response({
            'count': len(data),
            'reports': data,
        })
