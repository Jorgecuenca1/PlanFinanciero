"""
Admin para el módulo de Documentos
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ConfiguracionIA, PromptTemplate,
    SolicitudIA, NormativaReferencia
)


@admin.register(ConfiguracionIA)
class ConfiguracionIAAdmin(admin.ModelAdmin):
    """Admin para configuración de IA"""

    list_display = ['entidad', 'modelo_preferido', 'max_tokens', 'temperatura', 'activo']
    list_filter = ['activo', 'modelo_preferido']
    search_fields = ['entidad__razon_social']

    fieldsets = (
        ('Entidad', {
            'fields': ('entidad', 'activo')
        }),
        ('Configuración del Modelo', {
            'fields': (
                'modelo_preferido',
                ('max_tokens', 'temperatura'),
            )
        }),
        ('API Key', {
            'fields': ('api_key_personalizada',),
            'description': 'Opcional. Si no se especifica, usa la API Key global.',
            'classes': ('collapse',)
        }),
        ('Prompt del Sistema', {
            'fields': ('prompt_sistema',)
        }),
    )

    autocomplete_fields = ['entidad']


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    """Admin para plantillas de prompts"""

    list_display = ['nombre', 'tipo', 'es_global', 'entidad', 'estandar', 'activo']
    list_filter = ['tipo', 'es_global', 'activo']
    search_fields = ['nombre', 'descripcion', 'prompt']

    fieldsets = (
        (None, {
            'fields': ('nombre', 'tipo', 'descripcion')
        }),
        ('Prompt', {
            'fields': ('prompt',),
            'description': 'Usa {variables} para campos dinámicos: {criterio}, {entidad}, {servicio}'
        }),
        ('Asociación', {
            'fields': (
                ('estandar', 'criterio'),
            ),
            'classes': ('collapse',)
        }),
        ('Alcance', {
            'fields': (
                'es_global',
                'entidad',
            ),
            'description': 'Si es global, está disponible para todas las entidades.'
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

    autocomplete_fields = ['estandar', 'criterio', 'entidad']


@admin.register(SolicitudIA)
class SolicitudIAAdmin(admin.ModelAdmin):
    """Admin para solicitudes de IA"""

    list_display = [
        'id', 'usuario', 'entidad', 'estado_badge', 'modelo_usado',
        'tokens_total', 'costo_display', 'tiempo_display', 'fecha_solicitud'
    ]
    list_filter = ['estado', 'modelo_usado', 'entidad']
    search_fields = ['usuario__email', 'entidad__razon_social', 'prompt_enviado']
    date_hierarchy = 'fecha_solicitud'
    ordering = ['-fecha_solicitud']

    fieldsets = (
        ('Solicitud', {
            'fields': ('usuario', 'entidad', 'evaluacion', 'prompt_template')
        }),
        ('Contenido', {
            'fields': ('prompt_enviado', 'respuesta')
        }),
        ('Estado', {
            'fields': ('estado', 'mensaje_error')
        }),
        ('Métricas', {
            'fields': (
                'modelo_usado',
                ('tokens_prompt', 'tokens_respuesta', 'tokens_total'),
                ('costo_estimado', 'tiempo_procesamiento')
            )
        }),
        ('Fechas', {
            'fields': (('fecha_solicitud', 'fecha_respuesta'),),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = [
        'usuario', 'entidad', 'evaluacion', 'prompt_template',
        'prompt_enviado', 'respuesta', 'estado', 'mensaje_error',
        'modelo_usado', 'tokens_prompt', 'tokens_respuesta', 'tokens_total',
        'costo_estimado', 'tiempo_procesamiento', 'fecha_solicitud', 'fecha_respuesta'
    ]

    def estado_badge(self, obj):
        colores = {
            'PENDIENTE': 'gray',
            'PROCESANDO': 'blue',
            'COMPLETADA': 'green',
            'ERROR': 'red'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def costo_display(self, obj):
        if obj.costo_estimado:
            return f"${obj.costo_estimado:.6f}"
        return '-'
    costo_display.short_description = 'Costo'

    def tiempo_display(self, obj):
        if obj.tiempo_procesamiento:
            return f"{obj.tiempo_procesamiento:.2f}s"
        return '-'
    tiempo_display.short_description = 'Tiempo'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NormativaReferencia)
class NormativaReferenciaAdmin(admin.ModelAdmin):
    """Admin para normativas de referencia"""

    list_display = [
        'tipo', 'numero', 'anio', 'titulo_corto',
        'entidad_emisora', 'vigente', 'tiene_archivo'
    ]
    list_filter = ['tipo', 'vigente', 'anio', 'entidad_emisora']
    search_fields = ['numero', 'titulo', 'resumen', 'contenido_completo']
    date_hierarchy = 'fecha_expedicion'

    fieldsets = (
        ('Identificación', {
            'fields': (
                'tipo',
                ('numero', 'anio'),
                'titulo',
                'entidad_emisora',
                'fecha_expedicion',
                'vigente'
            )
        }),
        ('Contenido', {
            'fields': ('resumen', 'contenido_completo')
        }),
        ('Archivos', {
            'fields': ('archivo', 'url_oficial')
        }),
        ('Relaciones', {
            'fields': ('estandares_relacionados',),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ['estandares_relacionados']

    def titulo_corto(self, obj):
        if len(obj.titulo) > 60:
            return obj.titulo[:60] + '...'
        return obj.titulo
    titulo_corto.short_description = 'Título'

    def tiene_archivo(self, obj):
        return bool(obj.archivo)
    tiene_archivo.boolean = True
    tiene_archivo.short_description = 'Archivo'
