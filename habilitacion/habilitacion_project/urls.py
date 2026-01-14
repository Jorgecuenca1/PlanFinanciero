"""
URL configuration for habilitacion_project project.
Sistema de Gestión de Habilitación de Servicios de Salud
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Configuración del sitio admin
admin.site.site_header = 'Sistema de Habilitación'
admin.site.site_title = 'Habilitación Admin'
admin.site.index_title = 'Administración del Sistema'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('entidades/', include('entidades.urls')),
    path('estandares/', include('estandares.urls')),
    path('evaluacion/', include('evaluacion.urls')),
    path('documentos/', include('documentos.urls')),
    path('reportes/', include('reportes.urls')),
    path('pamec/', include('pamec.urls')),
    path('siau/', include('siau.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
