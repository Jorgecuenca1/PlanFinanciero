from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
import csv

from .models import Rubro, Movimiento, IngresoAgregado, OrganoEjecutor, TipoIngreso, Vigencia, RubroGasto, MovimientoGasto
from .forms import (
    RubroForm, MovimientoForm, IngresoAgregadoForm,
    TrasladoForm, AnularMovimientoForm, OrganoEjecutorForm, MovimientoGastoForm
)

# Alias para compatibilidad
FuenteFinanciacion = IngresoAgregado
FuenteFinanciacionForm = IngresoAgregadoForm


def get_rubros_con_saldos(queryset=None, solo_detalle=True):
    """
    Retorna rubros con saldos calculados a nivel de base de datos.
    Mucho mas eficiente que calcular en Python.
    """
    if queryset is None:
        queryset = Rubro.objects.all()

    if solo_detalle:
        queryset = queryset.filter(es_totalizador=False)

    return queryset.annotate(
        _presupuesto_inicial=Coalesce(
            Sum('movimientos__valor',
                filter=Q(movimientos__tipo='INICIAL', movimientos__anulado=False)),
            Value(Decimal('0')), output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
        _total_adiciones=Coalesce(
            Sum('movimientos__valor',
                filter=Q(movimientos__tipo='ADICION', movimientos__anulado=False)),
            Value(Decimal('0')), output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
        _total_reducciones=Coalesce(
            Sum('movimientos__valor',
                filter=Q(movimientos__tipo='REDUCCION', movimientos__anulado=False)),
            Value(Decimal('0')), output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
        _traslados_credito=Coalesce(
            Sum('movimientos__valor',
                filter=Q(movimientos__tipo='TRASLADO_CREDITO', movimientos__anulado=False)),
            Value(Decimal('0')), output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
        _traslados_debito=Coalesce(
            Sum('movimientos__valor',
                filter=Q(movimientos__tipo='TRASLADO_DEBITO', movimientos__anulado=False)),
            Value(Decimal('0')), output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
    )


def calcular_totales_db(queryset):
    """Calcula totales usando agregacion de base de datos"""
    totales = queryset.aggregate(
        total_inicial=Coalesce(Sum('_presupuesto_inicial'), Value(Decimal('0')), output_field=DecimalField()),
        total_adiciones=Coalesce(Sum('_total_adiciones'), Value(Decimal('0')), output_field=DecimalField()),
        total_reducciones=Coalesce(Sum('_total_reducciones'), Value(Decimal('0')), output_field=DecimalField()),
        total_traslados_cred=Coalesce(Sum('_traslados_credito'), Value(Decimal('0')), output_field=DecimalField()),
        total_traslados_deb=Coalesce(Sum('_traslados_debito'), Value(Decimal('0')), output_field=DecimalField()),
    )
    totales['total_saldo'] = (
        (totales['total_inicial'] or Decimal('0')) +
        (totales['total_adiciones'] or Decimal('0')) -
        (totales['total_reducciones'] or Decimal('0')) +
        (totales['total_traslados_cred'] or Decimal('0')) -
        (totales['total_traslados_deb'] or Decimal('0'))
    )
    return totales


@login_required
def dashboard(request):
    """Dashboard principal - OPTIMIZADO"""
    # Conteos rapidos
    total_rubros = Rubro.objects.filter(activo=True, es_totalizador=False).count()
    total_movimientos = Movimiento.objects.filter(anulado=False).count()

    # Totales usando agregacion directa (muy rapido)
    totales = Movimiento.objects.filter(anulado=False).aggregate(
        inicial=Coalesce(Sum('valor', filter=Q(tipo='INICIAL')), Value(Decimal('0')), output_field=DecimalField()),
        adiciones=Coalesce(Sum('valor', filter=Q(tipo='ADICION')), Value(Decimal('0')), output_field=DecimalField()),
        reducciones=Coalesce(Sum('valor', filter=Q(tipo='REDUCCION')), Value(Decimal('0')), output_field=DecimalField()),
        trasl_cred=Coalesce(Sum('valor', filter=Q(tipo='TRASLADO_CREDITO')), Value(Decimal('0')), output_field=DecimalField()),
        trasl_deb=Coalesce(Sum('valor', filter=Q(tipo='TRASLADO_DEBITO')), Value(Decimal('0')), output_field=DecimalField()),
    )

    total_presupuesto_inicial = totales['inicial'] or 0
    total_adiciones = totales['adiciones'] or 0
    total_reducciones = totales['reducciones'] or 0
    total_saldo = (
        total_presupuesto_inicial +
        total_adiciones -
        total_reducciones +
        (totales['trasl_cred'] or 0) -
        (totales['trasl_deb'] or 0)
    )

    # Ultimos movimientos (limitado, con select_related)
    ultimos_movimientos = Movimiento.objects.filter(
        anulado=False
    ).select_related('rubro', 'registrado_por').order_by('-fecha_registro')[:10]

    # Top 5 rubros con mayor saldo (usando anotacion)
    rubros_top = get_rubros_con_saldos().filter(activo=True).order_by('-_presupuesto_inicial')[:5]

    context = {
        'total_rubros': total_rubros,
        'total_movimientos': total_movimientos,
        'total_presupuesto_inicial': total_presupuesto_inicial,
        'total_adiciones': total_adiciones,
        'total_reducciones': total_reducciones,
        'total_saldo': total_saldo,
        'ultimos_movimientos': ultimos_movimientos,
        'rubros_top': rubros_top,
    }
    return render(request, 'planfinanciero/dashboard.html', context)


# === RUBROS ===

@login_required
def rubros_lista(request):
    """Lista de rubros - OPTIMIZADO con paginacion"""
    rubros = Rubro.objects.filter(activo=True).select_related(
        'organo_ejecutor', 'ingreso_agregado', 'tipo_ingreso'
    )

    # Filtros
    busqueda = request.GET.get('q', '')
    ingreso_id = request.GET.get('ingreso', '')
    nivel = request.GET.get('nivel', '')
    organo_id = request.GET.get('organo', '')
    solo_detalle = request.GET.get('solo_detalle', '')

    if busqueda:
        rubros = rubros.filter(
            Q(codigo__icontains=busqueda) | Q(nombre__icontains=busqueda)
        )
    if ingreso_id:
        rubros = rubros.filter(ingreso_agregado_id=ingreso_id)
    if nivel:
        rubros = rubros.filter(nivel=nivel)
    if organo_id:
        rubros = rubros.filter(organo_ejecutor_id=organo_id)
    if solo_detalle:
        rubros = rubros.filter(es_totalizador=False)

    # Anotar saldos a nivel de BD
    rubros = get_rubros_con_saldos(rubros, solo_detalle=False)

    # Paginacion
    paginator = Paginator(rubros.order_by('codigo'), 25)
    page = request.GET.get('page')
    rubros_page = paginator.get_page(page)

    ingresos = IngresoAgregado.objects.filter(activo=True)
    organos = OrganoEjecutor.objects.filter(activo=True)

    context = {
        'rubros': rubros_page,
        'ingresos': ingresos,
        'organos': organos,
        'fuentes': ingresos,
        'busqueda': busqueda,
        'ingreso_id': ingreso_id,
        'fuente_id': ingreso_id,
        'nivel': nivel,
        'organo_id': organo_id,
        'solo_detalle': solo_detalle,
    }
    return render(request, 'planfinanciero/rubros_lista.html', context)


@login_required
def rubro_crear(request):
    """Crear nuevo rubro presupuestal"""
    if request.method == 'POST':
        form = RubroForm(request.POST)
        if form.is_valid():
            rubro = form.save(commit=False)
            rubro.creado_por = request.user
            rubro.save()
            messages.success(request, f'Rubro "{rubro.codigo}" creado exitosamente.')
            return redirect('planfinanciero:rubros_lista')
    else:
        form = RubroForm()

    return render(request, 'planfinanciero/rubro_form.html', {
        'form': form,
        'titulo': 'Crear Rubro Presupuestal',
        'accion': 'Crear'
    })


@login_required
def rubro_detalle(request, pk):
    """Ver detalle de un rubro"""
    rubro = get_object_or_404(Rubro, pk=pk)
    movimientos = rubro.movimientos.filter(anulado=False).order_by('-fecha', '-fecha_registro')[:10]

    # Obtener hijos si es totalizador
    hijos = None
    if rubro.es_totalizador:
        hijos = get_rubros_con_saldos(
            rubro.hijos.filter(activo=True)
        ).order_by('codigo')[:20]

    context = {
        'rubro': rubro,
        'movimientos': movimientos,
        'hijos': hijos,
    }
    return render(request, 'planfinanciero/rubro_detalle.html', context)


@login_required
def rubro_editar(request, pk):
    """Editar rubro presupuestal"""
    rubro = get_object_or_404(Rubro, pk=pk)
    tiene_movimientos = rubro.tiene_movimientos()

    if request.method == 'POST':
        form = RubroForm(request.POST, instance=rubro)
        if form.is_valid():
            if tiene_movimientos:
                form.instance.codigo = rubro.codigo
            form.save()
            messages.success(request, 'Rubro actualizado exitosamente.')
            return redirect('planfinanciero:rubro_detalle', pk=pk)
    else:
        form = RubroForm(instance=rubro)

    return render(request, 'planfinanciero/rubro_form.html', {
        'form': form,
        'rubro': rubro,
        'titulo': f'Editar Rubro {rubro.codigo}',
        'accion': 'Guardar',
        'tiene_movimientos': tiene_movimientos
    })


@login_required
def rubro_kardex(request, pk):
    """Vista de Kardex (historia) de un rubro"""
    rubro = get_object_or_404(Rubro, pk=pk)
    movimientos = rubro.movimientos.all().order_by('fecha', 'fecha_registro')

    # Calcular saldo acumulado
    saldo = Decimal('0')
    movimientos_con_saldo = []
    for mov in movimientos:
        if mov.anulado:
            movimientos_con_saldo.append({'mov': mov, 'saldo': None})
        else:
            if mov.tipo in ['INICIAL', 'ADICION', 'TRASLADO_CREDITO']:
                saldo += mov.valor
            else:
                saldo -= mov.valor
            movimientos_con_saldo.append({'mov': mov, 'saldo': saldo})

    context = {
        'rubro': rubro,
        'movimientos_con_saldo': movimientos_con_saldo,
    }
    return render(request, 'planfinanciero/rubro_kardex.html', context)


# === FUENTES DE FINANCIACION ===

@login_required
def fuentes_lista(request):
    """Lista de fuentes de financiacion"""
    fuentes = IngresoAgregado.objects.all()
    return render(request, 'planfinanciero/fuentes_lista.html', {'fuentes': fuentes})


@login_required
def fuente_crear(request):
    """Crear fuente de financiacion"""
    if request.method == 'POST':
        form = IngresoAgregadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fuente de financiacion creada exitosamente.')
            return redirect('planfinanciero:fuentes_lista')
    else:
        form = IngresoAgregadoForm()

    return render(request, 'planfinanciero/fuente_form.html', {
        'form': form,
        'titulo': 'Crear Fuente de Financiacion',
        'accion': 'Crear'
    })


@login_required
def fuente_editar(request, pk):
    """Editar fuente de financiacion"""
    fuente = get_object_or_404(IngresoAgregado, pk=pk)

    if request.method == 'POST':
        form = IngresoAgregadoForm(request.POST, instance=fuente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fuente de financiacion actualizada.')
            return redirect('planfinanciero:fuentes_lista')
    else:
        form = IngresoAgregadoForm(instance=fuente)

    return render(request, 'planfinanciero/fuente_form.html', {
        'form': form,
        'titulo': f'Editar Fuente {fuente.codigo}',
        'accion': 'Guardar'
    })


# === ORGANOS EJECUTORES ===

@login_required
def organos_lista(request):
    """Lista de organos ejecutores"""
    organos = OrganoEjecutor.objects.all()
    return render(request, 'planfinanciero/organos_lista.html', {'organos': organos})


@login_required
def organo_crear(request):
    """Crear organo ejecutor"""
    if request.method == 'POST':
        form = OrganoEjecutorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organo ejecutor creado exitosamente.')
            return redirect('planfinanciero:organos_lista')
    else:
        form = OrganoEjecutorForm()

    return render(request, 'planfinanciero/organo_form.html', {
        'form': form,
        'titulo': 'Crear Organo Ejecutor',
        'accion': 'Crear'
    })


@login_required
def organo_editar(request, pk):
    """Editar organo ejecutor"""
    organo = get_object_or_404(OrganoEjecutor, pk=pk)

    if request.method == 'POST':
        form = OrganoEjecutorForm(request.POST, instance=organo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organo ejecutor actualizado.')
            return redirect('planfinanciero:organos_lista')
    else:
        form = OrganoEjecutorForm(instance=organo)

    return render(request, 'planfinanciero/organo_form.html', {
        'form': form,
        'titulo': f'Editar Organo {organo.nombre}',
        'accion': 'Guardar'
    })


# === MOVIMIENTOS ===

@login_required
def movimientos_lista(request):
    """Lista de movimientos - OPTIMIZADO"""
    movimientos = Movimiento.objects.select_related('rubro', 'registrado_por')

    # Filtros
    tipo = request.GET.get('tipo', '')
    rubro_codigo = request.GET.get('rubro_codigo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    mostrar_anulados = request.GET.get('anulados', '') == '1'

    if not mostrar_anulados:
        movimientos = movimientos.filter(anulado=False)
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    if rubro_codigo:
        movimientos = movimientos.filter(rubro__codigo__icontains=rubro_codigo)
    if fecha_desde:
        movimientos = movimientos.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)

    # Paginacion
    paginator = Paginator(movimientos.order_by('-fecha', '-fecha_registro'), 25)
    page = request.GET.get('page')
    movimientos_page = paginator.get_page(page)

    context = {
        'movimientos': movimientos_page,
        'tipo': tipo,
        'rubro_codigo': rubro_codigo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'mostrar_anulados': mostrar_anulados,
        'tipos_movimiento': Movimiento.TIPO_CHOICES,
    }
    return render(request, 'planfinanciero/movimientos_lista.html', context)


@login_required
def movimiento_crear(request):
    """Crear nuevo movimiento - OPTIMIZADO"""
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            try:
                movimiento = form.save(commit=False)
                movimiento.registrado_por = request.user
                movimiento.save()
                messages.success(request, 'Movimiento registrado exitosamente.')
                return redirect('planfinanciero:movimientos_lista')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        initial = {}
        rubro_id = request.GET.get('rubro')
        if rubro_id:
            initial['rubro'] = rubro_id
        form = MovimientoForm(initial=initial)

    return render(request, 'planfinanciero/movimiento_form.html', {
        'form': form,
        'titulo': 'Registrar Movimiento',
        'accion': 'Registrar'
    })


@login_required
def movimiento_detalle(request, pk):
    """Ver detalle de un movimiento"""
    movimiento = get_object_or_404(Movimiento.objects.select_related('rubro', 'registrado_por'), pk=pk)
    return render(request, 'planfinanciero/movimiento_detalle.html', {'movimiento': movimiento})


@login_required
def movimiento_anular(request, pk):
    """Anular un movimiento"""
    movimiento = get_object_or_404(Movimiento, pk=pk)

    if movimiento.anulado:
        messages.warning(request, 'Este movimiento ya esta anulado.')
        return redirect('planfinanciero:movimiento_detalle', pk=pk)

    if request.method == 'POST':
        form = AnularMovimientoForm(request.POST)
        if form.is_valid():
            movimiento.anulado = True
            movimiento.motivo_anulacion = form.cleaned_data['motivo']
            movimiento.fecha_anulacion = timezone.now()
            movimiento.anulado_por = request.user
            movimiento.save()

            if movimiento.movimiento_relacionado:
                rel = movimiento.movimiento_relacionado
                rel.anulado = True
                rel.motivo_anulacion = f"Anulacion por relacion con movimiento #{movimiento.pk}"
                rel.fecha_anulacion = timezone.now()
                rel.anulado_por = request.user
                rel.save()

            messages.success(request, 'Movimiento anulado exitosamente.')
            return redirect('planfinanciero:movimientos_lista')
    else:
        form = AnularMovimientoForm()

    return render(request, 'planfinanciero/movimiento_anular.html', {
        'movimiento': movimiento,
        'form': form
    })


@login_required
def traslado_crear(request):
    """Crear un traslado - OPTIMIZADO (sin cargar todos los rubros)"""
    if request.method == 'POST':
        form = TrasladoForm(request.POST)
        if form.is_valid():
            try:
                rubro_origen = form.cleaned_data['rubro_origen']
                rubro_destino = form.cleaned_data['rubro_destino']
                valor = form.cleaned_data['valor']
                fecha = form.cleaned_data['fecha']
                documento = form.cleaned_data['documento_soporte']
                observaciones = form.cleaned_data['observaciones']

                if not rubro_origen.puede_reducir(valor):
                    messages.error(
                        request,
                        f'El rubro origen no tiene saldo suficiente. Saldo: ${rubro_origen.saldo_actual:,.2f}'
                    )
                else:
                    mov_debito = Movimiento.objects.create(
                        rubro=rubro_origen,
                        fecha=fecha,
                        tipo='TRASLADO_DEBITO',
                        documento_soporte=documento,
                        valor=valor,
                        observaciones=f"Traslado hacia {rubro_destino.codigo}. {observaciones}",
                        registrado_por=request.user
                    )

                    mov_credito = Movimiento.objects.create(
                        rubro=rubro_destino,
                        fecha=fecha,
                        tipo='TRASLADO_CREDITO',
                        documento_soporte=documento,
                        valor=valor,
                        observaciones=f"Traslado desde {rubro_origen.codigo}. {observaciones}",
                        registrado_por=request.user,
                        movimiento_relacionado=mov_debito
                    )

                    mov_debito.movimiento_relacionado = mov_credito
                    mov_debito.save()

                    messages.success(request, 'Traslado registrado exitosamente.')
                    return redirect('planfinanciero:movimientos_lista')
            except Exception as e:
                messages.error(request, f'Error al registrar el traslado: {str(e)}')
    else:
        form = TrasladoForm()

    return render(request, 'planfinanciero/traslado_form.html', {
        'form': form,
        'titulo': 'Registrar Traslado'
    })


# === REPORTES ===

@login_required
def reportes(request):
    """Vista principal de reportes con resumen consolidado"""
    # Total Ingresos
    totales_ingresos = Movimiento.objects.filter(anulado=False).aggregate(
        inicial=Coalesce(Sum('valor', filter=Q(tipo='INICIAL')), Value(Decimal('0')), output_field=DecimalField()),
        adiciones=Coalesce(Sum('valor', filter=Q(tipo='ADICION')), Value(Decimal('0')), output_field=DecimalField()),
        reducciones=Coalesce(Sum('valor', filter=Q(tipo='REDUCCION')), Value(Decimal('0')), output_field=DecimalField()),
    )
    total_ingresos = (
        (totales_ingresos['inicial'] or Decimal('0')) +
        (totales_ingresos['adiciones'] or Decimal('0')) -
        (totales_ingresos['reducciones'] or Decimal('0'))
    )

    # Total Gastos
    totales_gastos = MovimientoGasto.objects.filter(anulado=False).aggregate(
        inicial=Coalesce(Sum('valor', filter=Q(tipo='INICIAL')), Value(Decimal('0')), output_field=DecimalField()),
        adiciones=Coalesce(Sum('valor', filter=Q(tipo='ADICION')), Value(Decimal('0')), output_field=DecimalField()),
        reducciones=Coalesce(Sum('valor', filter=Q(tipo='REDUCCION')), Value(Decimal('0')), output_field=DecimalField()),
        creditos=Coalesce(Sum('valor', filter=Q(tipo='CREDITO')), Value(Decimal('0')), output_field=DecimalField()),
        contracreditos=Coalesce(Sum('valor', filter=Q(tipo='CONTRACREDITO')), Value(Decimal('0')), output_field=DecimalField()),
    )
    total_gastos = (
        (totales_gastos['inicial'] or Decimal('0')) +
        (totales_gastos['adiciones'] or Decimal('0')) -
        (totales_gastos['reducciones'] or Decimal('0')) +
        (totales_gastos['creditos'] or Decimal('0')) -
        (totales_gastos['contracreditos'] or Decimal('0'))
    )

    diferencia = total_ingresos - total_gastos

    context = {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'diferencia': diferencia,
    }
    return render(request, 'planfinanciero/reportes.html', context)


@login_required
def reporte_ejecucion(request):
    """Reporte de ejecucion - OPTIMIZADO con paginacion"""
    rubros = get_rubros_con_saldos().filter(activo=True).select_related(
        'organo_ejecutor', 'ingreso_agregado', 'tipo_ingreso'
    )

    # Filtros
    ingreso_id = request.GET.get('ingreso', '')
    nivel = request.GET.get('nivel', '')
    organo_id = request.GET.get('organo', '')

    if ingreso_id:
        rubros = rubros.filter(ingreso_agregado_id=ingreso_id)
    if nivel:
        rubros = rubros.filter(nivel=nivel)
    if organo_id:
        rubros = rubros.filter(organo_ejecutor_id=organo_id)

    # Totales ANTES de paginar
    totales = calcular_totales_db(rubros)

    # Paginacion
    paginator = Paginator(rubros.order_by('codigo'), 50)
    page = request.GET.get('page')
    rubros_page = paginator.get_page(page)

    ingresos = IngresoAgregado.objects.filter(activo=True)
    organos = OrganoEjecutor.objects.filter(activo=True)

    context = {
        'rubros': rubros_page,
        'ingresos': ingresos,
        'fuentes': ingresos,
        'organos': organos,
        'ingreso_id': ingreso_id,
        'fuente_id': ingreso_id,
        'nivel': nivel,
        'organo_id': organo_id,
        'total_inicial': totales['total_inicial'],
        'total_adiciones': totales['total_adiciones'],
        'total_reducciones': totales['total_reducciones'],
        'total_saldo': totales['total_saldo'],
    }
    return render(request, 'planfinanciero/reporte_ejecucion.html', context)


# === REPORTES DINAMICOS - OPTIMIZADOS ===

def _calcular_totales_agregados(queryset):
    """Calcula totales de un queryset ya anotado"""
    return queryset.aggregate(
        inicial=Coalesce(Sum('_presupuesto_inicial'), Value(Decimal('0')), output_field=DecimalField()),
        adiciones=Coalesce(Sum('_total_adiciones'), Value(Decimal('0')), output_field=DecimalField()),
        reducciones=Coalesce(Sum('_total_reducciones'), Value(Decimal('0')), output_field=DecimalField()),
        traslados_credito=Coalesce(Sum('_traslados_credito'), Value(Decimal('0')), output_field=DecimalField()),
        traslados_debito=Coalesce(Sum('_traslados_debito'), Value(Decimal('0')), output_field=DecimalField()),
    )


@login_required
def reporte_por_nivel(request):
    """Reporte por Nivel - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True)

    datos = []
    for nivel_code, nivel_name in Rubro.NIVEL_CHOICES:
        qs = rubros.filter(nivel=nivel_code)
        count = qs.count()
        if count > 0:
            totales = _calcular_totales_agregados(qs)
            saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                    totales['traslados_credito'] - totales['traslados_debito'])
            datos.append({
                'nombre': nivel_name,
                'codigo': nivel_code,
                'cantidad': count,
                'inicial': totales['inicial'],
                'adiciones': totales['adiciones'],
                'reducciones': totales['reducciones'],
                'traslados_credito': totales['traslados_credito'],
                'traslados_debito': totales['traslados_debito'],
                'saldo': saldo,
            })

    # Gran total
    totales_all = _calcular_totales_agregados(rubros)
    gran_total = {
        'inicial': totales_all['inicial'],
        'adiciones': totales_all['adiciones'],
        'reducciones': totales_all['reducciones'],
        'traslados_credito': totales_all['traslados_credito'],
        'traslados_debito': totales_all['traslados_debito'],
        'saldo': (totales_all['inicial'] + totales_all['adiciones'] - totales_all['reducciones'] +
                  totales_all['traslados_credito'] - totales_all['traslados_debito']),
    }

    return render(request, 'planfinanciero/reporte_dinamico.html', {
        'titulo': 'Reporte por Nivel',
        'datos': datos,
        'gran_total': gran_total,
        'columna_grupo': 'Nivel',
    })


@login_required
def reporte_por_organo(request):
    """Reporte por Organo - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True)
    organos = OrganoEjecutor.objects.filter(activo=True)

    datos = []
    for organo in organos:
        qs = rubros.filter(organo_ejecutor_id=organo.id)
        count = qs.count()
        if count > 0:
            totales = _calcular_totales_agregados(qs)
            saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                    totales['traslados_credito'] - totales['traslados_debito'])
            datos.append({
                'nombre': organo.nombre,
                'codigo': organo.codigo,
                'cantidad': count,
                'inicial': totales['inicial'],
                'adiciones': totales['adiciones'],
                'reducciones': totales['reducciones'],
                'traslados_credito': totales['traslados_credito'],
                'traslados_debito': totales['traslados_debito'],
                'saldo': saldo,
            })

    datos.sort(key=lambda x: x['saldo'], reverse=True)

    totales_all = _calcular_totales_agregados(rubros)
    gran_total = {
        'inicial': totales_all['inicial'],
        'adiciones': totales_all['adiciones'],
        'reducciones': totales_all['reducciones'],
        'traslados_credito': totales_all['traslados_credito'],
        'traslados_debito': totales_all['traslados_debito'],
        'saldo': (totales_all['inicial'] + totales_all['adiciones'] - totales_all['reducciones'] +
                  totales_all['traslados_credito'] - totales_all['traslados_debito']),
    }

    return render(request, 'planfinanciero/reporte_dinamico.html', {
        'titulo': 'Reporte por Organo Ejecutor',
        'datos': datos,
        'gran_total': gran_total,
        'columna_grupo': 'Organo Ejecutor',
    })


@login_required
def reporte_por_ingreso(request):
    """Reporte por Ingreso - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True)
    ingresos = IngresoAgregado.objects.filter(activo=True)

    datos = []
    for ingreso in ingresos:
        qs = rubros.filter(ingreso_agregado_id=ingreso.id)
        count = qs.count()
        if count > 0:
            totales = _calcular_totales_agregados(qs)
            saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                    totales['traslados_credito'] - totales['traslados_debito'])
            datos.append({
                'nombre': ingreso.nombre,
                'codigo': ingreso.codigo,
                'cantidad': count,
                'inicial': totales['inicial'],
                'adiciones': totales['adiciones'],
                'reducciones': totales['reducciones'],
                'traslados_credito': totales['traslados_credito'],
                'traslados_debito': totales['traslados_debito'],
                'saldo': saldo,
            })

    datos.sort(key=lambda x: x['saldo'], reverse=True)

    totales_all = _calcular_totales_agregados(rubros)
    gran_total = {
        'inicial': totales_all['inicial'],
        'adiciones': totales_all['adiciones'],
        'reducciones': totales_all['reducciones'],
        'traslados_credito': totales_all['traslados_credito'],
        'traslados_debito': totales_all['traslados_debito'],
        'saldo': (totales_all['inicial'] + totales_all['adiciones'] - totales_all['reducciones'] +
                  totales_all['traslados_credito'] - totales_all['traslados_debito']),
    }

    return render(request, 'planfinanciero/reporte_dinamico.html', {
        'titulo': 'Reporte por Ingreso Agregado',
        'datos': datos,
        'gran_total': gran_total,
        'columna_grupo': 'Ingreso Agregado',
    })


@login_required
def reporte_por_clase(request):
    """Reporte por Clase - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True)

    datos = []
    for clase_code, clase_name in Rubro.CLASE_INGRESO_CHOICES:
        qs = rubros.filter(clase_ingreso=clase_code)
        count = qs.count()
        if count > 0:
            totales = _calcular_totales_agregados(qs)
            saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                    totales['traslados_credito'] - totales['traslados_debito'])
            datos.append({
                'nombre': clase_name,
                'codigo': clase_code,
                'cantidad': count,
                'inicial': totales['inicial'],
                'adiciones': totales['adiciones'],
                'reducciones': totales['reducciones'],
                'traslados_credito': totales['traslados_credito'],
                'traslados_debito': totales['traslados_debito'],
                'saldo': saldo,
            })

    datos.sort(key=lambda x: x['saldo'], reverse=True)

    totales_all = _calcular_totales_agregados(rubros)
    gran_total = {
        'inicial': totales_all['inicial'],
        'adiciones': totales_all['adiciones'],
        'reducciones': totales_all['reducciones'],
        'traslados_credito': totales_all['traslados_credito'],
        'traslados_debito': totales_all['traslados_debito'],
        'saldo': (totales_all['inicial'] + totales_all['adiciones'] - totales_all['reducciones'] +
                  totales_all['traslados_credito'] - totales_all['traslados_debito']),
    }

    return render(request, 'planfinanciero/reporte_dinamico.html', {
        'titulo': 'Reporte por Clase de Ingreso',
        'datos': datos,
        'gran_total': gran_total,
        'columna_grupo': 'Clase Ingreso',
    })


@login_required
def reporte_por_tipo(request):
    """Reporte por Tipo - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True)
    tipos = TipoIngreso.objects.filter(activo=True)

    datos = []
    for tipo in tipos:
        qs = rubros.filter(tipo_ingreso_id=tipo.id)
        count = qs.count()
        if count > 0:
            totales = _calcular_totales_agregados(qs)
            saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                    totales['traslados_credito'] - totales['traslados_debito'])
            datos.append({
                'nombre': tipo.nombre,
                'codigo': tipo.codigo,
                'cantidad': count,
                'inicial': totales['inicial'],
                'adiciones': totales['adiciones'],
                'reducciones': totales['reducciones'],
                'traslados_credito': totales['traslados_credito'],
                'traslados_debito': totales['traslados_debito'],
                'saldo': saldo,
            })

    datos.sort(key=lambda x: x['saldo'], reverse=True)

    totales_all = _calcular_totales_agregados(rubros)
    gran_total = {
        'inicial': totales_all['inicial'],
        'adiciones': totales_all['adiciones'],
        'reducciones': totales_all['reducciones'],
        'traslados_credito': totales_all['traslados_credito'],
        'traslados_debito': totales_all['traslados_debito'],
        'saldo': (totales_all['inicial'] + totales_all['adiciones'] - totales_all['reducciones'] +
                  totales_all['traslados_credito'] - totales_all['traslados_debito']),
    }

    return render(request, 'planfinanciero/reporte_dinamico.html', {
        'titulo': 'Reporte por Tipo de Ingreso',
        'datos': datos,
        'gran_total': gran_total,
        'columna_grupo': 'Tipo Ingreso',
    })


@login_required
def reporte_cruzado(request):
    """Reporte cruzado - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True)

    matriz = {}
    for nivel_code, nivel_name in Rubro.NIVEL_CHOICES:
        matriz[nivel_code] = {'nombre': nivel_name}
        for clase_code, clase_name in Rubro.CLASE_INGRESO_CHOICES:
            qs = rubros.filter(nivel=nivel_code, clase_ingreso=clase_code)
            totales = _calcular_totales_agregados(qs)
            saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                    totales['traslados_credito'] - totales['traslados_debito'])
            matriz[nivel_code][clase_code] = {
                'inicial': totales['inicial'],
                'adiciones': totales['adiciones'],
                'reducciones': totales['reducciones'],
                'traslados_credito': totales['traslados_credito'],
                'traslados_debito': totales['traslados_debito'],
                'saldo': saldo,
            }

    totales_clase = {}
    for clase_code, clase_name in Rubro.CLASE_INGRESO_CHOICES:
        qs = rubros.filter(clase_ingreso=clase_code)
        totales = _calcular_totales_agregados(qs)
        saldo = (totales['inicial'] + totales['adiciones'] - totales['reducciones'] +
                totales['traslados_credito'] - totales['traslados_debito'])
        totales_clase[clase_code] = {
            'inicial': totales['inicial'],
            'adiciones': totales['adiciones'],
            'reducciones': totales['reducciones'],
            'traslados_credito': totales['traslados_credito'],
            'traslados_debito': totales['traslados_debito'],
            'saldo': saldo,
        }

    totales_all = _calcular_totales_agregados(rubros)
    gran_total = {
        'inicial': totales_all['inicial'],
        'adiciones': totales_all['adiciones'],
        'reducciones': totales_all['reducciones'],
        'traslados_credito': totales_all['traslados_credito'],
        'traslados_debito': totales_all['traslados_debito'],
        'saldo': (totales_all['inicial'] + totales_all['adiciones'] - totales_all['reducciones'] +
                  totales_all['traslados_credito'] - totales_all['traslados_debito']),
    }

    return render(request, 'planfinanciero/reporte_cruzado.html', {
        'titulo': 'Reporte Cruzado: Nivel x Clase',
        'matriz': matriz,
        'niveles': Rubro.NIVEL_CHOICES,
        'clases': Rubro.CLASE_INGRESO_CHOICES,
        'totales_clase': totales_clase,
        'gran_total': gran_total,
    })


@login_required
def exportar_excel(request):
    """Exportar a CSV - OPTIMIZADO"""
    rubros = get_rubros_con_saldos().filter(activo=True).select_related(
        'organo_ejecutor', 'ingreso_agregado', 'tipo_ingreso'
    ).order_by('codigo')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ejecucion_presupuestal.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Codigo', 'Nombre', 'Nivel', 'Organo', 'Ingreso',
        'Clase', 'Tipo', 'P.Inicial', 'Adiciones',
        'Reducciones', 'Trasl.Cred', 'Trasl.Deb', 'Saldo'
    ])

    for r in rubros:
        saldo = (r._presupuesto_inicial + r._total_adiciones - r._total_reducciones +
                r._traslados_credito - r._traslados_debito)
        writer.writerow([
            r.codigo,
            r.nombre,
            r.get_nivel_display() if r.nivel else '',
            r.organo_ejecutor.nombre if r.organo_ejecutor else '',
            r.ingreso_agregado.codigo if r.ingreso_agregado else '',
            r.get_clase_ingreso_display() if r.clase_ingreso else '',
            r.tipo_ingreso.nombre if r.tipo_ingreso else '',
            r._presupuesto_inicial,
            r._total_adiciones,
            r._total_reducciones,
            r._traslados_credito,
            r._traslados_debito,
            saldo,
        ])

    return response


