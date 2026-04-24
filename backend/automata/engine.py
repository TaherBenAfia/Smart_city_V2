"""
Moteur d'Automates à États Finis (FSM Engine)
Implémente 3 automates déterministes pour la Smart City Neo-Sousse 2030:
  1. Cycle de vie des capteurs
  2. Validation des interventions
  3. Véhicule autonome
"""

from datetime import timedelta
from django.utils import timezone

from .models import StateTransition


# ============================================================================
# Définitions des automates (tables de transition)
# ============================================================================

# Chaque FSM est défini comme un dict:
#   { état_courant: { événement: état_suivant, ... }, ... }

CAPTEUR_FSM = {
    'name': 'Capteur Lifecycle',
    'initial_state': 'INACTIF',
    'states': ['INACTIF', 'ACTIF', 'SIGNALE', 'EN_MAINTENANCE', 'HORS_SERVICE'],
    'events': ['installation', 'detection_anomalie', 'reparation', 'panne'],
    'transitions': {
        'INACTIF': {
            'installation': 'ACTIF',
        },
        'ACTIF': {
            'detection_anomalie': 'SIGNALE',
            'panne': 'HORS_SERVICE',
        },
        'SIGNALE': {
            'reparation': 'EN_MAINTENANCE',
            'panne': 'HORS_SERVICE',
        },
        'EN_MAINTENANCE': {
            'reparation': 'ACTIF',
            'panne': 'HORS_SERVICE',
        },
        'HORS_SERVICE': {
            'reparation': 'EN_MAINTENANCE',
        },
    },
}

INTERVENTION_FSM = {
    'name': 'Intervention Validation',
    'initial_state': 'DEMANDE',
    'states': ['DEMANDE', 'TECH1_ASSIGNE', 'TECH2_VALIDE', 'IA_VALIDE', 'TERMINE'],
    'events': ['assigner_tech1', 'valider_tech2', 'valider_ia', 'terminer'],
    'transitions': {
        'DEMANDE': {
            'assigner_tech1': 'TECH1_ASSIGNE',
        },
        'TECH1_ASSIGNE': {
            'valider_tech2': 'TECH2_VALIDE',
        },
        'TECH2_VALIDE': {
            'valider_ia': 'IA_VALIDE',
        },
        'IA_VALIDE': {
            'terminer': 'TERMINE',
        },
        'TERMINE': {},
    },
}

VEHICULE_FSM = {
    'name': 'Véhicule Autonome',
    'initial_state': 'STATIONNE',
    'states': ['STATIONNE', 'EN_ROUTE', 'EN_PANNE', 'ARRIVE'],
    'events': ['demarrer', 'panne', 'reparer', 'arriver'],
    'transitions': {
        'STATIONNE': {
            'demarrer': 'EN_ROUTE',
        },
        'EN_ROUTE': {
            'panne': 'EN_PANNE',
            'arriver': 'ARRIVE',
        },
        'EN_PANNE': {
            'reparer': 'EN_ROUTE',
        },
        'ARRIVE': {
            'demarrer': 'EN_ROUTE',
        },
    },
}

# Registre des automates
FSM_REGISTRY = {
    'capteur': CAPTEUR_FSM,
    'intervention': INTERVENTION_FSM,
    'vehicule': VEHICULE_FSM,
}


# ============================================================================
# Classe moteur FSM
# ============================================================================

