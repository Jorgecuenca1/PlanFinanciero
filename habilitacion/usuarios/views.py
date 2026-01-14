"""
Vistas del módulo usuarios.
Gestión de usuarios, perfiles y autenticación.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario


@login_required
def perfil(request):
    """Vista del perfil del usuario actual"""
    return render(request, 'usuarios/perfil.html', {
        'titulo': 'Mi Perfil',
        'usuario': request.user,
    })


@login_required
def lista_usuarios(request):
    """Lista de usuarios (solo administradores)"""
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos para ver esta página.')
        return redirect('core:dashboard')

    usuarios = Usuario.objects.all()
    if request.user.rol != 'SUPER' and request.user.entidad:
        usuarios = usuarios.filter(entidad=request.user.entidad)

    return render(request, 'usuarios/lista.html', {
        'titulo': 'Usuarios',
        'usuarios': usuarios,
    })


@login_required
def crear_usuario(request):
    """Crear nuevo usuario"""
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos para esta acción.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        # Lógica de creación de usuario
        pass

    return render(request, 'usuarios/form.html', {
        'titulo': 'Crear Usuario',
    })


@login_required
def editar_usuario(request, pk):
    """Editar usuario existente"""
    if not request.user.es_administrador:
        messages.error(request, 'No tiene permisos para esta acción.')
        return redirect('core:dashboard')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        # Lógica de edición de usuario
        pass

    return render(request, 'usuarios/form.html', {
        'titulo': 'Editar Usuario',
        'usuario': usuario,
    })