@login_required
def exportar_reporte_dinamico(request, tipo):
    """Exportar reporte dinamico a CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_{tipo}.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Grupo', 'Cantidad', 'P.Inicial', 'Adiciones', 'Reducciones', 'Saldo'])

    rubros = get_rubros_con_saldos().filter(activo=True)

    if tipo == 'nivel':
        for code, name in Rubro.NIVEL_CHOICES:
            qs = rubros.filter(nivel=code)
            if qs.exists():
                t = _calcular_totales_agregados(qs)
                writer.writerow([name, qs.count(), t['inicial'], t['adiciones'], t['reducciones'],
                                t['inicial'] + t['adiciones'] - t['reducciones']])

    return response


# === API ===

@login_required
def api_buscar_rubros(request):
    """API para busqueda de rubros - OPTIMIZADO para Select2"""
    q = request.GET.get('q', '').strip()

    if len(q) < 2:
        return JsonResponse({'results': []})

    # Busqueda eficiente con limite
    rubros = Rubro.objects.filter(
        Q(codigo__icontains=q) | Q(nombre__icontains=q),
        activo=True,
        es_totalizador=False
    ).values('id', 'codigo', 'nombre')[:15]

    # Calcular saldos solo para los rubros encontrados
    rubros_ids = [r['id'] for r in rubros]
    saldos = {}

    if rubros_ids:
        saldos_qs = Movimiento.objects.filter(
            rubro_id__in=rubros_ids,
            anulado=False
        ).values('rubro_id').annotate(
            inicial=Coalesce(Sum('valor', filter=Q(tipo='INICIAL')), Value(Decimal('0')), output_field=DecimalField()),
            adiciones=Coalesce(Sum('valor', filter=Q(tipo='ADICION')), Value(Decimal('0')), output_field=DecimalField()),
            reducciones=Coalesce(Sum('valor', filter=Q(tipo='REDUCCION')), Value(Decimal('0')), output_field=DecimalField()),
            trasl_cred=Coalesce(Sum('valor', filter=Q(tipo='TRASLADO_CREDITO')), Value(Decimal('0')), output_field=DecimalField()),
            trasl_deb=Coalesce(Sum('valor', filter=Q(tipo='TRASLADO_DEBITO')), Value(Decimal('0')), output_field=DecimalField()),
        )
        for s in saldos_qs:
            saldos[s['rubro_id']] = (
                s['inicial'] + s['adiciones'] - s['reducciones'] +
                s['trasl_cred'] - s['trasl_deb']
            )

    results = [{
        'id': r['id'],
        'codigo': r['codigo'],
        'nombre': r['nombre'],
        'saldo': float(saldos.get(r['id'], 0))
    } for r in rubros]

    return JsonResponse({'results': results})


# ==========================================
# PLAN FINANCIERO DE GASTOS
# ==========================================

@login_required
def gastos_dashboard(request):
    """Dashboard del Plan Financiero de Gastos"""
    rubros = RubroGasto.objects.filter(activo=True)

    # Calcular totales para cada rubro
    datos_rubros = []
    total_inicial = Decimal('0')
    total_adiciones = Decimal('0')
    total_reducciones = Decimal('0')
    total_creditos = Decimal('0')
    total_contracreditos = Decimal('0')
    total_saldo = Decimal('0')

    for rubro in rubros:
        datos_rubros.append({
            'rubro': rubro,
            'inicial': rubro.presupuesto_inicial,
            'adiciones': rubro.total_adiciones,
            'reducciones': rubro.total_reducciones,
            'creditos': rubro.total_creditos,
            'contracreditos': rubro.total_contracreditos,
            'saldo': rubro.saldo_actual,
        })
        total_inicial += rubro.presupuesto_inicial
        total_adiciones += rubro.total_adiciones
        total_reducciones += rubro.total_reducciones
        total_creditos += rubro.total_creditos
        total_contracreditos += rubro.total_contracreditos
        total_saldo += rubro.saldo_actual

    # Ultimos movimientos
    ultimos_movimientos = MovimientoGasto.objects.filter(
        anulado=False
    ).select_related('rubro', 'registrado_por').order_by('-fecha_registro')[:10]

    context = {
        'datos_rubros': datos_rubros,
        'total_inicial': total_inicial,
        'total_adiciones': total_adiciones,
        'total_reducciones': total_reducciones,
        'total_creditos': total_creditos,
        'total_contracreditos': total_contracreditos,
        'total_saldo': total_saldo,
        'ultimos_movimientos': ultimos_movimientos,
        'total_movimientos': MovimientoGasto.objects.filter(anulado=False).count(),
    }
    return render(request, 'planfinanciero/gastos_dashboard.html', context)


@login_required
def gastos_movimientos_lista(request):
    """Lista de movimientos de gastos"""
    movimientos = MovimientoGasto.objects.select_related('rubro', 'registrado_por')

    # Filtros
    tipo = request.GET.get('tipo', '')
    rubro_codigo = request.GET.get('rubro', '')
    mostrar_anulados = request.GET.get('anulados', '') == '1'

    if not mostrar_anulados:
        movimientos = movimientos.filter(anulado=False)
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    if rubro_codigo:
        movimientos = movimientos.filter(rubro__codigo=rubro_codigo)

    # Paginacion
    paginator = Paginator(movimientos.order_by('-fecha', '-fecha_registro'), 25)
    page = request.GET.get('page')
    movimientos_page = paginator.get_page(page)

    context = {
        'movimientos': movimientos_page,
        'tipo': tipo,
        'rubro_codigo': rubro_codigo,
        'mostrar_anulados': mostrar_anulados,
        'tipos_movimiento': MovimientoGasto.TIPO_CHOICES,
        'rubros': RubroGasto.objects.filter(activo=True),
    }
    return render(request, 'planfinanciero/gastos_movimientos_lista.html', context)


@login_required
def gastos_movimiento_crear(request):
    """Crear nuevo movimiento de gasto"""
    if request.method == 'POST':
        form = MovimientoGastoForm(request.POST)
        if form.is_valid():
            try:
                movimiento = form.save(commit=False)
                movimiento.registrado_por = request.user
                movimiento.save()
                messages.success(request, 'Movimiento de gasto registrado exitosamente.')
                return redirect('planfinanciero:gastos_movimientos_lista')
            except Exception as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        initial = {}
        rubro_codigo = request.GET.get('rubro')
        if rubro_codigo:
            try:
                rubro = RubroGasto.objects.get(codigo=rubro_codigo)
                initial['rubro'] = rubro.pk
            except RubroGasto.DoesNotExist:
                pass
        form = MovimientoGastoForm(initial=initial)

    return render(request, 'planfinanciero/gastos_movimiento_form.html', {
        'form': form,
        'titulo': 'Registrar Movimiento de Gasto',
        'accion': 'Registrar'
    })


@login_required
def gastos_movimiento_detalle(request, pk):
    """Ver detalle de un movimiento de gasto"""
    movimiento = get_object_or_404(MovimientoGasto.objects.select_related('rubro', 'registrado_por'), pk=pk)
    return render(request, 'planfinanciero/gastos_movimiento_detalle.html', {'movimiento': movimiento})


@login_required
def gastos_movimiento_anular(request, pk):
    """Anular un movimiento de gasto"""
    movimiento = get_object_or_404(MovimientoGasto, pk=pk)

    if movimiento.anulado:
        messages.warning(request, 'Este movimiento ya esta anulado.')
        return redirect('planfinanciero:gastos_movimiento_detalle', pk=pk)

    if request.method == 'POST':
        form = AnularMovimientoForm(request.POST)
        if form.is_valid():
            movimiento.anulado = True
            movimiento.motivo_anulacion = form.cleaned_data['motivo']
            movimiento.fecha_anulacion = timezone.now()
            movimiento.anulado_por = request.user
            movimiento.save()

            messages.success(request, 'Movimiento de gasto anulado exitosamente.')
            return redirect('planfinanciero:gastos_movimientos_lista')
    else:
        form = AnularMovimientoForm()

    return render(request, 'planfinanciero/gastos_movimiento_anular.html', {
        'movimiento': movimiento,
        'form': form
    })


@login_required
def gastos_rubro_kardex(request, codigo):
    """Ver kardex de un rubro de gasto"""
    rubro = get_object_or_404(RubroGasto, codigo=codigo)
    movimientos = rubro.movimientos.all().order_by('fecha', 'fecha_registro')

    # Calcular saldo acumulado
    saldo = Decimal('0')
    movimientos_con_saldo = []
    for mov in movimientos:
        if mov.anulado:
            movimientos_con_saldo.append({'mov': mov, 'saldo': None})
        else:
            if mov.tipo in ['INICIAL', 'ADICION', 'CREDITO']:
                saldo += mov.valor
            else:
                saldo -= mov.valor
            movimientos_con_saldo.append({'mov': mov, 'saldo': saldo})

    context = {
        'rubro': rubro,
        'movimientos_con_saldo': movimientos_con_saldo,
    }
    return render(request, 'planfinanciero/gastos_rubro_kardex.html', context)


@login_required
def exportar_gastos_excel(request):
    """Exporta el reporte de gastos a CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plan_financiero_gastos.csv"'
    response.write('\ufeff')  # BOM para Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Rubro', 'P. Inicial', 'Adiciones', 'Reducciones',
        'Creditos', 'Contracreditos', 'Saldo Actual'
    ])

    rubros = RubroGasto.objects.filter(activo=True)
    total_inicial = Decimal('0')
    total_adiciones = Decimal('0')
    total_reducciones = Decimal('0')
    total_creditos = Decimal('0')
    total_contracreditos = Decimal('0')
    total_saldo = Decimal('0')

    for rubro in rubros:
        writer.writerow([
            rubro.nombre,
            rubro.presupuesto_inicial,
            rubro.total_adiciones,
            rubro.total_reducciones,
            rubro.total_creditos,
            rubro.total_contracreditos,
            rubro.saldo_actual,
        ])
        total_inicial += rubro.presupuesto_inicial
        total_adiciones += rubro.total_adiciones
        total_reducciones += rubro.total_reducciones
        total_creditos += rubro.total_creditos
        total_contracreditos += rubro.total_contracreditos
        total_saldo += rubro.saldo_actual

    # Fila de totales
    writer.writerow([
        'TOTAL', total_inicial, total_adiciones, total_reducciones,
        total_creditos, total_contracreditos, total_saldo
    ])

    return response


