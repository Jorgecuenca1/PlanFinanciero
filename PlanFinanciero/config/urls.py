"""
URL Configuration for Sistema de Gestión del Plan Financiero
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('app/', include('planfinanciero.urls')),
]
