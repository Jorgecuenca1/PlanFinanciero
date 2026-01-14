"""URLs del módulo reportes"""
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('cumplimiento/', views.reporte_cumplimiento, name='cumplimiento'),
    path('cumplimiento/<int:entidad_pk>/', views.reporte_cumplimiento_entidad, name='cumplimiento_entidad'),
    path('por-estandar/', views.reporte_por_estandar, name='por_estandar'),
    path('vencimientos/', views.reporte_vencimientos, name='vencimientos'),
    path('exportar/', views.exportar_dashboard, name='exportar'),
    path('exportar/<str:formato>/', views.exportar_reporte, name='exportar_formato'),
]
