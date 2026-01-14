"""URLs del módulo entidades"""
from django.urls import path
from . import views

app_name = 'entidades'

urlpatterns = [
    path('', views.lista_entidades, name='lista'),
    path('crear/', views.crear_entidad, name='crear'),
    path('crear-con-usuario/', views.crear_entidad_con_usuario, name='crear_con_usuario'),
    path('<int:pk>/', views.detalle_entidad, name='detalle'),
    path('<int:pk>/editar/', views.editar_entidad, name='editar'),
    path('<int:pk>/sedes/', views.lista_sedes, name='sedes'),
    path('<int:entidad_pk>/sedes/crear/', views.crear_sede, name='crear_sede'),
    path('sedes/<int:pk>/', views.detalle_sede, name='detalle_sede'),
    path('sedes/<int:pk>/editar/', views.editar_sede, name='editar_sede'),
    path('<int:pk>/servicios/', views.servicios_habilitados, name='servicios'),
    path('<int:pk>/documentos/', views.documentos_entidad, name='documentos'),
    path('<int:pk>/configuracion/', views.configuracion_servicios, name='configuracion_servicios'),
]
