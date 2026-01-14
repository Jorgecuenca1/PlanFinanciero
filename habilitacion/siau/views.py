"""
Vistas del módulo SIAU.
Sistema de Información y Atención al Usuario.
Este módulo está reservado para desarrollo futuro.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PQRS, EncuestaSatisfaccion


@login_required
def dashboard_siau(request):
    """Dashboard del módulo SIAU"""
    return render(request, 'siau/dashboard.html', {
        'titulo': 'SIAU',
        'mensaje': 'Módulo en desarrollo. Próximamente disponible.',
    })


@login_required
def lista_pqrs(request):
    """Lista de PQRS"""
    if request.user.entidad:
        pqrs = PQRS.objects.filter(entidad=request.user.entidad)
    else:
        pqrs = PQRS.objects.none()

    return render(request, 'siau/pqrs/lista.html', {
        'titulo': 'PQRS',
        'pqrs': pqrs,
    })


@login_required
def detalle_pqrs(request, pk):
    """Detalle de una PQRS"""
    pqrs = get_object_or_404(PQRS, pk=pk)

    return render(request, 'siau/pqrs/detalle.html', {
        'titulo': f'PQRS {pqrs.radicado}',
        'pqrs': pqrs,
    })


@login_required
def lista_encuestas(request):
    """Lista de encuestas de satisfacción"""
    if request.user.entidad:
        encuestas = EncuestaSatisfaccion.objects.filter(entidad=request.user.entidad)
    else:
        encuestas = EncuestaSatisfaccion.objects.none()

    return render(request, 'siau/encuestas/lista.html', {
        'titulo': 'Encuestas de Satisfacción',
        'encuestas': encuestas,
    })
