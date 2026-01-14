"""
Admin para el módulo de Estándares
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from .models import (
    GrupoEstandar, Estandar, Servicio,
    EstandarServicio, Criterio, PlantillaDocumento
)


class EstandarInline(admin.TabularInline):
    """Inline para estándares dentro de grupo"""
    model = Estandar
    extra = 0
    fields = ['codigo', 'codigo_corto', 'nombre', 'orden', 'activo']
    ordering = ['orden', 'codigo']


@admin.register(GrupoEstandar)
class GrupoEstandarAdmin(admin.ModelAdmin):
    """Admin para grupos de estándares"""

    list_display = ['codigo', 'nombre', 'aplica_todos', 'orden', 'total_estandares', 'activo']
    list_filter = ['aplica_todos', 'activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['orden', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('aplica_todos', 'orden', 'activo')
        }),
    )

    inlines = [EstandarInline]

    def total_estandares(self, obj):
        return obj.estandares.count()
    total_estandares.short_description = 'Estándares'


class CriterioInline(admin.TabularInline):
    """Inline para criterios dentro de estándar"""
    model = Criterio
    extra = 0
    fields = ['numero', 'texto', 'es_titulo', 'orden', 'activo']
    ordering = ['orden', 'numero']


@admin.register(Estandar)
class EstandarAdmin(admin.ModelAdmin):
    """Admin para estándares"""

    list_display = ['codigo', 'nombre', 'grupo', 'total_criterios', 'orden', 'activo']
    list_filter = ['grupo', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['grupo__orden', 'orden', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('grupo', 'codigo', 'codigo_corto', 'nombre', 'descripcion')
        }),
        ('Referencia', {
            'fields': ('paginas_resolucion',),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('orden', 'activo')
        }),
    )

    autocomplete_fields = ['grupo']
    inlines = [CriterioInline]

    def total_criterios(self, obj):
        return obj.total_criterios
    total_criterios.short_description = 'Criterios'


class EstandarServicioInline(admin.TabularInline):
    """Inline para estándares de servicio"""
    model = EstandarServicio
    extra = 0
    fields = ['tipo', 'codigo', 'descripcion', 'orden', 'activo']
    ordering = ['orden']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    """Admin para servicios"""

    list_display = ['codigo', 'nombre', 'grupo', 'codigo_hoja_excel', 'orden', 'activo']
    list_filter = ['grupo', 'activo']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['grupo__orden', 'orden', 'codigo']

    fieldsets = (
        (None, {
            'fields': ('grupo', 'codigo', 'nombre', 'descripcion')
        }),
        ('Referencia Excel', {
            'fields': ('codigo_hoja_excel',),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('orden', 'activo')
        }),
    )

    autocomplete_fields = ['grupo']
    inlines = [EstandarServicioInline]


class CriterioServicioInline(admin.TabularInline):
    """Inline para criterios de estándar de servicio"""
    model = Criterio
    fk_name = 'estandar_servicio'
    extra = 0
    fields = ['numero', 'texto', 'es_titulo', 'orden', 'activo']
    ordering = ['orden', 'numero']


@admin.register(EstandarServicio)
class EstandarServicioAdmin(admin.ModelAdmin):
    """Admin para estándares de servicio"""

    list_display = ['codigo', 'servicio', 'tipo', 'total_criterios', 'orden', 'activo']
    list_filter = ['tipo', 'servicio__grupo', 'activo']
    search_fields = ['codigo', 'servicio__nombre', 'descripcion']
    ordering = ['servicio__orden', 'orden']

    autocomplete_fields = ['servicio']
    inlines = [CriterioServicioInline]

    def total_criterios(self, obj):
        return obj.criterios.count()
    total_criterios.short_description = 'Criterios'


class PlantillaDocumentoInline(admin.TabularInline):
    """Inline para plantillas dentro de criterio"""
    model = PlantillaDocumento
    extra = 0
    fields = ['nombre', 'descripcion', 'es_ejemplo', 'archivo_plantilla']


@admin.register(Criterio)
class CriterioAdmin(admin.ModelAdmin):
    """Admin para criterios"""

    list_display = ['numero', 'texto_corto', 'estandar_padre', 'es_titulo', 'orden', 'activo']
    list_filter = ['es_titulo', 'activo', 'estandar__grupo', 'estandar']
    search_fields = ['numero', 'texto']
    ordering = ['orden', 'numero']

    fieldsets = (
        ('Pertenece a', {
            'fields': ('estandar', 'estandar_servicio'),
            'description': 'Seleccione UN solo tipo: estándar general O estándar de servicio'
        }),
        ('Contenido', {
            'fields': ('numero', 'texto', 'es_titulo')
        }),
        ('Aplicabilidad', {
            'fields': ('complejidad_aplica', 'modalidad_aplica', 'observaciones'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('orden', 'activo')
        }),
    )

    autocomplete_fields = ['estandar', 'estandar_servicio']
    inlines = [PlantillaDocumentoInline]

    def texto_corto(self, obj):
        if len(obj.texto) > 80:
            return obj.texto[:80] + '...'
        return obj.texto
    texto_corto.short_description = 'Texto'

    def estandar_padre(self, obj):
        return obj.estandar_padre
    estandar_padre.short_description = 'Estándar'


@admin.register(PlantillaDocumento)
class PlantillaDocumentoAdmin(admin.ModelAdmin):
    """Admin para plantillas de documentos"""

    list_display = ['nombre', 'criterio', 'es_ejemplo', 'tiene_archivo', 'fecha_modificacion']
    list_filter = ['es_ejemplo', 'criterio__estandar']
    search_fields = ['nombre', 'descripcion', 'criterio__numero']
    date_hierarchy = 'fecha_creacion'

    autocomplete_fields = ['criterio']

    def tiene_archivo(self, obj):
        return bool(obj.archivo_plantilla)
    tiene_archivo.boolean = True
    tiene_archivo.short_description = 'Archivo'
