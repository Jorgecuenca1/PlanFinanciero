"""
Admin para el módulo de Evaluación
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Evaluacion, DocumentoEvaluacion, HistorialEvaluacion,
    PeriodoEvaluacion, ResumenCumplimiento
)


class DocumentoEvaluacionInline(admin.TabularInline):
    """Inline para documentos dentro de evaluación"""
    model = DocumentoEvaluacion
    extra = 0
    fields = ['nombre', 'version', 'es_version_final', 'generado_con_ia', 'archivo']
    readonly_fields = ['version']


class HistorialEvaluacionInline(admin.TabularInline):
    """Inline para historial dentro de evaluación"""
    model = HistorialEvaluacion
    extra = 0
    fields = ['fecha', 'usuario', 'accion', 'descripcion']
    readonly_fields = ['fecha', 'usuario', 'accion', 'descripcion']
    ordering = ['-fecha']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    """Admin para evaluaciones"""

    list_display = [
        'sede', 'criterio_display', 'estado_badge', 'estado_documento_badge',
        'responsable_desarrollo', 'fecha_modificacion'
    ]
    list_filter = ['estado', 'estado_documento', 'sede__entidad', 'sede']
    search_fields = [
        'sede__nombre', 'sede__entidad__razon_social',
        'criterio__numero', 'criterio__texto'
    ]
    date_hierarchy = 'fecha_modificacion'
    ordering = ['-fecha_modificacion']

    fieldsets = (
        ('Identificación', {
            'fields': ('sede', 'criterio', 'servicio_habilitado')
        }),
        ('Estado', {
            'fields': (
                ('estado', 'estado_documento'),
                'justificacion_na',
                'comentarios'
            )
        }),
        ('Responsables', {
            'fields': (
                'responsable_desarrollo',
                'responsable_calidad',
                'responsable_aprobacion'
            )
        }),
        ('Fechas', {
            'fields': (
                ('fecha_evaluacion', 'fecha_aprobacion'),
                'fecha_vencimiento'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'fecha_creacion', 'fecha_modificacion', 'modificado_por'
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    autocomplete_fields = ['sede', 'criterio', 'servicio_habilitado']
    inlines = [DocumentoEvaluacionInline, HistorialEvaluacionInline]

    def criterio_display(self, obj):
        texto = obj.criterio.texto
        if len(texto) > 50:
            texto = texto[:50] + '...'
        return f"{obj.criterio.numero}: {texto}"
    criterio_display.short_description = 'Criterio'

    def estado_badge(self, obj):
        colores = {
            'C': 'green',
            'NC': 'red',
            'NA': 'gray',
            'PE': 'orange'
        }
        color = colores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'

    def estado_documento_badge(self, obj):
        colores = {
            'NT': 'gray',
            'ED': 'blue',
            'AP': 'green'
        }
        color = colores.get(obj.estado_documento, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_estado_documento_display()
        )
    estado_documento_badge.short_description = 'Doc.'


@admin.register(DocumentoEvaluacion)
class DocumentoEvaluacionAdmin(admin.ModelAdmin):
    """Admin para documentos de evaluación"""

    list_display = [
        'nombre', 'evaluacion', 'version', 'es_version_final',
        'generado_con_ia', 'tiene_archivo', 'fecha_modificacion'
    ]
    list_filter = ['es_version_final', 'generado_con_ia', 'evaluacion__sede__entidad']
    search_fields = ['nombre', 'descripcion', 'evaluacion__criterio__numero']
    date_hierarchy = 'fecha_creacion'

    fieldsets = (
        (None, {
            'fields': ('evaluacion', 'nombre', 'descripcion')
        }),
        ('Contenido', {
            'fields': ('contenido_html', 'archivo')
        }),
        ('Versión', {
            'fields': ('version', 'es_version_final')
        }),
        ('IA', {
            'fields': ('generado_con_ia', 'prompt_ia'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['version']
    autocomplete_fields = ['evaluacion']

    def tiene_archivo(self, obj):
        return bool(obj.archivo)
    tiene_archivo.boolean = True
    tiene_archivo.short_description = 'Archivo'


@admin.register(HistorialEvaluacion)
class HistorialEvaluacionAdmin(admin.ModelAdmin):
    """Admin para historial de evaluaciones"""

    list_display = ['fecha', 'evaluacion', 'usuario', 'accion', 'descripcion_corta']
    list_filter = ['accion', 'fecha']
    search_fields = ['evaluacion__criterio__numero', 'usuario__email', 'descripcion']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']

    readonly_fields = [
        'evaluacion', 'usuario', 'accion', 'descripcion',
        'estado_anterior', 'estado_nuevo', 'datos_adicionales', 'fecha'
    ]

    def descripcion_corta(self, obj):
        if len(obj.descripcion) > 60:
            return obj.descripcion[:60] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ResumenCumplimientoInline(admin.TabularInline):
    """Inline para resúmenes dentro de período"""
    model = ResumenCumplimiento
    extra = 0
    fields = [
        'sede', 'grupo_estandar', 'estandar', 'total_criterios',
        'criterios_cumple', 'criterios_no_cumple', 'porcentaje_cumplimiento'
    ]
    readonly_fields = fields


@admin.register(PeriodoEvaluacion)
class PeriodoEvaluacionAdmin(admin.ModelAdmin):
    """Admin para períodos de evaluación"""

    list_display = [
        'nombre', 'entidad', 'fecha_inicio', 'fecha_fin',
        'porcentaje_cumplimiento_general', 'activo'
    ]
    list_filter = ['activo', 'entidad']
    search_fields = ['nombre', 'entidad__razon_social']
    date_hierarchy = 'fecha_inicio'

    fieldsets = (
        (None, {
            'fields': ('entidad', 'nombre', 'activo')
        }),
        ('Período', {
            'fields': (('fecha_inicio', 'fecha_fin'),)
        }),
        ('Resultados', {
            'fields': ('porcentaje_cumplimiento_general', 'observaciones')
        }),
    )

    autocomplete_fields = ['entidad']
    inlines = [ResumenCumplimientoInline]

    actions = ['calcular_cumplimiento']

    @admin.action(description='Calcular porcentaje de cumplimiento')
    def calcular_cumplimiento(self, request, queryset):
        for periodo in queryset:
            periodo.calcular_porcentaje_cumplimiento()
        self.message_user(request, f'Se calculó el cumplimiento para {queryset.count()} período(s).')


@admin.register(ResumenCumplimiento)
class ResumenCumplimientoAdmin(admin.ModelAdmin):
    """Admin para resúmenes de cumplimiento"""

    list_display = [
        'sede', 'referencia', 'total_criterios', 'criterios_cumple',
        'criterios_no_cumple', 'porcentaje_display', 'fecha_calculo'
    ]
    list_filter = ['sede__entidad', 'grupo_estandar']
    search_fields = ['sede__nombre', 'sede__entidad__razon_social']

    readonly_fields = [
        'total_criterios', 'criterios_cumple', 'criterios_no_cumple',
        'criterios_no_aplica', 'criterios_pendientes', 'porcentaje_cumplimiento',
        'fecha_calculo'
    ]

    autocomplete_fields = ['sede', 'periodo', 'grupo_estandar', 'estandar', 'servicio']

    def referencia(self, obj):
        return obj.grupo_estandar or obj.estandar or obj.servicio or '-'
    referencia.short_description = 'Grupo/Estándar'

    def porcentaje_display(self, obj):
        color = 'green' if obj.porcentaje_cumplimiento >= 80 else 'orange' if obj.porcentaje_cumplimiento >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, obj.porcentaje_cumplimiento
        )
    porcentaje_display.short_description = '% Cumpl.'

    actions = ['recalcular']

    @admin.action(description='Recalcular resúmenes seleccionados')
    def recalcular(self, request, queryset):
        for resumen in queryset:
            resumen.calcular()
        self.message_user(request, f'Se recalcularon {queryset.count()} resúmenes.')
