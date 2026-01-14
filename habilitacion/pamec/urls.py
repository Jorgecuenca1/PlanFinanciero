"""URLs del módulo PAMEC"""
from django.urls import path
from . import views

app_name = 'pamec'

urlpatterns = [
    path('', views.dashboard_pamec, name='dashboard'),
    path('programas/', views.lista_programas, name='programas'),
    path('programas/<int:pk>/', views.detalle_programa, name='detalle'),
]
