"""
Context processors globales para el sistema de habilitación.
"""

from django.conf import settings


def global_settings(request):
    """
    Añade configuraciones globales al contexto de todos los templates.
    """
    context = {
        'SISTEMA_NOMBRE': 'Sistema de Habilitación de Servicios de Salud',
        'SISTEMA_VERSION': '1.0.0',
        'RESOLUCION': 'Resolución 3100 de 2019',
        'HABILITACION_CONFIG': settings.HABILITACION_CONFIG,
    }

    # Añadir información del usuario actual
    if request.user.is_authenticated:
        context['entidad_actual'] = getattr(request.user, 'entidad', None)
        context['sedes_usuario'] = request.user.sedes.all() if hasattr(request.user, 'sedes') else []

    return context
