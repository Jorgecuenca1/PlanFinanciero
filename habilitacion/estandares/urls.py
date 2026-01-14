"""URLs del módulo estandares"""
from django.urls import path
from . import views

app_name = 'estandares'

urlpatterns = [
    path('', views.lista_grupos, name='lista_grupos'),
    path('grupos/<int:pk>/', views.detalle_grupo, name='detalle_grupo'),
    path('estandar/<int:pk>/', views.detalle_estandar, name='detalle_estandar'),
    path('servicios/', views.lista_servicios, name='lista_servicios'),
    path('servicios/<int:pk>/', views.detalle_servicio, name='detalle_servicio'),
    path('criterios/<int:pk>/', views.detalle_criterio, name='detalle_criterio'),
]
