"""
Vistas del módulo reportes.
Dashboard y generación de reportes de cumplimiento.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q


@login_required
def dashboard_reportes(request):
    """Dashboard principal de reportes"""
    context = {
        'titulo': 'Reportes',
    }

    if request.user.entidad:
        from entidades.models import EntidadPrestadora, Sede
        from evaluacion.models import Evaluacion

        entidad = request.user.entidad
        sedes = Sede.objects.filter(entidad=entidad, activa=True)

        # Estadísticas generales
        total_evaluaciones = Evaluacion.objects.filter(sede__in=sedes).count()
        evaluaciones_por_estado = Evaluacion.objects.filter(
            sede__in=sedes
        ).values('estado').annotate(total=Count('id'))

        context.update({
            'entidad': entidad,
            'total_sedes': sedes.count(),
            'total_evaluaciones': total_evaluaciones,
            'evaluaciones_por_estado': {
                e['estado']: e['total'] for e in evaluaciones_por_estado
            },
        })

    return render(request, 'reportes/dashboard.html', context)


@login_required
def reporte_cumplimiento(request):
    """Reporte general de cumplimiento"""
    from entidades.models import EntidadPrestadora

    if request.user.rol == 'SUPER':
        entidades = EntidadPrestadora.objects.all()
    elif request.user.entidad:
        entidades = EntidadPrestadora.objects.filter(pk=request.user.entidad.pk)
    else:
        entidades = EntidadPrestadora.objects.none()

    return render(request, 'reportes/cumplimiento.html', {
        'titulo': 'Reporte de Cumplimiento',
        'entidades': entidades,
    })


@login_required
def reporte_cumplimiento_entidad(request, entidad_pk):
    """Reporte de cumplimiento para una entidad específica"""
    from entidades.models import EntidadPrestadora, Sede
    from evaluacion.models import Evaluacion, ResumenCumplimiento
    from estandares.models import GrupoEstandar

    entidad = get_object_or_404(EntidadPrestadora, pk=entidad_pk)
    sedes = Sede.objects.filter(entidad=entidad, activa=True)
    grupos = GrupoEstandar.objects.filter(activo=True)

    # Calcular cumplimiento por sede y grupo
    datos_cumplimiento = []
    for sede in sedes:
        sede_data = {'sede': sede, 'grupos': []}
        for grupo in grupos:
            resumen, _ = ResumenCumplimiento.objects.get_or_create(
                sede=sede,
                grupo_estandar=grupo
            )
            resumen.calcular()
            sede_data['grupos'].append({
                'grupo': grupo,
                'resumen': resumen
            })
        datos_cumplimiento.append(sede_data)

    return render(request, 'reportes/cumplimiento_entidad.html', {
        'titulo': f'Cumplimiento - {entidad.razon_social}',
        'entidad': entidad,
        'sedes': sedes,
        'grupos': grupos,
        'datos_cumplimiento': datos_cumplimiento,
    })


@login_required
def reporte_vencimientos(request):
    """Reporte de documentos por vencer"""
    from entidades.models import DocumentoEntidad
    from django.utils import timezone
    from datetime import timedelta

    fecha_limite = timezone.now().date() + timedelta(days=90)

    if request.user.entidad:
        documentos = DocumentoEntidad.objects.filter(
            entidad=request.user.entidad,
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lte=fecha_limite
        ).order_by('fecha_vencimiento')
    else:
        documentos = DocumentoEntidad.objects.none()

    return render(request, 'reportes/vencimientos.html', {
        'titulo': 'Documentos por Vencer',
        'documentos': documentos,
        'fecha_limite': fecha_limite,
    })


@login_required
def reporte_por_estandar(request):
    """Reporte de cumplimiento por estándar"""
    from estandares.models import GrupoEstandar, Estandar

    grupos = GrupoEstandar.objects.filter(activo=True).prefetch_related('estandares')

    return render(request, 'reportes/por_estandar.html', {
        'titulo': 'Reporte por Estándar',
        'grupos': grupos,
    })


@login_required
def exportar_dashboard(request):
    """Vista para opciones de exportación"""
    return render(request, 'reportes/exportar.html', {
        'titulo': 'Exportar Reportes',
    })


@login_required
def exportar_reporte(request, formato):
    """Exportar reporte en diferentes formatos"""
    # Placeholder para exportación a Excel/PDF
    if formato == 'excel':
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="reporte_habilitacion.xlsx"'
        # Aquí iría la lógica de generación del Excel
        return response
    elif formato == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_habilitacion.pdf"'
        # Aquí iría la lógica de generación del PDF
        return response

    return HttpResponse('Formato no soportado', status=400)
