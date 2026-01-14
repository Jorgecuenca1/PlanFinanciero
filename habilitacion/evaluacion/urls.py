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

    # ===== EVALUACIONES =====
    path('', views.lista_evaluaciones, name='lista'),
    path('sede/<int:sede_pk>/', views.evaluacion_sede, name='evaluacion_sede'),
    path('sede/<int:sede_pk>/iniciar/', views.iniciar_evaluacion_sede, name='iniciar_evaluacion'),
    path('sede/<int:sede_pk>/estandar/<int:estandar_pk>/', views.evaluar_estandar, name='evaluar_estandar'),
    path('sede/<int:sede_pk>/criterio/<int:criterio_pk>/', views.evaluar_criterio, name='evaluar_criterio'),
    path('resumen/<int:sede_pk>/', views.resumen_cumplimiento, name='resumen'),

    # ===== EVALUACIÓN INDIVIDUAL =====
    path('<int:pk>/', views.detalle_evaluacion, name='detalle'),
    path('<int:pk>/editar/', views.editar_evaluacion, name='editar'),
    path('<int:pk>/aprobar/', views.aprobar_evaluacion, name='aprobar'),
    path('<int:pk>/documento/', views.gestionar_documento, name='documento'),
    path('<int:pk>/historial/', views.historial_evaluacion, name='historial'),

    # ===== API IA =====
    path('<int:pk>/generar-ia/', views.generar_documento_ia, name='generar_ia'),

    # ===== EVALUACION POR ENTIDAD (NUEVO SISTEMA) =====
    path('mi-evaluacion/', views.dashboard_evaluacion_entidad, name='dashboard_entidad'),
    path('estandares/', views.lista_estandares_evaluar, name='lista_estandares'),
    path('estandar/<int:estandar_pk>/tabla/', views.tabla_criterios_estandar, name='tabla_criterios'),

    # ===== API AJAX PARA GUARDADO AUTOMATICO =====
    path('api/guardar-criterio/', views.guardar_evaluacion_criterio, name='api_guardar_criterio'),
    path('api/subir-archivo/<int:evaluacion_pk>/', views.subir_archivo_criterio, name='api_subir_archivo'),
    path('api/eliminar-archivo/<int:archivo_pk>/', views.eliminar_archivo_criterio, name='api_eliminar_archivo'),
]
