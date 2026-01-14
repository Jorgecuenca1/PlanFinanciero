"""
Vistas del módulo documentos.
Gestión de documentos con integración de IA (OpenAI/ChatGPT).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from .models import ConfiguracionIA, PromptTemplate, SolicitudIA, NormativaReferencia


@login_required
def lista_documentos(request):
    """Lista de documentos generados"""
    from evaluacion.models import DocumentoEvaluacion

    if request.user.entidad:
        documentos = DocumentoEvaluacion.objects.filter(
            evaluacion__sede__entidad=request.user.entidad
        ).order_by('-fecha_creacion')
    else:
        documentos = DocumentoEvaluacion.objects.none()

    return render(request, 'documentos/lista.html', {
        'titulo': 'Documentos',
        'documentos': documentos,
    })


@login_required
def generar_con_ia(request):
    """Generar documento con IA"""
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        evaluacion_id = request.POST.get('evaluacion_id')

        if not prompt:
            messages.error(request, 'Debe proporcionar un prompt.')
            return redirect('documentos:generar_ia')

        # Obtener configuración de IA
        config = None
        if request.user.entidad:
            config = getattr(request.user.entidad, 'config_ia', None)

        # Usar API key de la entidad o la global
        api_key = settings.OPENAI_API_KEY
        if config and config.api_key_personalizada:
            api_key = config.api_key_personalizada

        if not api_key:
            messages.error(request, 'No hay API key de OpenAI configurada.')
            return redirect('documentos:generar_ia')

        # Crear solicitud
        solicitud = SolicitudIA.objects.create(
            usuario=request.user,
            entidad=request.user.entidad,
            prompt_enviado=prompt,
            estado='PROCESANDO'
        )

        try:
            import openai
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            modelo = 'gpt-4o' if config is None else config.modelo_preferido
            sistema_prompt = (
                'Eres un experto en habilitación de servicios de salud en Colombia, '
                'especializado en la Resolución 3100 de 2019.'
            )
            if config and config.prompt_sistema:
                sistema_prompt = config.prompt_sistema

            inicio = timezone.now()
            response = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": sistema_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000 if config is None else config.max_tokens,
                temperature=0.7 if config is None else float(config.temperatura)
            )
            fin = timezone.now()

            respuesta = response.choices[0].message.content
            solicitud.respuesta = respuesta
            solicitud.modelo_usado = modelo
            solicitud.tokens_prompt = response.usage.prompt_tokens
            solicitud.tokens_respuesta = response.usage.completion_tokens
            solicitud.tokens_total = response.usage.total_tokens
            solicitud.estado = 'COMPLETADA'
            solicitud.fecha_respuesta = fin
            solicitud.tiempo_procesamiento = (fin - inicio).total_seconds()
            solicitud.save()

            messages.success(request, 'Documento generado exitosamente.')

            return render(request, 'documentos/resultado_ia.html', {
                'titulo': 'Documento Generado',
                'solicitud': solicitud,
                'respuesta': respuesta,
            })

        except Exception as e:
            solicitud.estado = 'ERROR'
            solicitud.mensaje_error = str(e)
            solicitud.save()
            messages.error(request, f'Error al generar documento: {e}')
            return redirect('documentos:generar_ia')

    # GET - mostrar formulario
    prompts = PromptTemplate.objects.filter(activo=True)

    return render(request, 'documentos/generar_ia.html', {
        'titulo': 'Generar con IA',
        'prompts': prompts,
    })


@login_required
def mejorar_con_ia(request, documento_pk):
    """Mejorar documento existente con IA"""
    from evaluacion.models import DocumentoEvaluacion
    documento = get_object_or_404(DocumentoEvaluacion, pk=documento_pk)

    return render(request, 'documentos/mejorar_ia.html', {
        'titulo': 'Mejorar con IA',
        'documento': documento,
    })


@login_required
def lista_prompts(request):
    """Lista de plantillas de prompts"""
    prompts = PromptTemplate.objects.filter(activo=True)

    if request.user.entidad and request.user.rol != 'SUPER':
        prompts = prompts.filter(
            es_global=True
        ) | prompts.filter(entidad=request.user.entidad)

    return render(request, 'documentos/prompts/lista.html', {
        'titulo': 'Plantillas de Prompts',
        'prompts': prompts,
    })


@login_required
def crear_prompt(request):
    """Crear nueva plantilla de prompt"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        prompt = request.POST.get('prompt')

        PromptTemplate.objects.create(
            nombre=nombre,
            tipo=tipo,
            prompt=prompt,
            es_global=request.user.rol == 'SUPER',
            entidad=request.user.entidad if request.user.rol != 'SUPER' else None
        )

        messages.success(request, 'Plantilla creada correctamente.')
        return redirect('documentos:prompts')

    return render(request, 'documentos/prompts/form.html', {
        'titulo': 'Crear Plantilla de Prompt',
        'tipos': PromptTemplate.TIPOS_PROMPT,
    })


@login_required
def lista_normativas(request):
    """Lista de normativas de referencia"""
    normativas = NormativaReferencia.objects.filter(vigente=True)

    return render(request, 'documentos/normativas/lista.html', {
        'titulo': 'Normativas de Referencia',
        'normativas': normativas,
    })


@login_required
def historial_ia(request):
    """Historial de solicitudes a la IA"""
    if request.user.entidad:
        solicitudes = SolicitudIA.objects.filter(
            entidad=request.user.entidad
        ).order_by('-fecha_solicitud')
    else:
        solicitudes = SolicitudIA.objects.none()

    return render(request, 'documentos/historial_ia.html', {
        'titulo': 'Historial de IA',
        'solicitudes': solicitudes,
    })
