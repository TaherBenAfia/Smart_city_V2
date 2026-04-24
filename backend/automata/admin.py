"""
Admin pour le module Automates
"""

from django.contrib import admin
from .models import StateTransition


@admin.register(StateTransition)
class StateTransitionAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'entity_id', 'from_state', 'to_state', 'event', 'timestamp']
    list_filter = ['entity_type', 'from_state', 'to_state', 'event']
    search_fields = ['entity_id']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
