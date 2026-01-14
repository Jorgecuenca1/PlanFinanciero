"""
Vistas del módulo core.
Dashboard principal y páginas generales del sistema.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone


def home(request):
    """Página de inicio - redirige al dashboard si está autenticado"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return redirect('usuarios:login')


@login_required
def dashboard(request):
    """Dashboard principal del sistema"""
    context = {
        'titulo': 'Dashboard',
    }

    # Si el usuario tiene una entidad asignada, mostrar estadísticas
    if hasattr(request.user, 'entidad') and request.user.entidad:
        entidad = request.user.entidad
        context['entidad'] = entidad

        # Obtener sedes de la entidad
        from entidades.models import Sede
        sedes = Sede.objects.filter(entidad=entidad, activa=True)
        context['total_sedes'] = sedes.count()

        # Obtener evaluaciones
        from evaluacion.models import Evaluacion
        evaluaciones = Evaluacion.objects.filter(sede__in=sedes)
        context['total_evaluaciones'] = evaluaciones.count()
        context['evaluaciones_pendientes'] = evaluaciones.filter(estado='PE').count()
        context['evaluaciones_cumple'] = evaluaciones.filter(estado='C').count()
        context['evaluaciones_no_cumple'] = evaluaciones.filter(estado='NC').count()

        # Calcular porcentaje de cumplimiento
        evaluables = evaluaciones.exclude(estado__in=['PE', 'NA']).count()
        if evaluables > 0:
            context['porcentaje_cumplimiento'] = round(
                (context['evaluaciones_cumple'] / evaluables) * 100, 1
            )
        else:
            context['porcentaje_cumplimiento'] = 0

        # Documentos por vencer (próximos 30 días)
        from entidades.models import DocumentoEntidad
        fecha_limite = timezone.now().date() + timezone.timedelta(days=30)
        context['documentos_por_vencer'] = DocumentoEntidad.objects.filter(
            entidad=entidad,
            fecha_vencimiento__isnull=False,
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date()
        ).count()

        # Últimas evaluaciones modificadas
        context['ultimas_evaluaciones'] = evaluaciones.order_by('-fecha_modificacion')[:5]

    return render(request, 'core/dashboard.html', context)
