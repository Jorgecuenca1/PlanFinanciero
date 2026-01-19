"""
Vistas del módulo evaluación.
Gestión de autoevaluaciones, cumplimiento de criterios y vigencias.
Sistema basado en SEDES (no en Entidades).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_sameorigin
import mimetypes
from django.db.models import Count, Q
from .models import Evaluacion, DocumentoEvaluacion, HistorialEvaluacion, ResumenCumplimiento, PeriodoEvaluacion, EvaluacionCriterio, ArchivoRepositorio
from entidades.models import EntidadPrestadora, Sede, ConfiguracionEvaluacionSede
from estandares.models import GrupoEstandar, Estandar, Criterio, Servicio
from usuarios.models import Usuario
import json


# ===============================
# VISTAS DE VIGENCIAS/PERÍODOS
# ===============================

@login_required
def lista_vigencias(request):
    """Lista de vigencias/períodos de evaluación"""
    if request.user.rol == 'SUPER':
        vigencias = PeriodoEvaluacion.objects.all().select_related('entidad')
    elif request.user.entidad:
        vigencias = PeriodoEvaluacion.objects.filter(entidad=request.user.entidad)
    else:
        vigencias = PeriodoEvaluacion.objects.none()

    return render(request, 'evaluacion/vigencias/lista.html', {
        'titulo': 'Vigencias de Evaluación',
        'vigencias': vigencias,
    })


@login_required
def crear_vigencia(request):
    """Crear nueva vigencia/período de evaluación"""
    if request.user.rol == 'SUPER':
        entidades = EntidadPrestadora.objects.filter(estado='ACTIVO')
    else:
        entidades = EntidadPrestadora.objects.filter(pk=request.user.entidad_id)

    if request.method == 'POST':
        try:
            entidad = get_object_or_404(EntidadPrestadora, pk=request.POST.get('entidad'))

            vigencia = PeriodoEvaluacion.objects.create(
                entidad=entidad,
                nombre=request.POST.get('nombre'),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_fin=request.POST.get('fecha_fin'),
                observaciones=request.POST.get('observaciones', ''),
                activo=request.POST.get('activo') == 'on'
            )

            messages.success(request, f'Vigencia "{vigencia.nombre}" creada exitosamente.')
            return redirect('evaluacion:detalle_vigencia', pk=vigencia.pk)
        except Exception as e:
            messages.error(request, f'Error al crear la vigencia: {str(e)}')

    return render(request, 'evaluacion/vigencias/form.html', {
        'titulo': 'Nueva Vigencia',
        'entidades': entidades,
    })


@login_required
def detalle_vigencia(request, pk):
    """Detalle de una vigencia con resumen de cumplimiento"""
    vigencia = get_object_or_404(PeriodoEvaluacion, pk=pk)

    # Calcular porcentaje de cumplimiento
    vigencia.calcular_porcentaje_cumplimiento()

    # Obtener resúmenes por grupo
    grupos = GrupoEstandar.objects.filter(activo=True)
    sedes = vigencia.entidad.sedes.filter(activa=True)

    resumenes_grupos = []
    for grupo in grupos:
        total_c = 0
        total_nc = 0
        total_na = 0
        total_pe = 0

        for sede in sedes:
            evaluaciones = Evaluacion.objects.filter(
                sede=sede,
                criterio__estandar__grupo=grupo,
                fecha_evaluacion__gte=vigencia.fecha_inicio,
                fecha_evaluacion__lte=vigencia.fecha_fin
            )
            total_c += evaluaciones.filter(estado='C').count()
            total_nc += evaluaciones.filter(estado='NC').count()
            total_na += evaluaciones.filter(estado='NA').count()
            total_pe += evaluaciones.filter(estado='PE').count()

        total = total_c + total_nc + total_na + total_pe
        evaluables = total - total_na
        porcentaje = round((total_c / evaluables * 100), 2) if evaluables > 0 else 0

        resumenes_grupos.append({
            'grupo': grupo,
            'total': total,
            'cumple': total_c,
            'no_cumple': total_nc,
            'no_aplica': total_na,
            'pendiente': total_pe,
            'porcentaje': porcentaje
        })

    return render(request, 'evaluacion/vigencias/detalle.html', {
        'titulo': vigencia.nombre,
        'vigencia': vigencia,
        'sedes': sedes,
        'resumenes_grupos': resumenes_grupos,
    })


@login_required
def editar_vigencia(request, pk):
    """Editar vigencia existente"""
    vigencia = get_object_or_404(PeriodoEvaluacion, pk=pk)

    if request.user.rol == 'SUPER':
        entidades = EntidadPrestadora.objects.filter(estado='ACTIVO')
    else:
        entidades = EntidadPrestadora.objects.filter(pk=request.user.entidad_id)

    if request.method == 'POST':
        try:
            entidad = get_object_or_404(EntidadPrestadora, pk=request.POST.get('entidad'))

            vigencia.entidad = entidad
            vigencia.nombre = request.POST.get('nombre')
            vigencia.fecha_inicio = request.POST.get('fecha_inicio')
            vigencia.fecha_fin = request.POST.get('fecha_fin')
            vigencia.observaciones = request.POST.get('observaciones', '')
            vigencia.activo = request.POST.get('activo') == 'on'
            vigencia.save()

            messages.success(request, f'Vigencia "{vigencia.nombre}" actualizada.')
            return redirect('evaluacion:detalle_vigencia', pk=vigencia.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar la vigencia: {str(e)}')

    return render(request, 'evaluacion/vigencias/form.html', {
        'titulo': 'Editar Vigencia',
        'vigencia': vigencia,
        'entidades': entidades,
    })


# ===============================
# VISTAS DE EVALUACIONES
# ===============================

@login_required
def lista_evaluaciones(request):
    """Lista de evaluaciones"""
    if request.user.rol == 'SUPER':
        evaluaciones = Evaluacion.objects.all().select_related('sede', 'criterio')[:100]
        entidades = EntidadPrestadora.objects.all()
    elif request.user.entidad:
        evaluaciones = Evaluacion.objects.filter(
            sede__entidad=request.user.entidad
        ).select_related('sede', 'criterio')[:100]
        entidades = EntidadPrestadora.objects.filter(pk=request.user.entidad_id)
    else:
        evaluaciones = Evaluacion.objects.none()
        entidades = EntidadPrestadora.objects.none()

    return render(request, 'evaluacion/lista.html', {
        'titulo': 'Evaluaciones',
        'evaluaciones': evaluaciones,
        'entidades': entidades,
    })


@login_required
def evaluacion_sede(request, sede_pk):
    """Evaluación completa de una sede"""
    from entidades.models import Sede
    sede = get_object_or_404(Sede, pk=sede_pk)

    evaluaciones = Evaluacion.objects.filter(sede=sede).select_related('criterio')

    # Agrupar por estándar
    from estandares.models import GrupoEstandar
    grupos = GrupoEstandar.objects.filter(activo=True)

    return render(request, 'evaluacion/sede.html', {
        'titulo': f'Evaluación - {sede.nombre}',
        'sede': sede,
        'evaluaciones': evaluaciones,
        'grupos': grupos,
    })


@login_required
def evaluar_estandar(request, sede_pk, estandar_pk):
    """Evaluar criterios de un estándar específico"""
    from entidades.models import Sede
    from estandares.models import Estandar

    sede = get_object_or_404(Sede, pk=sede_pk)
    estandar = get_object_or_404(Estandar, pk=estandar_pk)

    # Obtener o crear evaluaciones para cada criterio
    criterios = estandar.criterios.filter(activo=True, es_titulo=False)

    if request.method == 'POST':
        for criterio in criterios:
            estado = request.POST.get(f'estado_{criterio.id}')
            comentarios = request.POST.get(f'comentarios_{criterio.id}', '')

            if estado:
                evaluacion, created = Evaluacion.objects.get_or_create(
                    sede=sede,
                    criterio=criterio,
                    defaults={'estado': estado, 'comentarios': comentarios}
                )
                if not created:
                    evaluacion.estado = estado
                    evaluacion.comentarios = comentarios
                    evaluacion.fecha_evaluacion = timezone.now()
                    evaluacion.modificado_por = request.user
                    evaluacion.save()

        messages.success(request, 'Evaluación guardada correctamente.')
        return redirect('evaluacion:evaluacion_sede', sede_pk=sede_pk)

    evaluaciones_existentes = {
        e.criterio_id: e
        for e in Evaluacion.objects.filter(sede=sede, criterio__in=criterios)
    }

    return render(request, 'evaluacion/evaluar_estandar.html', {
        'titulo': f'Evaluar {estandar.nombre}',
        'sede': sede,
        'estandar': estandar,
        'criterios': criterios,
        'evaluaciones': evaluaciones_existentes,
    })


@login_required
def detalle_evaluacion(request, pk):
    """Detalle de una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, pk=pk)

    return render(request, 'evaluacion/detalle.html', {
        'titulo': f'Evaluación: {evaluacion.criterio.numero}',
        'evaluacion': evaluacion,
        'documentos': evaluacion.documentos.all(),
        'historial': evaluacion.historial.all()[:10],
    })