class FSMEngine:
    """
    Moteur d'automate à états finis réutilisable.
    Gère la validation, l'application et l'historique des transitions.
    """

    @staticmethod
    def get_fsm(entity_type):
        """Retourne la définition FSM pour un type d'entité."""
        fsm = FSM_REGISTRY.get(entity_type)
        if not fsm:
            raise ValueError(
                f"Type d'entité inconnu: '{entity_type}'. "
                f"Types valides: {list(FSM_REGISTRY.keys())}"
            )
        return fsm

    @staticmethod
    def get_current_state(entity_type, entity_id):
        """
        Retourne l'état courant d'une entité en lisant la dernière transition.
        Si aucune transition n'existe, retourne l'état initial de l'automate.
        """
        fsm = FSMEngine.get_fsm(entity_type)

        last_transition = StateTransition.objects.filter(
            entity_type=entity_type,
            entity_id=str(entity_id)
        ).order_by('-timestamp').first()

        if last_transition:
            return last_transition.to_state

        return fsm['initial_state']

    @staticmethod
    def validate_transition(entity_type, current_state, event):
        """
        Valide si une transition est possible.
        Retourne le nouvel état si valide, lève une exception sinon.
        """
        fsm = FSMEngine.get_fsm(entity_type)

        if current_state not in fsm['transitions']:
            raise ValueError(
                f"État '{current_state}' invalide pour l'automate '{fsm['name']}'. "
                f"États valides: {fsm['states']}"
            )

        transitions = fsm['transitions'][current_state]

        if event not in transitions:
            available_events = list(transitions.keys()) if transitions else []
            raise ValueError(
                f"Événement '{event}' non autorisé depuis l'état '{current_state}'. "
                f"Événements possibles: {available_events}"
            )

        return transitions[event]

    @staticmethod
    def apply_transition(entity_type, entity_id, event):
        """
        Applique une transition: valide, persiste, retourne le résultat.
        """
        current_state = FSMEngine.get_current_state(entity_type, entity_id)
        new_state = FSMEngine.validate_transition(entity_type, current_state, event)

        # Persister la transition
        transition = StateTransition.objects.create(
            entity_type=entity_type,
            entity_id=str(entity_id),
            from_state=current_state,
            to_state=new_state,
            event=event,
        )

        return {
            'entity_type': entity_type,
            'entity_id': str(entity_id),
            'from_state': current_state,
            'to_state': new_state,
            'event': event,
            'timestamp': transition.timestamp.isoformat(),
        }

    @staticmethod
    def get_history(entity_type, entity_id):
        """Retourne l'historique complet des transitions pour une entité."""
        FSMEngine.get_fsm(entity_type)  # Valide le type

        transitions = StateTransition.objects.filter(
            entity_type=entity_type,
            entity_id=str(entity_id)
        ).order_by('timestamp')

        return list(transitions.values(
            'id', 'from_state', 'to_state', 'event', 'timestamp'
        ))

    @staticmethod
    def check_alerts():
        """
        Vérifie les alertes automatiques:
        - Capteurs HORS_SERVICE depuis plus de 24h → log alert
        """
        alerts = []
        threshold = timezone.now() - timedelta(hours=24)

        # Trouver les capteurs dont la dernière transition est vers HORS_SERVICE
        # et dont le timestamp est > 24h
        from django.db.models import Max, Subquery, OuterRef

        # Dernière transition par capteur
        latest_transitions = StateTransition.objects.filter(
            entity_type='capteur'
        ).values('entity_id').annotate(
            last_ts=Max('timestamp')
        )

        for entry in latest_transitions:
            last = StateTransition.objects.filter(
                entity_type='capteur',
                entity_id=entry['entity_id'],
                timestamp=entry['last_ts']
            ).first()

            if last and last.to_state == 'HORS_SERVICE' and last.timestamp < threshold:
                hours = (timezone.now() - last.timestamp).total_seconds() / 3600
                alerts.append({
                    'entity_type': 'capteur',
                    'entity_id': last.entity_id,
                    'state': 'HORS_SERVICE',
                    'since': last.timestamp.isoformat(),
                    'hours_elapsed': round(hours, 1),
                    'message': (
                        f"ALERTE: Capteur {last.entity_id} est HORS_SERVICE "
                        f"depuis {round(hours, 1)}h (seuil: 24h)"
                    ),
                })

        return alerts

    @staticmethod
    def get_fsm_definition(entity_type):
        """Retourne la définition complète de l'automate pour affichage."""
        fsm = FSMEngine.get_fsm(entity_type)
        return {
            'name': fsm['name'],
            'entity_type': entity_type,
            'initial_state': fsm['initial_state'],
            'states': fsm['states'],
            'events': fsm['events'],
            'transitions': fsm['transitions'],
        }
