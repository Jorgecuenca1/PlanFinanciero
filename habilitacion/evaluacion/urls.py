"""URLs del módulo evaluación"""
from django.urls import path
from . import views

app_name = 'evaluacion'

urlpatterns = [
    # ===== VIGENCIAS/PERÍODOS =====
    path('vigencias/', views.lista_vigencias, name='lista_vigencias'),
    path('vigencias/nueva/', views.crear_vigencia, name='crear_vigencia'),
    path('vigencias/<int:pk>/', views.detalle_vigencia, name='detalle_vigencia'),
    path('vigencias/<int:pk>/editar/', views.editar_vigencia, name='editar_vigencia'),

    # ===== EVALUACIONES LEGACY (mantener por compatibilidad) =====
    path('lista/', views.lista_evaluaciones, name='lista'),
    path('sede-legacy/<int:sede_pk>/', views.evaluacion_sede, name='evaluacion_sede'),
    path('sede-legacy/<int:sede_pk>/iniciar/', views.iniciar_evaluacion_sede, name='iniciar_evaluacion'),
    path('sede-legacy/<int:sede_pk>/estandar/<int:estandar_pk>/', views.evaluar_estandar, name='evaluar_estandar'),
    path('sede-legacy/<int:sede_pk>/criterio/<int:criterio_pk>/', views.evaluar_criterio, name='evaluar_criterio'),
    path('resumen/<int:sede_pk>/', views.resumen_cumplimiento, name='resumen'),

    # ===== EVALUACIÓN INDIVIDUAL =====
    path('detalle/<int:pk>/', views.detalle_evaluacion, name='detalle'),
    path('detalle/<int:pk>/editar/', views.editar_evaluacion, name='editar'),
    path('detalle/<int:pk>/aprobar/', views.aprobar_evaluacion, name='aprobar'),
    path('detalle/<int:pk>/documento/', views.gestionar_documento, name='documento'),
    path('detalle/<int:pk>/historial/', views.historial_evaluacion, name='historial'),

    # ===== API IA =====
    path('detalle/<int:pk>/generar-ia/', views.generar_documento_ia, name='generar_ia'),

    # ===== NUEVO SISTEMA: NAVEGACIÓN EN ÁRBOL POR SEDE =====
    # Entrada principal: Lista de sedes
    path('', views.lista_sedes_evaluar, name='sedes_evaluar'),

    # Sede -> Categorías (grupos de estándares)
    path('sede/<int:sede_pk>/', views.sede_categorias, name='sede_categorias'),

    # Sede -> Categoría -> Subcategorías (estándares dentro del grupo)
    path('sede/<int:sede_pk>/grupo/<int:grupo_pk>/', views.sede_subcategorias, name='sede_subcategorias'),

    # Sede -> Categoría -> Subcategoría -> Criterios para evaluar
    path('sede/<int:sede_pk>/estandar/<int:estandar_pk>/', views.sede_criterios_estandar, name='sede_criterios'),

    # Configuración de grupos por sede
    path('sede/<int:sede_pk>/configuracion/', views.sede_configuracion, name='sede_configuracion'),

    # Ver documentos de un criterio (página separada)
    path('documentos/<int:evaluacion_pk>/', views.ver_documentos_criterio, name='ver_documentos'),

    # Resumen de evaluación de sede
    path('sede/<int:sede_pk>/resumen/', views.resumen_evaluacion_sede, name='sede_resumen'),

    # ===== LEGACY: Mantener por compatibilidad =====
    path('mi-evaluacion/', views.dashboard_evaluacion_entidad, name='dashboard_entidad'),
    path('estandares/', views.lista_estandares_evaluar, name='lista_estandares'),
    path('tabla/<int:estandar_pk>/', views.tabla_criterios_estandar, name='tabla_criterios'),

    # ===== API AJAX PARA GUARDADO AUTOMATICO (SEDE) =====
    path('api/guardar-criterio/', views.guardar_evaluacion_criterio_sede, name='api_guardar_criterio'),
    path('api/subir-archivo/<int:evaluacion_pk>/', views.subir_archivo_criterio_sede, name='api_subir_archivo'),
    path('api/eliminar-archivo/<int:archivo_pk>/', views.eliminar_archivo_criterio_sede, name='api_eliminar_archivo'),

    # ===== PREVIEW DE ARCHIVOS (para auditores) =====
    path('preview-archivo/<int:archivo_pk>/', views.preview_archivo, name='preview_archivo'),
]