@login_required
def editar_evaluacion(request, pk):
    """Editar una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, pk=pk)

    if not evaluacion.puede_editar and not request.user.es_administrador:
        messages.error(request, 'Esta evaluación ya está aprobada y no puede ser editada.')
        return redirect('evaluacion:detalle', pk=pk)

    if request.method == 'POST':
        estado_anterior = evaluacion.estado
        evaluacion.estado = request.POST.get('estado', evaluacion.estado)
        evaluacion.comentarios = request.POST.get('comentarios', '')
        evaluacion.fecha_evaluacion = timezone.now()
        evaluacion.modificado_por = request.user
        evaluacion.save()

        HistorialEvaluacion.objects.create(
            evaluacion=evaluacion,
            usuario=request.user,
            accion='EDITAR',
            descripcion='Evaluación modificada',
            estado_anterior=estado_anterior,
            estado_nuevo=evaluacion.estado
        )

        messages.success(request, 'Evaluación actualizada.')
        return redirect('evaluacion:detalle', pk=pk)

    return render(request, 'evaluacion/editar.html', {
        'titulo': 'Editar Evaluación',
        'evaluacion': evaluacion,
    })


@login_required
def aprobar_evaluacion(request, pk):
    """Aprobar una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, pk=pk)

    if not request.user.puede_aprobar:
        messages.error(request, 'No tiene permisos para aprobar evaluaciones.')
        return redirect('evaluacion:detalle', pk=pk)

    if request.method == 'POST':
        evaluacion.aprobar(request.user)
        messages.success(request, 'Evaluación aprobada correctamente.')

    return redirect('evaluacion:detalle', pk=pk)


