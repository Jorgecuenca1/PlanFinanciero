"""URLs del módulo documentos"""
from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('', views.lista_documentos, name='lista'),
    path('generar-ia/', views.generar_con_ia, name='generar_ia'),
    path('mejorar-ia/<int:documento_pk>/', views.mejorar_con_ia, name='mejorar_ia'),
    path('prompts/', views.lista_prompts, name='prompts'),
    path('prompts/crear/', views.crear_prompt, name='crear_prompt'),
    path('normativas/', views.lista_normativas, name='normativas'),
    path('historial-ia/', views.historial_ia, name='historial_ia'),
]
