"""
Admin para el módulo de Entidades
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    TipoPrestador, Departamento, Municipio,
    EntidadPrestadora, Sede, ServicioHabilitado,
    DocumentoEntidad, VigenciaHabilitacion
)


@admin.register(TipoPrestador)
class TipoPrestadorAdmin(admin.ModelAdmin):
    """Admin para tipos de prestador"""
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['nombre']


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    """Admin para departamentos"""
    list_display = ['codigo', 'nombre']
    search_fields = ['codigo', 'nombre']
    ordering = ['nombre']


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    """Admin para municipios"""
    list_display = ['codigo', 'nombre', 'departamento']
    list_filter = ['departamento']
    search_fields = ['codigo', 'nombre', 'departamento__nombre']
    ordering = ['departamento__nombre', 'nombre']
    autocomplete_fields = ['departamento']


class SedeInline(admin.TabularInline):
    """Inline para sedes dentro de entidad"""
    model = Sede
    extra = 0
    fields = ['nombre', 'tipo', 'codigo_reps_sede', 'municipio', 'activa']
    autocomplete_fields = ['municipio', 'departamento']


class DocumentoEntidadInline(admin.TabularInline):
    """Inline para documentos dentro de entidad"""
    model = DocumentoEntidad
    extra = 0
    fields = ['tipo', 'nombre', 'fecha_expedicion', 'fecha_vencimiento', 'archivo']


class VigenciaHabilitacionInline(admin.TabularInline):
    """Inline para vigencias dentro de entidad"""
    model = VigenciaHabilitacion
    extra = 0
    fields = ['fecha_inicio', 'fecha_fin', 'numero_resolucion', 'estado', 'porcentaje_cumplimiento']


@admin.register(EntidadPrestadora)
class EntidadPrestadoraAdmin(admin.ModelAdmin):
    """Admin para entidades prestadoras"""

    list_display = [
        'razon_social', 'nit_completo', 'tipo_prestador', 'codigo_reps',
        'municipio', 'estado', 'estado_habilitacion', 'fecha_vencimiento_habilitacion'
    ]
    list_filter = ['tipo_prestador', 'estado', 'departamento']
    search_fields = ['razon_social', 'nombre_comercial', 'nit', 'codigo_reps']
    date_hierarchy = 'fecha_creacion'
    ordering = ['razon_social']

    fieldsets = (
        ('Información Básica', {
            'fields': (
                'tipo_prestador',
                ('razon_social', 'nombre_comercial'),
                ('nit', 'digito_verificacion'),
                'codigo_reps',
                'logo'
            )
        }),
        ('Representante Legal', {
            'fields': (
                ('representante_legal', 'documento_representante'),
            )
        }),
        ('Ubicación', {
            'fields': (
                ('departamento', 'municipio'),
                'direccion',
                ('telefono', 'email'),
                'sitio_web'
            )
        }),
        ('Gestión', {
            'fields': (
                ('gerente', 'responsable_calidad'),
            )
        }),
        ('Estado y Vigencia', {
            'fields': (
                'estado',
                ('fecha_inscripcion_reps', 'fecha_vencimiento_habilitacion'),
            )
        }),
    )

    autocomplete_fields = ['departamento', 'municipio', 'tipo_prestador']
    inlines = [SedeInline, DocumentoEntidadInline, VigenciaHabilitacionInline]

    def nit_completo(self, obj):
        return obj.nit_completo
    nit_completo.short_description = 'NIT'

    def estado_habilitacion(self, obj):
        if obj.esta_vencida:
            return format_html('<span style="color: red; font-weight: bold;">VENCIDA</span>')
        elif obj.esta_por_vencer:
            return format_html('<span style="color: orange; font-weight: bold;">POR VENCER</span>')
        else:
            return format_html('<span style="color: green;">VIGENTE</span>')
    estado_habilitacion.short_description = 'Estado Hab.'


class ServicioHabilitadoInline(admin.TabularInline):
    """Inline para servicios dentro de sede"""
    model = ServicioHabilitado
    extra = 0
    fields = ['servicio', 'complejidad', 'modalidad', 'fecha_habilitacion', 'activo']
    autocomplete_fields = ['servicio']


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    """Admin para sedes"""

    list_display = ['nombre', 'entidad', 'tipo', 'codigo_reps_sede', 'municipio', 'activa']
    list_filter = ['tipo', 'activa', 'departamento', 'entidad']
    search_fields = ['nombre', 'codigo_reps_sede', 'entidad__razon_social']
    ordering = ['entidad__razon_social', 'nombre']

    fieldsets = (
        ('Información General', {
            'fields': (
                'entidad',
                ('nombre', 'tipo'),
                'codigo_reps_sede',
            )
        }),
        ('Ubicación', {
            'fields': (
                ('departamento', 'municipio'),
                'direccion',
                ('telefono', 'email'),
            )
        }),
        ('Responsables', {
            'fields': (
                ('director', 'responsable_sede'),
            )
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )

    autocomplete_fields = ['entidad', 'departamento', 'municipio']
    inlines = [ServicioHabilitadoInline]


@admin.register(ServicioHabilitado)
class ServicioHabilitadoAdmin(admin.ModelAdmin):
    """Admin para servicios habilitados"""

    list_display = ['servicio', 'sede', 'complejidad', 'modalidad', 'fecha_habilitacion', 'activo']
    list_filter = ['complejidad', 'modalidad', 'activo', 'sede__entidad']
    search_fields = ['servicio__nombre', 'sede__nombre', 'sede__entidad__razon_social']
    autocomplete_fields = ['sede', 'servicio']


@admin.register(DocumentoEntidad)
class DocumentoEntidadAdmin(admin.ModelAdmin):
    """Admin para documentos de entidad"""

    list_display = ['nombre', 'entidad', 'tipo', 'fecha_expedicion', 'fecha_vencimiento', 'estado_vencimiento']
    list_filter = ['tipo', 'entidad']
    search_fields = ['nombre', 'entidad__razon_social']
    date_hierarchy = 'fecha_expedicion'

    autocomplete_fields = ['entidad']

    def estado_vencimiento(self, obj):
        if obj.esta_vencido:
            return format_html('<span style="color: red;">VENCIDO</span>')
        dias = obj.dias_para_vencimiento
        if dias and dias <= 30:
            return format_html('<span style="color: orange;">Por vencer ({} días)</span>', dias)
        return format_html('<span style="color: green;">Vigente</span>')
    estado_vencimiento.short_description = 'Estado'


@admin.register(VigenciaHabilitacion)
class VigenciaHabilitacionAdmin(admin.ModelAdmin):
    """Admin para vigencias de habilitación"""

    list_display = ['entidad', 'fecha_inicio', 'fecha_fin', 'numero_resolucion', 'estado', 'porcentaje_cumplimiento']
    list_filter = ['estado', 'entidad']
    search_fields = ['entidad__razon_social', 'numero_resolucion']
    date_hierarchy = 'fecha_inicio'

    autocomplete_fields = ['entidad']