@login_required
def gestionar_documento(request, pk):
    """Gestionar documento de una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, pk=pk)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        contenido = request.POST.get('contenido', '')

        documento = DocumentoEvaluacion.objects.create(
            evaluacion=evaluacion,
            nombre=nombre,
            contenido_html=contenido,
            creado_por=request.user
        )

        evaluacion.estado_documento = 'ED'
        evaluacion.save()

        messages.success(request, 'Documento guardado correctamente.')
        return redirect('evaluacion:detalle', pk=pk)

    return render(request, 'evaluacion/documento.html', {
        'titulo': 'Gestionar Documento',
        'evaluacion': evaluacion,
        'documentos': evaluacion.documentos.all(),
    })


@login_required
def historial_evaluacion(request, pk):
    """Historial de una evaluación"""
    evaluacion = get_object_or_404(Evaluacion, pk=pk)
    historial = evaluacion.historial.all()

    return render(request, 'evaluacion/historial.html', {
        'titulo': 'Historial de Evaluación',
        'evaluacion': evaluacion,
        'historial': historial,
    })


@login_required
def resumen_cumplimiento(request, sede_pk):
    """Resumen de cumplimiento por sede"""
    sede = get_object_or_404(Sede, pk=sede_pk)

    # Calcular resúmenes
    grupos = GrupoEstandar.objects.filter(activo=True)

    resumenes = []
    for grupo in grupos:
        resumen, _ = ResumenCumplimiento.objects.get_or_create(
            sede=sede,
            grupo_estandar=grupo
        )
        resumen.calcular()
        resumenes.append(resumen)

    return render(request, 'evaluacion/resumen.html', {
        'titulo': f'Resumen de Cumplimiento - {sede.nombre}',
        'sede': sede,
        'resumenes': resumenes,
    })


# ===============================
# VISTA DETALLADA DE CRITERIO
# ===============================

@login_required
def evaluar_criterio(request, sede_pk, criterio_pk):
    """Evaluar un criterio individual con editor de documentos"""
    sede = get_object_or_404(Sede, pk=sede_pk)
    criterio = get_object_or_404(Criterio, pk=criterio_pk)

    # Obtener o crear evaluación
    evaluacion, created = Evaluacion.objects.get_or_create(
        sede=sede,
        criterio=criterio,
        defaults={'estado': 'PE', 'estado_documento': 'NT'}
    )

    # Obtener usuarios para asignar responsables
    from usuarios.models import Usuario
    usuarios = Usuario.objects.filter(is_active=True, entidad=sede.entidad)

    # Verificar si el documento está bloqueado
    bloqueado = evaluacion.estado_documento == 'AP' and not request.user.es_administrador

    if request.method == 'POST' and not bloqueado:
        estado_anterior = evaluacion.estado
        doc_estado_anterior = evaluacion.estado_documento

        # Actualizar estado del criterio
        evaluacion.estado = request.POST.get('estado', evaluacion.estado)
        evaluacion.estado_documento = request.POST.get('estado_documento', evaluacion.estado_documento)
        evaluacion.comentarios = request.POST.get('comentarios', '')

        # Justificación NA
        if evaluacion.estado == 'NA':
            evaluacion.justificacion_na = request.POST.get('justificacion_na', '')

        # Asignar responsables
        resp_desarrollo = request.POST.get('responsable_desarrollo')
        if resp_desarrollo:
            evaluacion.responsable_desarrollo_id = resp_desarrollo

        resp_calidad = request.POST.get('responsable_calidad')
        if resp_calidad:
            evaluacion.responsable_calidad_id = resp_calidad

        resp_aprobacion = request.POST.get('responsable_aprobacion')
        if resp_aprobacion:
            evaluacion.responsable_aprobacion_id = resp_aprobacion

        # Fecha de vencimiento
        fecha_venc = request.POST.get('fecha_vencimiento')
        if fecha_venc:
            evaluacion.fecha_vencimiento = fecha_venc

        evaluacion.fecha_evaluacion = timezone.now()
        evaluacion.modificado_por = request.user

        # Si se aprueba, guardar fecha
        if evaluacion.estado_documento == 'AP' and doc_estado_anterior != 'AP':
            evaluacion.fecha_aprobacion = timezone.now()
            evaluacion.responsable_aprobacion = request.user

        evaluacion.save()

        # Registrar en historial
        HistorialEvaluacion.objects.create(
            evaluacion=evaluacion,
            usuario=request.user,
            accion='EDITAR',
            descripcion=f'Estado: {estado_anterior} -> {evaluacion.estado}, Documento: {doc_estado_anterior} -> {evaluacion.estado_documento}',
            estado_anterior=estado_anterior,
            estado_nuevo=evaluacion.estado
        )

        # Guardar contenido del documento
        contenido_doc = request.POST.get('contenido_documento', '')
        if contenido_doc:
            doc_existente = evaluacion.documentos.first()
            if doc_existente:
                doc_existente.contenido_html = contenido_doc
                doc_existente.save()
            else:
                DocumentoEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    nombre=f'Documento - {criterio.numero}',
                    contenido_html=contenido_doc,
                    creado_por=request.user
                )

        messages.success(request, 'Criterio evaluado correctamente.')

        # Redirigir al siguiente criterio o al resumen
        siguiente = Criterio.objects.filter(
            estandar=criterio.estandar,
            orden__gt=criterio.orden,
            activo=True,
            es_titulo=False
        ).first()

        if siguiente and request.POST.get('siguiente'):
            return redirect('evaluacion:evaluar_criterio', sede_pk=sede.pk, criterio_pk=siguiente.pk)

        return redirect('evaluacion:evaluacion_sede', sede_pk=sede.pk)

    # Obtener documento actual
    documento_actual = evaluacion.documentos.first()

    # Obtener plantilla del criterio si existe
    plantilla = criterio.plantillas.first()

    return render(request, 'evaluacion/evaluar_criterio.html', {
        'titulo': f'Evaluar: {criterio.numero}',
        'sede': sede,
        'criterio': criterio,
        'evaluacion': evaluacion,
        'documento': documento_actual,
        'plantilla': plantilla,
        'usuarios': usuarios,
        'bloqueado': bloqueado,
        'historial': evaluacion.historial.all()[:5],
    })


@login_required
@require_POST
def generar_documento_ia(request, pk):
    """Genera contenido de documento usando OpenAI API"""
    evaluacion = get_object_or_404(Evaluacion, pk=pk)

    if evaluacion.estado_documento == 'AP' and not request.user.es_administrador:
        return JsonResponse({'error': 'El documento está aprobado y no puede modificarse.'}, status=403)

    try:
        import openai
        from django.conf import settings

        prompt = request.POST.get('prompt', '')
        criterio_texto = evaluacion.criterio.texto

        # Construir prompt para la IA
        prompt_completo = f"""
        Eres un experto en habilitación de servicios de salud en Colombia,
        específicamente en la Resolución 3100 de 2019.

        Criterio a documentar:
        {criterio_texto}

        Instrucción del usuario: {prompt}

        Genera un documento profesional en formato HTML que demuestre el cumplimiento
        de este criterio. El documento debe ser formal, específico y aplicable a
        una institución prestadora de servicios de salud.
        """

        # Llamar a la API de OpenAI
        client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto en documentación de calidad en salud para Colombia."},
                {"role": "user", "content": prompt_completo}
            ],
            max_tokens=2000
        )

        contenido_generado = response.choices[0].message.content

        # Guardar o actualizar documento
        doc, created = DocumentoEvaluacion.objects.get_or_create(
            evaluacion=evaluacion,
            defaults={
                'nombre': f'Documento - {evaluacion.criterio.numero}',
                'contenido_html': contenido_generado,
                'generado_con_ia': True,
                'prompt_ia': prompt,
                'creado_por': request.user
            }
        )

        if not created:
            doc.contenido_html = contenido_generado
            doc.generado_con_ia = True
            doc.prompt_ia = prompt
            doc.save()

        # Actualizar estado del documento a "En Desarrollo"
        if evaluacion.estado_documento == 'NT':
            evaluacion.estado_documento = 'ED'
            evaluacion.save()

        return JsonResponse({
            'success': True,
            'contenido': contenido_generado
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Error al generar documento: {str(e)}'
        }, status=500)


@login_required
def iniciar_evaluacion_sede(request, sede_pk):
    """Inicia el proceso de evaluación para una sede, creando evaluaciones para todos los criterios"""
    sede = get_object_or_404(Sede, pk=sede_pk)

    if request.method == 'POST':
        # Obtener todos los criterios activos
        criterios = Criterio.objects.filter(activo=True, es_titulo=False)

        created_count = 0
        for criterio in criterios:
            _, created = Evaluacion.objects.get_or_create(
                sede=sede,
                criterio=criterio,
                defaults={'estado': 'PE', 'estado_documento': 'NT'}
            )
            if created:
                created_count += 1

        messages.success(request, f'Se iniciaron {created_count} evaluaciones para la sede {sede.nombre}.')
        return redirect('evaluacion:evaluacion_sede', sede_pk=sede.pk)

    # Contar criterios
    total_criterios = Criterio.objects.filter(activo=True, es_titulo=False).count()
    evaluaciones_existentes = Evaluacion.objects.filter(sede=sede).count()

    return render(request, 'evaluacion/iniciar_evaluacion.html', {
        'titulo': f'Iniciar Evaluación - {sede.nombre}',
        'sede': sede,
        'total_criterios': total_criterios,
        'evaluaciones_existentes': evaluaciones_existentes,
    })


# ===============================
# NUEVAS VISTAS DE EVALUACION POR ENTIDAD
# ===============================

@login_required
def dashboard_evaluacion_entidad(request):
    """Dashboard de evaluacion para la entidad del usuario"""
    if not request.user.entidad:
        messages.error(request, 'No tiene una entidad asignada.')
        return redirect('core:dashboard')

    entidad = request.user.entidad

    # Obtener servicios habilitados para esta entidad
    configuraciones = ConfiguracionEvaluacion.objects.filter(
        entidad=entidad,
        activo=True
    ).select_related('servicio', 'servicio__grupo')

    # Agrupar por grupo
    grupos_servicios = {}
    for config in configuraciones:
        grupo = config.servicio.grupo
        if grupo.id not in grupos_servicios:
            grupos_servicios[grupo.id] = {
                'grupo': grupo,
                'servicios': []
            }

        # Calcular progreso del servicio
        total_criterios = Criterio.objects.filter(
            estandar__grupo=grupo,
            activo=True,
            es_titulo=False
        ).count()

        evaluados = EvaluacionCriterio.objects.filter(
            entidad=entidad,
            criterio__estandar__grupo=grupo
        ).exclude(estado='P').count()

        porcentaje = round((evaluados / total_criterios * 100), 1) if total_criterios > 0 else 0

        grupos_servicios[grupo.id]['servicios'].append({
            'servicio': config.servicio,
            'total_criterios': total_criterios,
            'evaluados': evaluados,
            'porcentaje': porcentaje
        })

    # Calcular estadisticas generales
    total_criterios_entidad = 0
    total_evaluados = 0
    total_cumple = 0
    total_no_cumple = 0
    total_en_proceso = 0

    for grupo_data in grupos_servicios.values():
        for serv in grupo_data['servicios']:
            total_criterios_entidad += serv['total_criterios']
            total_evaluados += serv['evaluados']

    evaluaciones = EvaluacionCriterio.objects.filter(entidad=entidad)
    total_cumple = evaluaciones.filter(estado='C').count()
    total_no_cumple = evaluaciones.filter(estado='NC').count()
    total_en_proceso = evaluaciones.filter(en_proceso=True).count()

    return render(request, 'evaluacion/dashboard_entidad.html', {
        'titulo': f'Evaluacion - {entidad.razon_social}',
        'entidad': entidad,
        'grupos_servicios': grupos_servicios.values(),
        'total_criterios': total_criterios_entidad,
        'total_evaluados': total_evaluados,
        'total_cumple': total_cumple,
        'total_no_cumple': total_no_cumple,
        'total_en_proceso': total_en_proceso,
    })


@login_required
def tabla_criterios_estandar(request, estandar_pk):
    """Vista de tabla para evaluar criterios de un estandar"""
    if not request.user.entidad:
        messages.error(request, 'No tiene una entidad asignada.')
        return redirect('core:dashboard')

    entidad = request.user.entidad
    estandar = get_object_or_404(Estandar, pk=estandar_pk)

    # Verificar que la entidad tiene acceso a este estandar
    tiene_acceso = ConfiguracionEvaluacion.objects.filter(
        entidad=entidad,
        servicio__grupo=estandar.grupo,
        activo=True
    ).exists()

    # Los estandares del grupo 11.1 son obligatorios
    es_obligatorio = estandar.grupo.codigo.startswith('11.1')

    if not tiene_acceso and not es_obligatorio:
        messages.error(request, 'No tiene acceso a este estandar.')
        return redirect('evaluacion:dashboard_entidad')

    # Obtener criterios del estandar
    criterios = estandar.criterios.filter(activo=True, es_titulo=False).order_by('orden', 'numero')

    # Obtener o crear evaluaciones para cada criterio
    evaluaciones_data = []
    for criterio in criterios:
        evaluacion, created = EvaluacionCriterio.objects.get_or_create(
            entidad=entidad,
            criterio=criterio,
            defaults={'estado': 'P', 'modificado_por': request.user}
        )
        evaluaciones_data.append({
            'criterio': criterio,
            'evaluacion': evaluacion,
            'archivos': evaluacion.archivos_repositorio.all()
        })

    # Obtener usuarios de la entidad para asignar responsables
    usuarios_entidad = Usuario.objects.filter(entidad=entidad, is_active=True)

    return render(request, 'evaluacion/tabla_criterios.html', {
        'titulo': f'Evaluar: {estandar.nombre}',
        'entidad': entidad,
        'estandar': estandar,
        'evaluaciones_data': evaluaciones_data,
        'usuarios_entidad': usuarios_entidad,
        'estados': EvaluacionCriterio.ESTADOS,
    })


@login_required
@require_POST
def guardar_evaluacion_criterio(request):
    """API para guardar evaluacion de un criterio (AJAX)"""
    if not request.user.entidad:
        return JsonResponse({'error': 'No tiene entidad asignada'}, status=403)

    try:
        data = json.loads(request.body)
        evaluacion_id = data.get('evaluacion_id')
        campo = data.get('campo')
        valor = data.get('valor')

        evaluacion = get_object_or_404(
            EvaluacionCriterio,
            pk=evaluacion_id,
            entidad=request.user.entidad
        )

        # Actualizar el campo correspondiente
        if campo == 'estado':
            evaluacion.estado = valor
        elif campo == 'en_proceso':
            evaluacion.en_proceso = valor
        elif campo == 'responsable':
            if valor:
                evaluacion.responsable_id = valor
            else:
                evaluacion.responsable = None
        elif campo == 'comentarios':
            evaluacion.comentarios = valor

        evaluacion.modificado_por = request.user
        evaluacion.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Guardado correctamente'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def subir_archivo_criterio(request, evaluacion_pk):
    """Subir archivo al repositorio de un criterio"""
    if not request.user.entidad:
        return JsonResponse({'error': 'No tiene entidad asignada'}, status=403)

    evaluacion = get_object_or_404(
        EvaluacionCriterio,
        pk=evaluacion_pk,
        entidad=request.user.entidad
    )

    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No se envio ningun archivo'}, status=400)

    archivo = request.FILES['archivo']
    nombre = request.POST.get('nombre', archivo.name)
    descripcion = request.POST.get('descripcion', '')

    archivo_repo = ArchivoRepositorio.objects.create(
        evaluacion=evaluacion,
        archivo=archivo,
        nombre=nombre,
        descripcion=descripcion,
        subido_por=request.user
    )

    return JsonResponse({
        'success': True,
        'archivo': {
            'id': archivo_repo.id,
            'nombre': archivo_repo.nombre,
            'url': archivo_repo.archivo.url,
            'fecha': archivo_repo.fecha_subida.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
@require_POST
def eliminar_archivo_criterio(request, archivo_pk):
    """Eliminar archivo del repositorio"""
    if not request.user.entidad:
        return JsonResponse({'error': 'No tiene entidad asignada'}, status=403)

    archivo = get_object_or_404(
        ArchivoRepositorio,
        pk=archivo_pk,
        evaluacion__entidad=request.user.entidad
    )

    archivo.archivo.delete()
    archivo.delete()

    return JsonResponse({'success': True})


@login_required
def lista_estandares_evaluar(request):
    """Lista de estandares disponibles para evaluar"""
    if not request.user.entidad:
        messages.error(request, 'No tiene una entidad asignada.')
        return redirect('core:dashboard')

    entidad = request.user.entidad

    # Obtener grupos con sus estandares
    grupos = GrupoEstandar.objects.filter(activo=True).prefetch_related('estandares')

    # Verificar configuraciones de la entidad
    configuraciones = ConfiguracionEvaluacion.objects.filter(
        entidad=entidad,
        activo=True
    ).values_list('servicio__grupo_id', flat=True)

    estandares_disponibles = []

    for grupo in grupos:
        # Grupo 11.1 es obligatorio para todos
        es_obligatorio = grupo.codigo.startswith('11.1')

        if es_obligatorio or grupo.id in configuraciones:
            for estandar in grupo.estandares.filter(activo=True):
                # Calcular progreso
                total = estandar.criterios.filter(activo=True, es_titulo=False).count()
                evaluados = EvaluacionCriterio.objects.filter(
                    entidad=entidad,
                    criterio__estandar=estandar
                ).exclude(estado='P').count()

                estandares_disponibles.append({
                    'estandar': estandar,
                    'grupo': grupo,
                    'total': total,
                    'evaluados': evaluados,
                    'porcentaje': round((evaluados / total * 100), 1) if total > 0 else 0,
                    'es_obligatorio': es_obligatorio
                })

    return render(request, 'evaluacion/lista_estandares.html', {
        'titulo': 'Estandares a Evaluar',
        'entidad': entidad,
        'estandares': estandares_disponibles,
    })


# ===============================
# NUEVAS VISTAS PARA NAVEGACIÓN EN ÁRBOL POR SEDE
# ===============================

@login_required
def lista_sedes_evaluar(request):
    """Lista de sedes disponibles para evaluar"""
    if not request.user.entidad:
        messages.error(request, 'No tiene una entidad asignada.')
        return redirect('core:dashboard')

    entidad = request.user.entidad
    sedes = Sede.objects.filter(entidad=entidad, activa=True)

    # Calcular estadísticas por sede
    sedes_data = []
    for sede in sedes:
        # Obtener grupos habilitados para esta sede
        grupos_habilitados = ConfiguracionEvaluacionSede.objects.filter(
            sede=sede, activo=True
        ).select_related('grupo_estandar')

        # Contar criterios y evaluaciones
        total_criterios = 0
        evaluados = 0
        cumple = 0
        no_cumple = 0
        no_aplica = 0

        for config in grupos_habilitados:
            grupo = config.grupo_estandar
            criterios_grupo = Criterio.objects.filter(
                estandar__grupo=grupo,
                activo=True,
                es_titulo=False
            ).count()
            total_criterios += criterios_grupo

            evals = EvaluacionCriterio.objects.filter(
                sede=sede,
                criterio__estandar__grupo=grupo
            )
            evaluados += evals.exclude(estado='P').count()
            cumple += evals.filter(estado='C').count()
            no_cumple += evals.filter(estado='NC').count()
            no_aplica += evals.filter(estado='NA').count()

        # Porcentaje de cumplimiento (sobre criterios que aplican)
        criterios_aplican = total_criterios - no_aplica
        porcentaje = round((cumple / criterios_aplican * 100), 1) if criterios_aplican > 0 else 0

        sedes_data.append({
            'sede': sede,
            'total_criterios': total_criterios,
            'evaluados': evaluados,
            'cumple': cumple,
            'no_cumple': no_cumple,
            'no_aplica': no_aplica,
            'porcentaje': porcentaje,
            'grupos_habilitados': grupos_habilitados.count()
        })

    return render(request, 'evaluacion/sedes/lista.html', {
        'titulo': 'Sedes a Evaluar',
        'entidad': entidad,
        'sedes_data': sedes_data,
    })


@login_required
def sede_categorias(request, sede_pk):
    """
    Vista de categorías (grupos de estándares) para una sede.
    Estructura de árbol: Sede -> Categorías (11.1, 11.2, etc.)
    """
    sede = get_object_or_404(Sede, pk=sede_pk)

    # Verificar acceso
    if request.user.entidad != sede.entidad and request.user.rol != 'SUPER':
        messages.error(request, 'No tiene acceso a esta sede.')
        return redirect('evaluacion:sedes_evaluar')

    # Obtener grupos habilitados para esta sede
    configuraciones = ConfiguracionEvaluacionSede.objects.filter(
        sede=sede, activo=True
    ).select_related('grupo_estandar')

    # Si no hay configuración, crear la obligatoria (11.1)
    if not configuraciones.exists():
        ConfiguracionEvaluacionSede.crear_configuracion_obligatoria(sede, request.user)
        configuraciones = ConfiguracionEvaluacionSede.objects.filter(
            sede=sede, activo=True
        ).select_related('grupo_estandar')

    categorias_data = []
    total_criterios_sede = 0
    total_cumple_sede = 0
    total_no_cumple_sede = 0
    total_na_sede = 0
    total_pendiente_sede = 0

    for config in configuraciones:
        grupo = config.grupo_estandar

        # Contar criterios del grupo
        criterios_grupo = Criterio.objects.filter(
            estandar__grupo=grupo,
            activo=True,
            es_titulo=False
        )
        total_criterios = criterios_grupo.count()

        # Contar evaluaciones
        evals = EvaluacionCriterio.objects.filter(
            sede=sede,
            criterio__in=criterios_grupo
        )
        cumple = evals.filter(estado='C').count()
        no_cumple = evals.filter(estado='NC').count()
        no_aplica = evals.filter(estado='NA').count()
        pendiente = total_criterios - cumple - no_cumple - no_aplica

        # Acumular totales
        total_criterios_sede += total_criterios
        total_cumple_sede += cumple
        total_no_cumple_sede += no_cumple
        total_na_sede += no_aplica
        total_pendiente_sede += pendiente

        # Porcentaje de cumplimiento
        criterios_aplican = total_criterios - no_aplica
        porcentaje = round((cumple / criterios_aplican * 100), 1) if criterios_aplican > 0 else 0

        # Obtener subcategorías (estándares)
        estandares = Estandar.objects.filter(grupo=grupo, activo=True).order_by('orden')

        categorias_data.append({
            'grupo': grupo,
            'config': config,
            'estandares': estandares,
            'total_criterios': total_criterios,
            'cumple': cumple,
            'no_cumple': no_cumple,
            'no_aplica': no_aplica,
            'pendiente': pendiente,
            'porcentaje': porcentaje,
            'es_obligatorio': grupo.codigo == '11.1'
        })

    # Calcular porcentaje general
    criterios_aplican_sede = total_criterios_sede - total_na_sede
    porcentaje_general = round((total_cumple_sede / criterios_aplican_sede * 100), 1) if criterios_aplican_sede > 0 else 0

    return render(request, 'evaluacion/sedes/categorias.html', {
        'titulo': f'Evaluación - {sede.nombre}',
        'sede': sede,
        'categorias_data': categorias_data,
        'resumen': {
            'total_criterios': total_criterios_sede,
            'cumple': total_cumple_sede,
            'no_cumple': total_no_cumple_sede,
            'no_aplica': total_na_sede,
            'pendiente': total_pendiente_sede,
            'porcentaje': porcentaje_general
        }
    })


@login_required
def sede_subcategorias(request, sede_pk, grupo_pk):
    """
    Vista de subcategorías (estándares) dentro de una categoría.
    Estructura: Sede -> Categoría (11.1) -> Subcategorías (11.1.1, 11.1.2, etc.)
    """
    sede = get_object_or_404(Sede, pk=sede_pk)
    grupo = get_object_or_404(GrupoEstandar, pk=grupo_pk)

    # Verificar acceso
    if request.user.entidad != sede.entidad and request.user.rol != 'SUPER':
        messages.error(request, 'No tiene acceso a esta sede.')
        return redirect('evaluacion:sedes_evaluar')

    # Verificar que el grupo está habilitado para esta sede
    es_obligatorio = grupo.codigo == '11.1'
    config = ConfiguracionEvaluacionSede.objects.filter(
        sede=sede, grupo_estandar=grupo, activo=True
    ).first()

    if not es_obligatorio and not config:
        messages.error(request, 'Este grupo de criterios no está habilitado para esta sede.')
        return redirect('evaluacion:sede_categorias', sede_pk=sede.pk)

    # Obtener estándares del grupo
    estandares = Estandar.objects.filter(grupo=grupo, activo=True).order_by('orden')

    subcategorias_data = []
    for estandar in estandares:
        # Contar criterios
        criterios = Criterio.objects.filter(
            estandar=estandar,
            activo=True,
            es_titulo=False
        )
        total_criterios = criterios.count()

        # Contar evaluaciones
        evals = EvaluacionCriterio.objects.filter(
            sede=sede,
            criterio__in=criterios
        )
        cumple = evals.filter(estado='C').count()
        no_cumple = evals.filter(estado='NC').count()
        no_aplica = evals.filter(estado='NA').count()
        pendiente = total_criterios - cumple - no_cumple - no_aplica

        # Porcentaje
        criterios_aplican = total_criterios - no_aplica
        porcentaje = round((cumple / criterios_aplican * 100), 1) if criterios_aplican > 0 else 0

        subcategorias_data.append({
            'estandar': estandar,
            'total_criterios': total_criterios,
            'cumple': cumple,
            'no_cumple': no_cumple,
            'no_aplica': no_aplica,
            'pendiente': pendiente,
            'porcentaje': porcentaje
        })

    return render(request, 'evaluacion/sedes/subcategorias.html', {
        'titulo': f'{grupo.nombre}',
        'sede': sede,
        'grupo': grupo,
        'subcategorias_data': subcategorias_data,
        'es_obligatorio': es_obligatorio
    })


@login_required
def sede_criterios_estandar(request, sede_pk, estandar_pk):
    """
    Vista de criterios para evaluar dentro de un estándar.
    Estructura: Sede -> Categoría -> Subcategoría (Estándar) -> Criterios
    """
    sede = get_object_or_404(Sede, pk=sede_pk)
    estandar = get_object_or_404(Estandar, pk=estandar_pk)

    # Verificar acceso
    if request.user.entidad != sede.entidad and request.user.rol != 'SUPER':
        messages.error(request, 'No tiene acceso a esta sede.')
        return redirect('evaluacion:sedes_evaluar')

    # Obtener criterios del estándar (incluyendo títulos para estructura)
    criterios = Criterio.objects.filter(
        estandar=estandar,
        activo=True
    ).order_by('orden', 'numero')

    # Crear o obtener evaluaciones
    criterios_data = []
    for criterio in criterios:
        # Solo los criterios de tipo 'CRITERIO' son evaluables
        if criterio.tipo_criterio != 'CRITERIO':
            # Es un título o subtítulo, no requiere evaluación
            criterios_data.append({
                'criterio': criterio,
                'es_titulo': True,
                'tipo': criterio.tipo_criterio,
                'evaluacion': None
            })
        else:
            # Obtener o crear evaluación para criterios evaluables
            evaluacion, created = EvaluacionCriterio.objects.get_or_create(
                sede=sede,
                criterio=criterio,
                defaults={'estado': 'P', 'modificado_por': request.user}
            )
            criterios_data.append({
                'criterio': criterio,
                'es_titulo': False,
                'tipo': 'CRITERIO',
                'evaluacion': evaluacion,
                'archivos_count': evaluacion.cantidad_archivos
            })

    # Calcular resumen (solo criterios evaluables)
    evaluaciones = EvaluacionCriterio.objects.filter(
        sede=sede,
        criterio__estandar=estandar,
        criterio__tipo_criterio='CRITERIO'
    )
    total = evaluaciones.count()
    cumple = evaluaciones.filter(estado='C').count()
    no_cumple = evaluaciones.filter(estado='NC').count()
    no_aplica = evaluaciones.filter(estado='NA').count()
    pendiente = total - cumple - no_cumple - no_aplica

    criterios_aplican = total - no_aplica
    porcentaje = round((cumple / criterios_aplican * 100), 1) if criterios_aplican > 0 else 0

    # Obtener usuarios para asignar responsables
    usuarios_entidad = Usuario.objects.filter(entidad=sede.entidad, is_active=True)

    return render(request, 'evaluacion/sedes/criterios.html', {
        'titulo': f'{estandar.nombre}',
        'sede': sede,
        'estandar': estandar,
        'grupo': estandar.grupo,
        'criterios_data': criterios_data,
        'usuarios_entidad': usuarios_entidad,
        'estados': EvaluacionCriterio.ESTADOS,
        'resumen': {
            'total': total,
            'cumple': cumple,
            'no_cumple': no_cumple,
            'no_aplica': no_aplica,
            'pendiente': pendiente,
            'porcentaje': porcentaje
        }
    })


@login_required
def sede_configuracion(request, sede_pk):
    """
    Configuración de grupos de criterios habilitados para una sede.
    El grupo 11.1 es obligatorio y no se puede desactivar.
    """
    sede = get_object_or_404(Sede, pk=sede_pk)

    # Verificar acceso
    if request.user.entidad != sede.entidad and request.user.rol != 'SUPER':
        messages.error(request, 'No tiene acceso a esta sede.')
        return redirect('evaluacion:sedes_evaluar')

    # Obtener todos los grupos de estándares
    grupos = GrupoEstandar.objects.filter(activo=True).order_by('orden')

    if request.method == 'POST':
        grupos_seleccionados = request.POST.getlist('grupos')

        for grupo in grupos:
            es_obligatorio = grupo.codigo == '11.1'
            esta_seleccionado = str(grupo.id) in grupos_seleccionados

            if es_obligatorio:
                # Asegurar que el grupo obligatorio esté siempre activo
                ConfiguracionEvaluacionSede.objects.get_or_create(
                    sede=sede,
                    grupo_estandar=grupo,
                    defaults={'activo': True, 'activado_por': request.user}
                )
            else:
                config, created = ConfiguracionEvaluacionSede.objects.get_or_create(
                    sede=sede,
                    grupo_estandar=grupo,
                    defaults={'activo': esta_seleccionado, 'activado_por': request.user}
                )
                if not created and config.activo != esta_seleccionado:
                    config.activo = esta_seleccionado
                    config.activado_por = request.user
                    config.save()

        messages.success(request, 'Configuración guardada correctamente.')
        return redirect('evaluacion:sede_categorias', sede_pk=sede.pk)

    # Preparar datos de grupos
    grupos_data = []
    for grupo in grupos:
        config = ConfiguracionEvaluacionSede.objects.filter(
            sede=sede, grupo_estandar=grupo
        ).first()

        es_obligatorio = grupo.codigo == '11.1'
        activo = config.activo if config else es_obligatorio

        # Contar estándares y criterios
        estandares_count = Estandar.objects.filter(grupo=grupo, activo=True).count()
        criterios_count = Criterio.objects.filter(
            estandar__grupo=grupo,
            activo=True,
            es_titulo=False
        ).count()

        grupos_data.append({
            'grupo': grupo,
            'activo': activo,
            'es_obligatorio': es_obligatorio,
            'estandares_count': estandares_count,
            'criterios_count': criterios_count,
            'config': config
        })

    return render(request, 'evaluacion/sedes/configuracion.html', {
        'titulo': f'Configuración - {sede.nombre}',
        'sede': sede,
        'grupos_data': grupos_data
    })


@login_required
def ver_documentos_criterio(request, evaluacion_pk):
    """
    Vista separada para ver los documentos de un criterio.
    Se accede mediante "Ir a ver documentos".
    """
    evaluacion = get_object_or_404(EvaluacionCriterio, pk=evaluacion_pk)

    # Verificar acceso
    if request.user.entidad != evaluacion.sede.entidad and request.user.rol != 'SUPER':
        messages.error(request, 'No tiene acceso a estos documentos.')
        return redirect('core:dashboard')

    archivos = evaluacion.archivos_repositorio.all().order_by('-fecha_subida')

    return render(request, 'evaluacion/sedes/documentos_criterio.html', {
        'titulo': f'Documentos - {evaluacion.criterio.numero}',
        'evaluacion': evaluacion,
        'criterio': evaluacion.criterio,
        'sede': evaluacion.sede,
        'archivos': archivos
    })


@login_required
def resumen_evaluacion_sede(request, sede_pk):
    """
    Resumen de evaluación de una sede con conteo de C, NC, N/A.
    Solo para reportes, la evaluación se hace sobre criterios que aplican.
    """
    sede = get_object_or_404(Sede, pk=sede_pk)

    # Verificar acceso
    if request.user.entidad != sede.entidad and request.user.rol != 'SUPER':
        messages.error(request, 'No tiene acceso a esta sede.')
        return redirect('evaluacion:sedes_evaluar')

    # Obtener grupos habilitados
    configuraciones = ConfiguracionEvaluacionSede.objects.filter(
        sede=sede, activo=True
    ).select_related('grupo_estandar')

    resumen_grupos = []
    totales = {'criterios': 0, 'cumple': 0, 'no_cumple': 0, 'no_aplica': 0, 'pendiente': 0}

    for config in configuraciones:
        grupo = config.grupo_estandar

        # Calcular estadísticas del grupo
        evals = EvaluacionCriterio.objects.filter(
            sede=sede,
            criterio__estandar__grupo=grupo,
            criterio__es_titulo=False
        )

        total = Criterio.objects.filter(
            estandar__grupo=grupo,
            activo=True,
            es_titulo=False
        ).count()

        cumple = evals.filter(estado='C').count()
        no_cumple = evals.filter(estado='NC').count()
        no_aplica = evals.filter(estado='NA').count()
        pendiente = total - cumple - no_cumple - no_aplica

        # Porcentaje sobre criterios que aplican
        criterios_aplican = total - no_aplica
        porcentaje = round((cumple / criterios_aplican * 100), 1) if criterios_aplican > 0 else 0

        resumen_grupos.append({
            'grupo': grupo,
            'total': total,
            'cumple': cumple,
            'no_cumple': no_cumple,
            'no_aplica': no_aplica,
            'pendiente': pendiente,
            'porcentaje': porcentaje
        })

        # Acumular totales
        totales['criterios'] += total
        totales['cumple'] += cumple
        totales['no_cumple'] += no_cumple
        totales['no_aplica'] += no_aplica
        totales['pendiente'] += pendiente

    # Porcentaje general
    criterios_aplican = totales['criterios'] - totales['no_aplica']
    totales['porcentaje'] = round((totales['cumple'] / criterios_aplican * 100), 1) if criterios_aplican > 0 else 0

    return render(request, 'evaluacion/sedes/resumen.html', {
        'titulo': f'Resumen de Evaluación - {sede.nombre}',
        'sede': sede,
        'resumen_grupos': resumen_grupos,
        'totales': totales
    })


# ===============================
# APIS AJAX ACTUALIZADAS PARA SEDES
# ===============================

@login_required
@require_POST
def guardar_evaluacion_criterio_sede(request):
    """API para guardar evaluación de un criterio por SEDE (AJAX)"""
    try:
        data = json.loads(request.body)
        evaluacion_id = data.get('evaluacion_id')
        campo = data.get('campo')
        valor = data.get('valor')

        evaluacion = get_object_or_404(EvaluacionCriterio, pk=evaluacion_id)

        # Verificar acceso
        if request.user.entidad != evaluacion.sede.entidad and request.user.rol != 'SUPER':
            return JsonResponse({'error': 'No tiene acceso'}, status=403)

        # Actualizar el campo correspondiente
        if campo == 'estado':
            evaluacion.estado = valor
            evaluacion.fecha_evaluacion = timezone.now()
        elif campo == 'en_proceso':
            evaluacion.en_proceso = valor
        elif campo == 'responsable':
            if valor:
                evaluacion.responsable_id = valor
            else:
                evaluacion.responsable = None
        elif campo == 'comentarios':
            evaluacion.comentarios = valor
        elif campo == 'justificacion_na':
            evaluacion.justificacion_na = valor

        evaluacion.modificado_por = request.user
        evaluacion.save()

        return JsonResponse({
            'success': True,
            'mensaje': 'Guardado correctamente'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def subir_archivo_criterio_sede(request, evaluacion_pk):
    """Subir archivo al repositorio de un criterio (por SEDE)"""
    evaluacion = get_object_or_404(EvaluacionCriterio, pk=evaluacion_pk)

    # Verificar acceso
    if request.user.entidad != evaluacion.sede.entidad and request.user.rol != 'SUPER':
        return JsonResponse({'error': 'No tiene acceso'}, status=403)

    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No se envió ningún archivo'}, status=400)

    archivo = request.FILES['archivo']
    nombre = request.POST.get('nombre', archivo.name)
    descripcion = request.POST.get('descripcion', '')

    archivo_repo = ArchivoRepositorio.objects.create(
        evaluacion=evaluacion,
        archivo=archivo,
        nombre=nombre,
        descripcion=descripcion,
        subido_por=request.user
    )

    return JsonResponse({
        'success': True,
        'archivo': {
            'id': archivo_repo.id,
            'nombre': archivo_repo.nombre,
            'url': archivo_repo.archivo.url,
            'fecha': archivo_repo.fecha_subida.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
@require_POST
def eliminar_archivo_criterio_sede(request, archivo_pk):
    """Eliminar archivo del repositorio (por SEDE)"""
    archivo = get_object_or_404(ArchivoRepositorio, pk=archivo_pk)

    # Verificar acceso
    if request.user.entidad != archivo.evaluacion.sede.entidad and request.user.rol != 'SUPER':
        return JsonResponse({'error': 'No tiene acceso'}, status=403)

    archivo.archivo.delete()
    archivo.delete()

    return JsonResponse({'success': True})


@login_required
@xframe_options_sameorigin
def preview_archivo(request, archivo_pk):
    """
    Vista para previsualizar archivos en iframe (para auditores).
    Sirve el archivo con headers que permiten embedding en iframes del mismo origen.
    """
    archivo = get_object_or_404(ArchivoRepositorio, pk=archivo_pk)

    # Verificar acceso - debe pertenecer a la entidad del usuario
    if request.user.rol != 'SUPER':
        if request.user.entidad != archivo.evaluacion.sede.entidad:
            return HttpResponse('Acceso denegado', status=403)

    # Obtener el tipo MIME del archivo
    content_type, _ = mimetypes.guess_type(archivo.archivo.name)
    if not content_type:
        content_type = 'application/octet-stream'

    # Para PDFs e imágenes, servir inline (no como descarga)
    try:
        response = FileResponse(
            archivo.archivo.open('rb'),
            content_type=content_type
        )
        # Content-Disposition: inline permite ver en el navegador
        response['Content-Disposition'] = f'inline; filename="{archivo.nombre}"'
        # Deshabilitar cache para seguridad
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        return response
    except FileNotFoundError:
        return HttpResponse('Archivo no encontrado', status=404)
