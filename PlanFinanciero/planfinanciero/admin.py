from django.contrib import admin
from .models import OrganoEjecutor, IngresoAgregado, TipoIngreso, Rubro, Movimiento, Vigencia


@admin.register(OrganoEjecutor)
class OrganoEjecutorAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['nombre']


@admin.register(IngresoAgregado)
class IngresoAgregadoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']


@admin.register(TipoIngreso)
class TipoIngresoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activo']
    list_filter = ['activo']
    search_fields = ['codigo', 'nombre']


@admin.register(Rubro)
class RubroAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'nivel', 'organo_ejecutor', 'ingreso_agregado', 'clase_ingreso', 'es_totalizador', 'activo']
    list_filter = ['nivel', 'organo_ejecutor', 'ingreso_agregado', 'clase_ingreso', 'tipo_ingreso', 'es_totalizador', 'activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'creado_por']
    raw_id_fields = ['padre']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'tipo', 'rubro', 'valor', 'documento_soporte', 'numero_ajuste', 'anulado']
    list_filter = ['tipo', 'anulado', 'fecha', 'numero_ajuste']
    search_fields = ['rubro__codigo', 'rubro__nombre', 'documento_soporte']
    date_hierarchy = 'fecha'
    ordering = ['-fecha', '-fecha_registro']
    readonly_fields = ['fecha_registro', 'registrado_por', 'fecha_anulacion', 'anulado_por']
    raw_id_fields = ['rubro']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Vigencia)
class VigenciaAdmin(admin.ModelAdmin):
    list_display = ['ano', 'activa', 'fecha_apertura', 'fecha_cierre']
    list_filter = ['activa']
    ordering = ['-ano']


admin.site.site_header = 'Plan Financiero - Administracion'
admin.site.site_title = 'Plan Financiero Admin'
admin.site.index_title = 'Panel de Administracion'
