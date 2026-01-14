"""
Admin para el módulo SIAU
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import ConfiguracionSIAU, PQRS, EncuestaSatisfaccion


@admin.register(ConfiguracionSIAU)
class ConfiguracionSIAUAdmin(admin.ModelAdmin):
    """Admin para configuración SIAU"""

    list_display = ['entidad', 'telefono_atencion', 'email_atencion', 'responsable', 'activo']
    list_filter = ['activo']
    search_fields = ['entidad__razon_social']

    fieldsets = (
        ('Entidad', {
            'fields': ('entidad', 'activo')
        }),
        ('Contacto', {
            'fields': (
                'telefono_atencion',
                'email_atencion',
                'horario_atencion'
            )
        }),
        ('Responsable', {
            'fields': ('responsable',)
        }),
    )

    autocomplete_fields = ['entidad', 'responsable']


@admin.register(PQRS)
class PQRSAdmin(admin.ModelAdmin):
    """Admin para PQRS"""

    list_display = [
        'radicado', 'tipo', 'entidad', 'nombre_solicitante',
        'asunto_corto', 'estado_badge', 'fecha_radicacion', 'vencimiento_badge'
    ]
    list_filter = ['tipo', 'estado', 'entidad', 'sede']
    search_fields = ['radicado', 'nombre_solicitante', 'asunto', 'descripcion']
    date_hierarchy = 'fecha_radicacion'
    ordering = ['-fecha_radicacion']

    fieldsets = (
        ('Radicación', {
            'fields': ('entidad', 'sede', 'tipo', 'radicado')
        }),
        ('Solicitante', {
            'fields': (
                'nombre_solicitante',
                ('documento_solicitante', 'telefono_solicitante'),
                'email_solicitante'
            )
        }),
        ('Contenido', {
            'fields': ('asunto', 'descripcion', 'archivo_adjunto')
        }),
        ('Gestión', {
            'fields': (
                'estado',
                'fecha_vencimiento',
                'responsable'
            )
        }),
        ('Respuesta', {
            'fields': ('fecha_respuesta', 'respuesta'),
            'classes': ('collapse',)
        }),
    )

    autocomplete_fields = ['entidad', 'sede', 'responsable']

    def asunto_corto(self, obj):
        if len(obj.asunto) > 40:
            return obj.asunto[:40] + '...'
        return obj.asunto
    asunto_corto.short_description = 'Asunto'

    def estado_badge(self, obj):
        colores = {
            'RECIBIDA': 'gray',
            'EN_PROCESO': 'blue',
            'RESPONDIDA': 'green',
            'CERRADA': 'darkgreen'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def vencimiento_badge(self, obj):
        from django.utils import timezone

        if obj.estado in ['RESPONDIDA', 'CERRADA']:
            return format_html('<span style="color: green;">Cerrada</span>')

        hoy = timezone.now().date()
        if obj.fecha_vencimiento < hoy:
            return format_html('<span style="color: red; font-weight: bold;">VENCIDA</span>')

        dias = (obj.fecha_vencimiento - hoy).days
        if dias <= 3:
            return format_html('<span style="color: orange;">En {} días</span>', dias)

        return format_html('<span style="color: green;">{} días</span>', dias)
    vencimiento_badge.short_description = 'Vencimiento'


@admin.register(EncuestaSatisfaccion)
class EncuestaSatisfaccionAdmin(admin.ModelAdmin):
    """Admin para encuestas de satisfacción"""

    list_display = ['fecha', 'entidad', 'sede', 'servicio', 'calificacion_display']
    list_filter = ['calificacion_general', 'entidad', 'sede']
    search_fields = ['entidad__razon_social', 'comentarios']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']

    fieldsets = (
        ('Ubicación', {
            'fields': ('entidad', 'sede', 'servicio')
        }),
        ('Resultado', {
            'fields': ('calificacion_general', 'comentarios')
        }),
    )

    autocomplete_fields = ['entidad', 'sede', 'servicio']

    def calificacion_display(self, obj):
        estrellas = '★' * obj.calificacion_general + '☆' * (5 - obj.calificacion_general)
        color = 'green' if obj.calificacion_general >= 4 else 'orange' if obj.calificacion_general >= 3 else 'red'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, estrellas
        )
    calificacion_display.short_description = 'Calificación'
