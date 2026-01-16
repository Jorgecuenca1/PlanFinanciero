"""
Vistas del módulo entidades.
Gestión de entidades prestadoras de servicios de salud y sedes.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import EntidadPrestadora, Sede, ServicioHabilitado, DocumentoEntidad, TipoPrestador, Departamento, Municipio, ConfiguracionEvaluacionSede
from estandares.models import Servicio, GrupoEstandar
from usuarios.models import Usuario
import secrets
import string


@login_required
def lista_entidades(request):
    """Lista de entidades prestadoras"""
    if request.user.rol == 'SUPER':
        entidades = EntidadPrestadora.objects.all()
    else:
        entidades = EntidadPrestadora.objects.filter(pk=request.user.entidad_id)

    return render(request, 'entidades/lista.html', {
        'titulo': 'Entidades Prestadoras',
        'entidades': entidades,
    })


@login_required
def crear_entidad(request):
    """Crear nueva entidad"""
    if request.user.rol != 'SUPER':
        messages.error(request, 'No tiene permisos para esta acción.')
        return redirect('entidades:lista')

    tipos_prestador = TipoPrestador.objects.filter(activo=True)
    departamentos = Departamento.objects.all().order_by('nombre')
    municipios = Municipio.objects.all().order_by('nombre')

    if request.method == 'POST':
        try:
            tipo_prestador = get_object_or_404(TipoPrestador, pk=request.POST.get('tipo_prestador'))
            departamento = get_object_or_404(Departamento, pk=request.POST.get('departamento'))
            municipio = get_object_or_404(Municipio, pk=request.POST.get('municipio'))

            entidad = EntidadPrestadora.objects.create(
                tipo_prestador=tipo_prestador,
                razon_social=request.POST.get('razon_social'),
                nombre_comercial=request.POST.get('nombre_comercial') or '',
                nit=request.POST.get('nit'),
                digito_verificacion=request.POST.get('digito_verificacion'),
                codigo_reps=request.POST.get('codigo_reps') or None,
                representante_legal=request.POST.get('representante_legal'),
                documento_representante=request.POST.get('documento_representante'),
                departamento=departamento,
                municipio=municipio,
                direccion=request.POST.get('direccion'),
                telefono=request.POST.get('telefono'),
                email=request.POST.get('email'),
                sitio_web=request.POST.get('sitio_web') or '',
                gerente=request.POST.get('gerente') or '',
                responsable_calidad=request.POST.get('responsable_calidad') or '',
                estado=request.POST.get('estado', 'EN_PROCESO'),
                creado_por=request.user,
            )
            messages.success(request, f'Entidad "{entidad.razon_social}" creada exitosamente.')
            return redirect('entidades:detalle', pk=entidad.pk)
        except Exception as e:
            messages.error(request, f'Error al crear la entidad: {str(e)}')

    return render(request, 'entidades/form.html', {
        'titulo': 'Crear Entidad',
        'tipos_prestador': tipos_prestador,
        'departamentos': departamentos,
        'municipios': municipios,
    })


@login_required
def detalle_entidad(request, pk):
    """Detalle de una entidad"""
    entidad = get_object_or_404(EntidadPrestadora, pk=pk)

    return render(request, 'entidades/detalle.html', {
        'titulo': entidad.razon_social,
        'entidad': entidad,
        'sedes': entidad.sedes.all(),
    })


@login_required
def editar_entidad(request, pk):
    """Editar entidad existente"""
    entidad = get_object_or_404(EntidadPrestadora, pk=pk)
    tipos_prestador = TipoPrestador.objects.filter(activo=True)
    departamentos = Departamento.objects.all().order_by('nombre')
    municipios = Municipio.objects.all().order_by('nombre')

    if request.method == 'POST':
        try:
            tipo_prestador = get_object_or_404(TipoPrestador, pk=request.POST.get('tipo_prestador'))
            departamento = get_object_or_404(Departamento, pk=request.POST.get('departamento'))
            municipio = get_object_or_404(Municipio, pk=request.POST.get('municipio'))

            entidad.tipo_prestador = tipo_prestador
            entidad.razon_social = request.POST.get('razon_social')
            entidad.nombre_comercial = request.POST.get('nombre_comercial') or ''
            entidad.nit = request.POST.get('nit')
            entidad.digito_verificacion = request.POST.get('digito_verificacion')
            entidad.codigo_reps = request.POST.get('codigo_reps') or None
            entidad.representante_legal = request.POST.get('representante_legal')
            entidad.documento_representante = request.POST.get('documento_representante')
            entidad.departamento = departamento
            entidad.municipio = municipio
            entidad.direccion = request.POST.get('direccion')
            entidad.telefono = request.POST.get('telefono')
            entidad.email = request.POST.get('email')
            entidad.sitio_web = request.POST.get('sitio_web') or ''
            entidad.gerente = request.POST.get('gerente') or ''
            entidad.responsable_calidad = request.POST.get('responsable_calidad') or ''
            entidad.estado = request.POST.get('estado', 'EN_PROCESO')
            entidad.save()
            messages.success(request, f'Entidad "{entidad.razon_social}" actualizada exitosamente.')
            return redirect('entidades:detalle', pk=entidad.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar la entidad: {str(e)}')

    return render(request, 'entidades/form.html', {
        'titulo': 'Editar Entidad',
        'entidad': entidad,
        'tipos_prestador': tipos_prestador,
        'departamentos': departamentos,
        'municipios': municipios,
    })


@login_required
def lista_sedes(request, pk):
    """Lista de sedes de una entidad"""
    entidad = get_object_or_404(EntidadPrestadora, pk=pk)
    sedes = Sede.objects.filter(entidad=entidad)

    return render(request, 'entidades/sedes/lista.html', {
        'titulo': f'Sedes de {entidad.razon_social}',
        'entidad': entidad,
        'sedes': sedes,
    })


@login_required
def crear_sede(request, entidad_pk):
    """Crear nueva sede"""
    entidad = get_object_or_404(EntidadPrestadora, pk=entidad_pk)
    departamentos = Departamento.objects.all()
    municipios = Municipio.objects.all()

    if request.method == 'POST':
        try:
            municipio_id = request.POST.get('municipio')
            municipio = Municipio.objects.get(pk=municipio_id) if municipio_id else None

            sede = Sede.objects.create(
                entidad=entidad,
                nombre=request.POST.get('nombre'),
                codigo_reps_sede=request.POST.get('codigo_reps', ''),
                departamento=municipio.departamento if municipio else entidad.departamento,
                municipio=municipio or entidad.municipio,
                direccion=request.POST.get('direccion', ''),
                telefono=request.POST.get('telefono', ''),
                email=request.POST.get('email', ''),
                activa='activo' in request.POST,
            )
            # Crear configuración obligatoria (grupo 11.1)
            ConfiguracionEvaluacionSede.crear_configuracion_obligatoria(sede, request.user)
            messages.success(request, f'Sede "{sede.nombre}" creada exitosamente.')
            return redirect('entidades:detalle', pk=entidad.pk)
        except Exception as e:
            messages.error(request, f'Error al crear la sede: {str(e)}')

    return render(request, 'entidades/sedes/form.html', {
        'titulo': 'Crear Sede',
        'entidad': entidad,
        'departamentos': departamentos,
        'municipios': municipios,
    })


@login_required
def detalle_sede(request, pk):
    """Detalle de una sede"""
    sede = get_object_or_404(Sede, pk=pk)

    return render(request, 'entidades/sedes/detalle.html', {
        'titulo': sede.nombre,
        'sede': sede,
        'servicios': sede.servicios_habilitados.all(),
    })


@login_required
def editar_sede(request, pk):
    """Editar sede existente"""
    sede = get_object_or_404(Sede, pk=pk)
    departamentos = Departamento.objects.all()
    municipios = Municipio.objects.all()

    if request.method == 'POST':
        try:
            municipio_id = request.POST.get('municipio')
            municipio = Municipio.objects.get(pk=municipio_id) if municipio_id else None

            sede.nombre = request.POST.get('nombre')
            sede.codigo_reps_sede = request.POST.get('codigo_reps', '')
            if municipio:
                sede.departamento = municipio.departamento
                sede.municipio = municipio
            sede.direccion = request.POST.get('direccion', '')
            sede.telefono = request.POST.get('telefono', '')
            sede.email = request.POST.get('email', '')
            sede.activa = 'activo' in request.POST
            sede.save()
            messages.success(request, f'Sede "{sede.nombre}" actualizada exitosamente.')
            return redirect('entidades:detalle', pk=sede.entidad.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar la sede: {str(e)}')

    return render(request, 'entidades/sedes/form.html', {
        'titulo': 'Editar Sede',
        'sede': sede,
        'departamentos': departamentos,
        'municipios': municipios,
    })


@login_required
def servicios_habilitados(request, pk):
    """Servicios habilitados de una entidad"""
    entidad = get_object_or_404(EntidadPrestadora, pk=pk)
    servicios = ServicioHabilitado.objects.filter(sede__entidad=entidad)

    return render(request, 'entidades/servicios.html', {
        'titulo': f'Servicios de {entidad.razon_social}',
        'entidad': entidad,
        'servicios': servicios,
    })


@login_required
def documentos_entidad(request, pk):
    """Documentos de una entidad"""
    entidad = get_object_or_404(EntidadPrestadora, pk=pk)
    documentos = DocumentoEntidad.objects.filter(entidad=entidad)

    return render(request, 'entidades/documentos.html', {
        'titulo': f'Documentos de {entidad.razon_social}',
        'entidad': entidad,
        'documentos': documentos,
    })


def generar_password(longitud=12):
    """Genera una contraseña aleatoria segura"""
    caracteres = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))


@login_required
def crear_entidad_con_usuario(request):
    """Crear nueva entidad con usuario automático"""
    if request.user.rol != 'SUPER':
        messages.error(request, 'No tiene permisos para esta accion.')
        return redirect('entidades:lista')

    tipos_prestador = TipoPrestador.objects.filter(activo=True)
    departamentos = Departamento.objects.all().order_by('nombre')
    municipios = Municipio.objects.all().order_by('nombre')

    if request.method == 'POST':
        try:
            tipo_prestador = get_object_or_404(TipoPrestador, pk=request.POST.get('tipo_prestador'))
            departamento = get_object_or_404(Departamento, pk=request.POST.get('departamento'))
            municipio = get_object_or_404(Municipio, pk=request.POST.get('municipio'))

            email = request.POST.get('email')

            # Crear entidad
            entidad = EntidadPrestadora.objects.create(
                tipo_prestador=tipo_prestador,
                razon_social=request.POST.get('razon_social'),
                nombre_comercial=request.POST.get('nombre_comercial') or '',
                nit=request.POST.get('nit'),
                digito_verificacion=request.POST.get('digito_verificacion'),
                codigo_reps=request.POST.get('codigo_reps') or None,
                representante_legal=request.POST.get('representante_legal'),
                documento_representante=request.POST.get('documento_representante'),
                departamento=departamento,
                municipio=municipio,
                direccion=request.POST.get('direccion'),
                telefono=request.POST.get('telefono'),
                email=email,
                sitio_web=request.POST.get('sitio_web') or '',
                gerente=request.POST.get('gerente') or '',
                responsable_calidad=request.POST.get('responsable_calidad') or '',
                estado='EN_PROCESO',
                creado_por=request.user,
            )

            # Crear usuario con email como username
            password = generar_password()
            usuario = Usuario.objects.create_user(
                username=email,
                email=email,
                password=password,
                nombres=entidad.razon_social[:50],
                apellidos='',
                rol='ADMIN',
                entidad=entidad,
                activo=True
            )

            # Crear sede principal automaticamente
            sede_principal = Sede.objects.create(
                entidad=entidad,
                nombre='Sede Principal',
                tipo='PRINCIPAL',
                departamento=departamento,
                municipio=municipio,
                direccion=request.POST.get('direccion'),
                telefono=request.POST.get('telefono'),
                email=email,
                activa=True
            )

            # Crear configuracion obligatoria (grupo 11.1) para la sede principal
            ConfiguracionEvaluacionSede.crear_configuracion_obligatoria(sede_principal, request.user)

            messages.success(
                request,
                f'Entidad "{entidad.razon_social}" creada con sede principal. '
                f'Usuario: {email} | Password: {password}'
            )
            return redirect('entidades:detalle', pk=entidad.pk)

        except Exception as e:
            messages.error(request, f'Error al crear la entidad: {str(e)}')

    return render(request, 'entidades/form_con_usuario.html', {
        'titulo': 'Crear Entidad con Usuario',
        'tipos_prestador': tipos_prestador,
        'departamentos': departamentos,
        'municipios': municipios,
    })


@login_required
def configuracion_servicios(request, pk):
    """
    Redirige a la configuracion por sede.
    La configuracion de grupos de criterios ahora se hace por SEDE, no por entidad.
    """
    entidad = get_object_or_404(EntidadPrestadora, pk=pk)

    if request.user.rol != 'SUPER' and request.user.entidad_id != pk:
        messages.error(request, 'No tiene permisos para esta accion.')
        return redirect('entidades:lista')

    # Redirigir a la lista de sedes para que el usuario seleccione cual configurar
    sedes = entidad.sedes.filter(activa=True)

    if sedes.count() == 1:
        # Si solo hay una sede, redirigir directamente a su configuracion
        return redirect('evaluacion:sede_configuracion', sede_pk=sedes.first().pk)

    # Si hay varias sedes, mostrar lista para seleccionar
    messages.info(request, 'Seleccione una sede para configurar los grupos de criterios a evaluar.')
    return redirect('entidades:sedes', pk=pk)
