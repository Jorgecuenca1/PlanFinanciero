"""
Vistas del módulo estándares.
Visualización de grupos, estándares, servicios y criterios.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GrupoEstandar, Estandar, Servicio, Criterio


@login_required
def lista_grupos(request):
    """Lista de grupos de estándares"""
    grupos = GrupoEstandar.objects.filter(activo=True)

    return render(request, 'estandares/grupos/lista.html', {
        'titulo': 'Grupos de Estándares',
        'grupos': grupos,
    })


@login_required
def detalle_grupo(request, pk):
    """Detalle de un grupo de estándares"""
    grupo = get_object_or_404(GrupoEstandar, pk=pk)
    estandares = grupo.estandares.filter(activo=True)
    servicios = grupo.servicios.filter(activo=True)

    return render(request, 'estandares/grupos/detalle.html', {
        'titulo': grupo.nombre,
        'grupo': grupo,
        'estandares': estandares,
        'servicios': servicios,
    })


@login_required
def detalle_estandar(request, pk):
    """Detalle de un estándar"""
    estandar = get_object_or_404(Estandar, pk=pk)
    criterios = estandar.criterios.filter(activo=True)

    return render(request, 'estandares/detalle.html', {
        'titulo': estandar.nombre,
        'estandar': estandar,
        'criterios': criterios,
    })


@login_required
def lista_servicios(request):
    """Lista de todos los servicios"""
    servicios = Servicio.objects.filter(activo=True).select_related('grupo')

    return render(request, 'estandares/servicios/lista.html', {
        'titulo': 'Servicios de Salud',
        'servicios': servicios,
    })


@login_required
def detalle_servicio(request, pk):
    """Detalle de un servicio"""
    servicio = get_object_or_404(Servicio, pk=pk)
    estandares_especificos = servicio.estandares_especificos.filter(activo=True)

    return render(request, 'estandares/servicios/detalle.html', {
        'titulo': servicio.nombre,
        'servicio': servicio,
        'estandares_especificos': estandares_especificos,
    })


@login_required
def detalle_criterio(request, pk):
    """Detalle de un criterio"""
    criterio = get_object_or_404(Criterio, pk=pk)

    return render(request, 'estandares/criterio.html', {
        'titulo': f'Criterio {criterio.numero}',
        'criterio': criterio,
    })
