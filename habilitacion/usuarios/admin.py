"""
Admin para el módulo de Usuarios
Sistema de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Usuario, RegistroActividad


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para el modelo Usuario"""

    list_display = [
        'email', 'nombre_completo', 'rol', 'entidad', 'is_active', 'fecha_ultimo_acceso'
    ]
    list_filter = ['rol', 'is_active', 'is_staff', 'entidad']
    search_fields = ['email', 'primer_nombre', 'primer_apellido', 'documento_identidad']
    ordering = ['primer_apellido', 'primer_nombre']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {
            'fields': (
                ('primer_nombre', 'segundo_nombre'),
                ('primer_apellido', 'segundo_apellido'),
                'documento_identidad',
                'telefono',
                'cargo',
                'foto'
            )
        }),
        ('Rol y Entidad', {
            'fields': ('rol', 'entidad', 'sedes')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_ultimo_acceso'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'primer_nombre', 'primer_apellido',
                'rol', 'entidad', 'is_active'
            ),
        }),
    )

    readonly_fields = ['fecha_ultimo_acceso', 'last_login', 'date_joined']
    filter_horizontal = ['groups', 'user_permissions', 'sedes']


@admin.register(RegistroActividad)
class RegistroActividadAdmin(admin.ModelAdmin):
    """Admin para el registro de actividades"""

    list_display = ['fecha', 'usuario', 'tipo', 'modelo_afectado', 'descripcion_corta', 'ip_address']
    list_filter = ['tipo', 'modelo_afectado', 'fecha']
    search_fields = ['usuario__email', 'descripcion', 'ip_address']
    date_hierarchy = 'fecha'
    ordering = ['-fecha']

    readonly_fields = [
        'usuario', 'tipo', 'descripcion', 'modelo_afectado', 'objeto_id',
        'datos_anteriores', 'datos_nuevos', 'ip_address', 'user_agent', 'fecha'
    ]

    def descripcion_corta(self, obj):
        if len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
