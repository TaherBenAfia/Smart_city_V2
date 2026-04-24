"""
Serializers DRF pour le module Automates
"""

from rest_framework import serializers
from .models import StateTransition


class StateTransitionSerializer(serializers.ModelSerializer):
    """Serializer pour les transitions d'état"""

    class Meta:
        model = StateTransition
        fields = ['id', 'entity_type', 'entity_id', 'from_state',
                  'to_state', 'event', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class TransitionRequestSerializer(serializers.Serializer):
    """Serializer pour les requêtes de transition"""

    entity_type = serializers.ChoiceField(
        choices=['capteur', 'intervention', 'vehicule'],
        help_text="Type d'entité"
    )
    entity_id = serializers.CharField(
        max_length=50,
        help_text="ID de l'entité"
    )
    event = serializers.CharField(
        max_length=50,
        help_text="Événement déclencheur"
    )


class TransitionResponseSerializer(serializers.Serializer):
    """Serializer pour les réponses de transition"""

    entity_type = serializers.CharField()
    entity_id = serializers.CharField()
    from_state = serializers.CharField()
    to_state = serializers.CharField()
    event = serializers.CharField()
    timestamp = serializers.CharField()


class StateResponseSerializer(serializers.Serializer):
    """Serializer pour l'état courant"""

    entity_type = serializers.CharField()
    entity_id = serializers.CharField()
    current_state = serializers.CharField()
    fsm_definition = serializers.DictField()
