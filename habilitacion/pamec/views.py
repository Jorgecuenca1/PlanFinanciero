"""
Vistas del módulo PAMEC.
Programa de Auditoría para el Mejoramiento de la Calidad en Salud.
Este módulo está reservado para desarrollo futuro.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ProgramaPAMEC


@login_required
def dashboard_pamec(request):
    """Dashboard del módulo PAMEC"""
    return render(request, 'pamec/dashboard.html', {
        'titulo': 'PAMEC',
        'mensaje': 'Módulo en desarrollo. Próximamente disponible.',
    })


@login_required
def lista_programas(request):
    """Lista de programas PAMEC"""
    if request.user.entidad:
        programas = ProgramaPAMEC.objects.filter(entidad=request.user.entidad)
    else:
        programas = ProgramaPAMEC.objects.none()

    return render(request, 'pamec/programas/lista.html', {
        'titulo': 'Programas PAMEC',
        'programas': programas,
    })


@login_required
def detalle_programa(request, pk):
    """Detalle de un programa PAMEC"""
    programa = get_object_or_404(ProgramaPAMEC, pk=pk)

    return render(request, 'pamec/programas/detalle.html', {
        'titulo': programa.nombre,
        'programa': programa,
    })
