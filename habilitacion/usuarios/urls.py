"""URLs del módulo usuarios"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('lista/', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
]
