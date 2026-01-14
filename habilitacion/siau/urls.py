"""URLs del módulo SIAU"""
from django.urls import path
from . import views

app_name = 'siau'

urlpatterns = [
    path('', views.dashboard_siau, name='dashboard'),
    path('pqrs/', views.lista_pqrs, name='pqrs'),
    path('pqrs/<int:pk>/', views.detalle_pqrs, name='detalle_pqrs'),
    path('encuestas/', views.lista_encuestas, name='encuestas'),
]
