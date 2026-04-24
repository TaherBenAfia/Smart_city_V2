"""
Models pour le module Automates à États Finis
Stocke l'historique des transitions d'état pour chaque entité
"""

from django.db import models


class StateTransition(models.Model):
    """Historique des transitions d'état pour les automates"""

    ENTITY_TYPE_CHOICES = [
        ('capteur', 'Capteur'),
        ('intervention', 'Intervention'),
        ('vehicule', 'Véhicule'),
    ]

    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE_CHOICES,
        help_text="Type d'entité (capteur, intervention, vehicule)"
    )
    entity_id = models.CharField(
        max_length=50,
        help_text="ID de l'entité (UUID pour capteurs, int pour les autres)"
    )
    from_state = models.CharField(
        max_length=30,
        help_text="État avant la transition"
    )
    to_state = models.CharField(
        max_length=30,
        help_text="État après la transition"
    )
    event = models.CharField(
        max_length=50,
        help_text="Événement déclencheur"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Date/heure de la transition"
    )

    class Meta:
        db_table = 'state_transitions'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = 'Transition d\'état'
        verbose_name_plural = 'Transitions d\'état'

    def __str__(self):
        return (
            f"{self.entity_type}:{self.entity_id} "
            f"{self.from_state} → {self.to_state} "
            f"[{self.event}]"
        )
