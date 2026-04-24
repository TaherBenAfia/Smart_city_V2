"""
Admin pour le module Rapports IA
"""

from django.contrib import admin
from .models import AIReport


@admin.register(AIReport)
class AIReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'date_range', 'generated_at']
    list_filter = ['report_type']
    ordering = ['-generated_at']
    readonly_fields = ['generated_at']
