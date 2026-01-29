from django.urls import path
from . import views

app_name = 'planfinanciero'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Rubros
    path('rubros/', views.rubros_lista, name='rubros_lista'),
    path('rubros/crear/', views.rubro_crear, name='rubro_crear'),
    path('rubros/<int:pk>/', views.rubro_detalle, name='rubro_detalle'),
    path('rubros/<int:pk>/editar/', views.rubro_editar, name='rubro_editar'),
    path('rubros/<int:pk>/kardex/', views.rubro_kardex, name='rubro_kardex'),

    # Fuentes de Financiacion (Ingresos Agregados)
    path('fuentes/', views.fuentes_lista, name='fuentes_lista'),
    path('fuentes/crear/', views.fuente_crear, name='fuente_crear'),
    path('fuentes/<int:pk>/editar/', views.fuente_editar, name='fuente_editar'),

    # Organos Ejecutores
    path('organos/', views.organos_lista, name='organos_lista'),
    path('organos/crear/', views.organo_crear, name='organo_crear'),
    path('organos/<int:pk>/editar/', views.organo_editar, name='organo_editar'),

    # Movimientos
    path('movimientos/', views.movimientos_lista, name='movimientos_lista'),
    path('movimientos/crear/', views.movimiento_crear, name='movimiento_crear'),
    path('movimientos/<int:pk>/', views.movimiento_detalle, name='movimiento_detalle'),
    path('movimientos/<int:pk>/anular/', views.movimiento_anular, name='movimiento_anular'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/ejecucion/', views.reporte_ejecucion, name='reporte_ejecucion'),
    path('reportes/exportar-excel/', views.exportar_excel, name='exportar_excel'),

    # Reportes Dinamicos (Tablas Dinamicas)
    path('reportes/nivel/', views.reporte_por_nivel, name='reporte_por_nivel'),
    path('reportes/organo/', views.reporte_por_organo, name='reporte_por_organo'),
    path('reportes/ingreso/', views.reporte_por_ingreso, name='reporte_por_ingreso'),
    path('reportes/clase/', views.reporte_por_clase, name='reporte_por_clase'),
    path('reportes/tipo/', views.reporte_por_tipo, name='reporte_por_tipo'),
    path('reportes/cruzado/', views.reporte_cruzado, name='reporte_cruzado'),

    # Exportar reportes dinamicos
    path('reportes/exportar/<str:tipo>/', views.exportar_reporte_dinamico, name='exportar_reporte_dinamico'),

    # API para busqueda
    path('api/rubros/buscar/', views.api_buscar_rubros, name='api_buscar_rubros'),

    # ==========================================
    # PLAN FINANCIERO DE GASTOS - CENTRALIZADOS
    # ==========================================
    path('gastos/', views.gastos_dashboard, name='gastos_dashboard'),
    path('gastos/centralizados/', views.gastos_dashboard, {'tipo_entidad': 'CENTRALIZADO'}, name='gastos_centralizados'),
    path('gastos/descentralizados/', views.gastos_dashboard, {'tipo_entidad': 'DESCENTRALIZADO'}, name='gastos_descentralizados'),
    path('gastos/movimientos/', views.gastos_movimientos_lista, name='gastos_movimientos_lista'),
    path('gastos/movimientos/crear/', views.gastos_movimiento_crear, name='gastos_movimiento_crear'),
    path('gastos/movimientos/<int:pk>/', views.gastos_movimiento_detalle, name='gastos_movimiento_detalle'),
    path('gastos/movimientos/<int:pk>/anular/', views.gastos_movimiento_anular, name='gastos_movimiento_anular'),
    path('gastos/rubro/<str:tipo_entidad>/<str:codigo>/kardex/', views.gastos_rubro_kardex, name='gastos_rubro_kardex'),
    path('gastos/exportar-excel/', views.exportar_gastos_excel, name='exportar_gastos_excel'),

    # Reporte Comparativo
    path('reportes/comparativo/', views.reporte_comparativo, name='reporte_comparativo'),
]