@login_required
def reporte_comparativo(request):
    """Reporte comparativo entre ingresos y gastos"""
    # Totales de Ingresos
    totales_ingresos = Movimiento.objects.filter(anulado=False).aggregate(
        inicial=Coalesce(Sum('valor', filter=Q(tipo='INICIAL')), Value(Decimal('0')), output_field=DecimalField()),
        adiciones=Coalesce(Sum('valor', filter=Q(tipo='ADICION')), Value(Decimal('0')), output_field=DecimalField()),
        reducciones=Coalesce(Sum('valor', filter=Q(tipo='REDUCCION')), Value(Decimal('0')), output_field=DecimalField()),
    )
    ingresos_inicial = totales_ingresos['inicial'] or Decimal('0')
    ingresos_adiciones = totales_ingresos['adiciones'] or Decimal('0')
    ingresos_reducciones = totales_ingresos['reducciones'] or Decimal('0')
    total_ingresos = ingresos_inicial + ingresos_adiciones - ingresos_reducciones

    # Totales de Gastos por rubro
    rubros_gastos = []
    for rubro in RubroGasto.objects.filter(activo=True):
        rubros_gastos.append({
            'nombre': rubro.nombre,
            'inicial': rubro.presupuesto_inicial,
            'adiciones': rubro.total_adiciones,
            'reducciones': rubro.total_reducciones,
            'creditos': rubro.total_creditos,
            'contracreditos': rubro.total_contracreditos,
            'saldo': rubro.saldo_actual,
        })

    gastos_inicial = sum(r['inicial'] for r in rubros_gastos)
    gastos_adiciones = sum(r['adiciones'] for r in rubros_gastos)
    gastos_reducciones = sum(r['reducciones'] for r in rubros_gastos)
    gastos_creditos = sum(r['creditos'] for r in rubros_gastos)
    gastos_contracreditos = sum(r['contracreditos'] for r in rubros_gastos)
    total_gastos = sum(r['saldo'] for r in rubros_gastos)

    diferencia = total_ingresos - total_gastos
    porcentaje_ejecucion = (total_gastos / total_ingresos * 100) if total_ingresos > 0 else 0

    context = {
        'ingresos_inicial': ingresos_inicial,
        'ingresos_adiciones': ingresos_adiciones,
        'ingresos_reducciones': ingresos_reducciones,
        'total_ingresos': total_ingresos,
        'rubros_gastos': rubros_gastos,
        'gastos_inicial': gastos_inicial,
        'gastos_adiciones': gastos_adiciones,
        'gastos_reducciones': gastos_reducciones,
        'gastos_creditos': gastos_creditos,
        'gastos_contracreditos': gastos_contracreditos,
        'total_gastos': total_gastos,
        'diferencia': diferencia,
        'porcentaje_ejecucion': porcentaje_ejecucion,
    }
    return render(request, 'planfinanciero/reporte_comparativo.html', context)
