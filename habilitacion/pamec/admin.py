"""
Admin para el módulo PAMEC
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ProgramaPAMEC, CicloPHVA


class CicloPHVAInline(admin.TabularInline):
    """Inline para ciclos dentro de programa"""
    model = CicloPHVA
    extra = 0
    fields = ['fase', 'descripcion', 'fecha_inicio', 'fecha_fin', 'porcentaje_avance', 'responsable']


@admin.register(ProgramaPAMEC)
class ProgramaPAMECAdmin(admin.ModelAdmin):
    """Admin para programas PAMEC"""

    list_display = ['nombre', 'entidad', 'periodo', 'fecha_inicio', 'fecha_fin', 'estado_badge']
    list_filter = ['estado', 'entidad']
    search_fields = ['nombre', 'entidad__razon_social', 'periodo']
    date_hierarchy = 'fecha_inicio'

    fieldsets = (
        (None, {
            'fields': ('entidad', 'nombre', 'periodo')
        }),
        ('Período', {
            'fields': (('fecha_inicio', 'fecha_fin'),)
        }),
        ('Estado', {
            'fields': ('estado', 'observaciones')
        }),
    )

    autocomplete_fields = ['entidad']
    inlines = [CicloPHVAInline]

    def estado_badge(self, obj):
        colores = {
            'PLANIFICACION': 'gray',
            'EJECUCION': 'blue',
            'SEGUIMIENTO': 'orange',
            'FINALIZADO': 'green'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'


@admin.register(CicloPHVA)
class CicloPHVAAdmin(admin.ModelAdmin):
    """Admin para ciclos PHVA"""

    list_display = ['programa', 'fase', 'fecha_inicio', 'fecha_fin', 'avance_display', 'responsable']
    list_filter = ['fase', 'programa__entidad']
    search_fields = ['programa__nombre', 'descripcion']

    fieldsets = (
        (None, {
            'fields': ('programa', 'fase', 'descripcion')
        }),
        ('Período', {
            'fields': (('fecha_inicio', 'fecha_fin'),)
        }),
        ('Avance', {
            'fields': ('porcentaje_avance', 'responsable')
        }),
    )

    autocomplete_fields = ['programa', 'responsable']

    def avance_display(self, obj):
        color = 'green' if obj.porcentaje_avance >= 80 else 'orange' if obj.porcentaje_avance >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, obj.porcentaje_avance
        )
    avance_display.short_description = 'Avance'
