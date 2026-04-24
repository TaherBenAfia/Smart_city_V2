"""
Models pour le module Rapports IA
Stocke les rapports générés par l'IA
"""

from django.db import models


class AIReport(models.Model):
    """Rapports générés par l'intelligence artificielle"""

    REPORT_TYPE_CHOICES = [
        ('air_quality', 'Qualité de l\'air'),
        ('interventions', 'Interventions de maintenance'),
        ('capteurs', 'État des capteurs'),
    ]

    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        help_text="Type de rapport"
    )
    content = models.TextField(
        help_text="Contenu du rapport généré"
    )
    date_range = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Date ou plage de dates du rapport"
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date/heure de génération"
    )

    class Meta:
        db_table = 'ai_reports'
        ordering = ['-generated_at']
        verbose_name = 'Rapport IA'
        verbose_name_plural = 'Rapports IA'

    def __str__(self):
        return f"Rapport {self.get_report_type_display()} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"
