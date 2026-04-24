"""
API Views pour le module Automates à États Finis
Expose les endpoints pour gérer les transitions d'état
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .engine import FSMEngine, FSM_REGISTRY
from .serializers import TransitionRequestSerializer


class TransitionView(APIView):
    """
    POST /api/automata/transition/
    Applique un événement à une entité et retourne le nouvel état.

    Body: {"entity_type": "capteur", "entity_id": "abc-123", "event": "installation"}
    """

    def post(self, request):
        serializer = TransitionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            result = FSMEngine.apply_transition(
                entity_type=data['entity_type'],
                entity_id=data['entity_id'],
                event=data['event'],
            )
            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class StateView(APIView):
    """
    GET /api/automata/state/<entity_type>/<entity_id>/
    Retourne l'état courant d'une entité et la définition de son automate.
    """

    def get(self, request, entity_type, entity_id):
        try:
            current_state = FSMEngine.get_current_state(entity_type, entity_id)
            fsm_def = FSMEngine.get_fsm_definition(entity_type)

            return Response({
                'entity_type': entity_type,
                'entity_id': entity_id,
                'current_state': current_state,
                'fsm_definition': fsm_def,
            })

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class HistoryView(APIView):
    """
    GET /api/automata/history/<entity_type>/<entity_id>/
    Retourne l'historique complet des transitions pour une entité.
    """

    def get(self, request, entity_type, entity_id):
        try:
            history = FSMEngine.get_history(entity_type, entity_id)
            current_state = FSMEngine.get_current_state(entity_type, entity_id)

            return Response({
                'entity_type': entity_type,
                'entity_id': entity_id,
                'current_state': current_state,
                'transitions_count': len(history),
                'history': history,
            })

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AlertsView(APIView):
    """
    GET /api/automata/alerts/
    Retourne les alertes automatiques (capteurs HORS_SERVICE > 24h).
    """

    def get(self, request):
        alerts = FSMEngine.check_alerts()
        return Response({
            'alerts_count': len(alerts),
            'alerts': alerts,
        })


class FSMDefinitionsView(APIView):
    """
    GET /api/automata/definitions/
    Retourne les définitions de tous les automates disponibles.
    """

    def get(self, request):
        definitions = {}
        for entity_type in FSM_REGISTRY:
            definitions[entity_type] = FSMEngine.get_fsm_definition(entity_type)
        return Response(definitions)
