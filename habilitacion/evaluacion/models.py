"""
Modelos de Evaluación y Autoevaluación
Sistema de seguimiento del cumplimiento de criterios de habilitación
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Evaluacion(models.Model):
    """
    Evaluación de un criterio específico para una sede.
    Registra el estado de cumplimiento (C, NC, NA).
    """

    ESTADOS = [
        ('C', 'Cumple'),
        ('NC', 'No Cumple'),
        ('NA', 'No Aplica'),
        ('PE', 'Pendiente de evaluar'),
    ]

    ESTADOS_DOCUMENTO = [
        ('NT', 'No Trabajado'),
        ('ED', 'En Desarrollo'),
        ('AP', 'Aprobado'),
    ]

    # Relación con la sede y el criterio
    sede = models.ForeignKey(
        'entidades.Sede',
        on_delete=models.CASCADE,
        related_name='evaluaciones',
        verbose_name='Sede'
    )
    criterio = models.ForeignKey(
        'estandares.Criterio',
        on_delete=models.CASCADE,
        related_name='evaluaciones',
        verbose_name='Criterio'
    )
    servicio_habilitado = models.ForeignKey(
        'entidades.ServicioHabilitado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones',
        verbose_name='Servicio habilitado',
        help_text='Solo aplica para criterios de servicios específicos'
    )

    # Estado de cumplimiento
    estado = models.CharField('Estado', max_length=5, choices=ESTADOS, default='PE')
    estado_documento = models.CharField(
        'Estado del documento',
        max_length=5,
        choices=ESTADOS_DOCUMENTO,
        default='NT'
    )

    # Comentarios y observaciones
    comentarios = models.TextField('Comentarios', blank=True)
    justificacion_na = models.TextField(
        'Justificación No Aplica',
        blank=True,
        help_text='Obligatorio cuando el estado es NA'
    )

    # Responsables
    responsable_desarrollo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_desarrollo',
        verbose_name='Responsable de desarrollo'
    )
    responsable_calidad = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_calidad',
        verbose_name='Responsable de calidad'
    )
    responsable_aprobacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_aprobacion',
        verbose_name='Responsable de aprobación'
    )

    # Fechas
    fecha_evaluacion = models.DateTimeField('Fecha de evaluación', null=True, blank=True)
    fecha_aprobacion = models.DateTimeField('Fecha de aprobación', null=True, blank=True)
    fecha_vencimiento = models.DateField(
        'Fecha de vencimiento',
        null=True,
        blank=True,
        help_text='Para criterios con documentos que tienen fecha de vencimiento'
    )

    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_modificadas'
    )

    class Meta:
        verbose_name = 'Evaluación'
        verbose_name_plural = 'Evaluaciones'
        ordering = ['sede', 'criterio']
        unique_together = ['sede', 'criterio', 'servicio_habilitado']

    def __str__(self):
        return f"{self.sede.nombre} - {self.criterio.numero}: {self.get_estado_display()}"

    @property
    def esta_aprobado(self):
        """Indica si la evaluación está aprobada"""
        return self.estado_documento == 'AP'

    @property
    def puede_editar(self):
        """Indica si se puede editar la evaluación"""
        return self.estado_documento != 'AP'

    @property
    def esta_vencido(self):
        """Indica si el documento asociado está vencido"""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < timezone.now().date()

    def aprobar(self, usuario):
        """Aprueba la evaluación"""
        self.estado_documento = 'AP'
        self.responsable_aprobacion = usuario
        self.fecha_aprobacion = timezone.now()
        self.save()
        # Registrar en historial
        HistorialEvaluacion.objects.create(
            evaluacion=self,
            usuario=usuario,
            accion='APROBAR',
            descripcion='Evaluación aprobada'
        )

    def rechazar(self, usuario, motivo=''):
        """Rechaza la evaluación y la devuelve a desarrollo"""
        self.estado_documento = 'ED'
        self.save()
        HistorialEvaluacion.objects.create(
            evaluacion=self,
            usuario=usuario,
            accion='RECHAZAR',
            descripcion=f'Evaluación rechazada: {motivo}'
        )


class DocumentoEvaluacion(models.Model):
    """
    Documentos de soporte para cada evaluación.
    Pueden ser archivos Word editables o PDFs aprobados.
    """
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Evaluación'
    )
    nombre = models.CharField('Nombre del documento', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)

    # Contenido editable (HTML/texto enriquecido)
    contenido_html = models.TextField(
        'Contenido editable',
        blank=True,
        help_text='Contenido del documento en formato HTML editable'
    )

    # Archivo adjunto
    archivo = models.FileField(
        'Archivo',
        upload_to='evaluaciones/documentos/',
        blank=True,
        null=True
    )

    # Versión y estado
    version = models.PositiveIntegerField('Versión', default=1)
    es_version_final = models.BooleanField('Es versión final', default=False)

    # Generado con IA
    generado_con_ia = models.BooleanField(
        'Generado con IA',
        default=False,
        help_text='Indica si el documento fue generado o modificado con ayuda de IA'
    )
    prompt_ia = models.TextField(
        'Prompt IA',
        blank=True,
        help_text='Prompt utilizado para generar el documento con IA'
    )

    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos_creados'
    )

    class Meta:
        verbose_name = 'Documento de Evaluación'
        verbose_name_plural = 'Documentos de Evaluación'
        ordering = ['evaluacion', '-version']

    def __str__(self):
        return f"{self.nombre} v{self.version}"

    def crear_nueva_version(self, usuario):
        """Crea una nueva versión del documento"""
        nueva_version = DocumentoEvaluacion.objects.create(
            evaluacion=self.evaluacion,
            nombre=self.nombre,
            descripcion=self.descripcion,
            contenido_html=self.contenido_html,
            version=self.version + 1,
            creado_por=usuario
        )
        return nueva_version


class HistorialEvaluacion(models.Model):
    """
    Historial de cambios en las evaluaciones.
    Registra todas las modificaciones para auditoría.
    """

    ACCIONES = [
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('CAMBIAR_ESTADO', 'Cambio de estado'),
        ('APROBAR', 'Aprobación'),
        ('RECHAZAR', 'Rechazo'),
        ('ASIGNAR', 'Asignación de responsable'),
        ('ADJUNTAR', 'Adjuntar documento'),
        ('COMENTAR', 'Agregar comentario'),
    ]

    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name='Evaluación'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='historial_evaluaciones'
    )
    accion = models.CharField('Acción', max_length=20, choices=ACCIONES)
    descripcion = models.TextField('Descripción')
    estado_anterior = models.CharField('Estado anterior', max_length=5, blank=True)
    estado_nuevo = models.CharField('Estado nuevo', max_length=5, blank=True)
    datos_adicionales = models.JSONField('Datos adicionales', null=True, blank=True)
    fecha = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de Evaluación'
        verbose_name_plural = 'Historial de Evaluaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.evaluacion} - {self.accion} - {self.fecha}"


class PeriodoEvaluacion(models.Model):
    """
    Períodos de evaluación/vigencia para seguimiento.
    Permite agrupar evaluaciones por período.
    """
    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        related_name='periodos_evaluacion',
        verbose_name='Entidad'
    )
    nombre = models.CharField('Nombre del período', max_length=100)
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin')
    activo = models.BooleanField('Período activo', default=True)
    observaciones = models.TextField('Observaciones', blank=True)

    # Porcentajes de cumplimiento
    porcentaje_cumplimiento_general = models.DecimalField(
        'Porcentaje cumplimiento general',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Período de Evaluación'
        verbose_name_plural = 'Períodos de Evaluación'
        ordering = ['entidad', '-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.entidad.razon_social})"

    def calcular_porcentaje_cumplimiento(self):
        """Calcula el porcentaje de cumplimiento del período"""
        from django.db.models import Count, Q

        sedes = self.entidad.sedes.filter(activa=True)
        total_evaluaciones = Evaluacion.objects.filter(
            sede__in=sedes,
            fecha_evaluacion__gte=self.fecha_inicio,
            fecha_evaluacion__lte=self.fecha_fin
        ).exclude(estado='PE').count()

        if total_evaluaciones == 0:
            return 0

        cumple = Evaluacion.objects.filter(
            sede__in=sedes,
            fecha_evaluacion__gte=self.fecha_inicio,
            fecha_evaluacion__lte=self.fecha_fin,
            estado='C'
        ).count()

        no_aplica = Evaluacion.objects.filter(
            sede__in=sedes,
            fecha_evaluacion__gte=self.fecha_inicio,
            fecha_evaluacion__lte=self.fecha_fin,
            estado='NA'
        ).count()

        evaluables = total_evaluaciones - no_aplica
        if evaluables == 0:
            return 100

        porcentaje = (cumple / evaluables) * 100
        self.porcentaje_cumplimiento_general = round(porcentaje, 2)
        self.save(update_fields=['porcentaje_cumplimiento_general'])
        return self.porcentaje_cumplimiento_general


class ResumenCumplimiento(models.Model):
    """
    Resumen de cumplimiento por estándar/grupo para una sede.
    Facilita la generación de reportes y dashboards.
    """
    sede = models.ForeignKey(
        'entidades.Sede',
        on_delete=models.CASCADE,
        related_name='resumenes_cumplimiento',
        verbose_name='Sede'
    )
    periodo = models.ForeignKey(
        PeriodoEvaluacion,
        on_delete=models.CASCADE,
        related_name='resumenes',
        verbose_name='Período',
        null=True,
        blank=True
    )

    # Puede ser por grupo o por estándar
    grupo_estandar = models.ForeignKey(
        'estandares.GrupoEstandar',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='resumenes_cumplimiento'
    )
    estandar = models.ForeignKey(
        'estandares.Estandar',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='resumenes_cumplimiento'
    )
    servicio = models.ForeignKey(
        'estandares.Servicio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='resumenes_cumplimiento'
    )

    # Contadores
    total_criterios = models.PositiveIntegerField('Total criterios', default=0)
    criterios_cumple = models.PositiveIntegerField('Criterios que cumplen', default=0)
    criterios_no_cumple = models.PositiveIntegerField('Criterios que no cumplen', default=0)
    criterios_no_aplica = models.PositiveIntegerField('Criterios no aplica', default=0)
    criterios_pendientes = models.PositiveIntegerField('Criterios pendientes', default=0)

    # Porcentaje calculado
    porcentaje_cumplimiento = models.DecimalField(
        'Porcentaje de cumplimiento',
        max_digits=5,
        decimal_places=2,
        default=0
    )

    fecha_calculo = models.DateTimeField('Fecha de cálculo', auto_now=True)

    class Meta:
        verbose_name = 'Resumen de Cumplimiento'
        verbose_name_plural = 'Resúmenes de Cumplimiento'
        ordering = ['sede', 'grupo_estandar', 'estandar']

    def __str__(self):
        referencia = self.grupo_estandar or self.estandar or self.servicio
        return f"{self.sede.nombre} - {referencia}: {self.porcentaje_cumplimiento}%"

    def calcular(self):
        """Calcula los valores del resumen"""
        from django.db.models import Q

        filtro_base = Q(sede=self.sede)

        if self.estandar:
            filtro_base &= Q(criterio__estandar=self.estandar)
        elif self.grupo_estandar:
            filtro_base &= Q(criterio__estandar__grupo=self.grupo_estandar)
        elif self.servicio:
            filtro_base &= Q(criterio__estandar_servicio__servicio=self.servicio)

        evaluaciones = Evaluacion.objects.filter(filtro_base)

        self.total_criterios = evaluaciones.count()
        self.criterios_cumple = evaluaciones.filter(estado='C').count()
        self.criterios_no_cumple = evaluaciones.filter(estado='NC').count()
        self.criterios_no_aplica = evaluaciones.filter(estado='NA').count()
        self.criterios_pendientes = evaluaciones.filter(estado='PE').count()

        evaluables = self.total_criterios - self.criterios_no_aplica
        if evaluables > 0:
            self.porcentaje_cumplimiento = round((self.criterios_cumple / evaluables) * 100, 2)
        else:
            self.porcentaje_cumplimiento = 100 if self.total_criterios > 0 else 0

        self.save()


class EvaluacionCriterio(models.Model):
    """
    Evaluación de cada criterio por SEDE.
    Sistema simplificado para evaluación directa desde tabla.
    La evaluación se hace sobre criterios que aplican a cada sede específica.
    """

    ESTADOS = [
        ('P', 'Pendiente'),
        ('C', 'Cumple'),
        ('NC', 'No Cumple'),
        ('NA', 'No Aplica'),
    ]

    # Relación con la SEDE y el criterio
    sede = models.ForeignKey(
        'entidades.Sede',
        on_delete=models.CASCADE,
        related_name='evaluaciones_criterios',
        verbose_name='Sede'
    )
    criterio = models.ForeignKey(
        'estandares.Criterio',
        on_delete=models.CASCADE,
        related_name='evaluaciones_sede',
        verbose_name='Criterio'
    )

    # Estado de cumplimiento
    estado = models.CharField(
        'Estado',
        max_length=2,
        choices=ESTADOS,
        default='P'
    )

    # En proceso de trabajo
    en_proceso = models.BooleanField(
        'En proceso',
        default=False,
        help_text='Indica si se está trabajando activamente en este criterio'
    )

    # Responsable asignado
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='criterios_asignados',
        verbose_name='Responsable'
    )

    # Comentarios
    comentarios = models.TextField('Comentarios', blank=True)

    # Justificación cuando es N/A
    justificacion_na = models.TextField(
        'Justificación No Aplica',
        blank=True,
        help_text='Obligatorio cuando el estado es NA'
    )

    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)
    fecha_evaluacion = models.DateTimeField('Fecha de evaluación', null=True, blank=True)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_criterios_modificadas'
    )

    class Meta:
        verbose_name = 'Evaluación de Criterio'
        verbose_name_plural = 'Evaluaciones de Criterios'
        unique_together = ['sede', 'criterio']
        ordering = ['sede', 'criterio__orden']

    def __str__(self):
        return f"{self.sede.nombre} - {self.criterio.numero}: {self.get_estado_display()}"

    @property
    def tiene_archivos(self):
        """Indica si tiene archivos adjuntos"""
        return self.archivos_repositorio.exists()

    @property
    def cantidad_archivos(self):
        """Retorna la cantidad de archivos adjuntos"""
        return self.archivos_repositorio.count()

    @property
    def entidad(self):
        """Acceso a la entidad a través de la sede"""
        return self.sede.entidad


class ArchivoRepositorio(models.Model):
    """
    Repositorio de archivos por evaluación de criterio.
    Permite múltiples archivos por criterio.
    """
    evaluacion = models.ForeignKey(
        EvaluacionCriterio,
        on_delete=models.CASCADE,
        related_name='archivos_repositorio',
        verbose_name='Evaluación'
    )
    archivo = models.FileField(
        'Archivo',
        upload_to='repositorio/%Y/%m/'
    )
    nombre = models.CharField('Nombre', max_length=255)
    descripcion = models.TextField('Descripción', blank=True)

    # Auditoría
    fecha_subida = models.DateTimeField('Fecha de subida', auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='archivos_subidos_repositorio'
    )

    class Meta:
        verbose_name = 'Archivo de Repositorio'
        verbose_name_plural = 'Archivos de Repositorio'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.nombre} - {self.evaluacion.criterio.numero}"

    @property
    def extension(self):
        """Retorna la extensión del archivo"""
        import os
        return os.path.splitext(self.archivo.name)[1].lower()

    @property
    def es_imagen(self):
        """Indica si el archivo es una imagen"""
        return self.extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    @property
    def es_pdf(self):
        """Indica si el archivo es un PDF"""
        return self.extension == '.pdf'

    @property
    def es_word(self):
        """Indica si el archivo es un documento Word"""
        return self.extension in ['.doc', '.docx']

    @property
    def es_excel(self):
        """Indica si el archivo es un documento Excel"""
        return self.extension in ['.xls', '.xlsx']

    @property
    def es_previsualizable(self):
        """Indica si el archivo se puede previsualizar en el navegador"""
        return self.es_imagen or self.es_pdf or self.es_word or self.es_excel

    @property
    def tipo_archivo(self):
        """Retorna el tipo de archivo para el visor"""
        if self.es_pdf:
            return 'pdf'
        elif self.es_imagen:
            return 'imagen'
        elif self.es_word:
            return 'word'
        elif self.es_excel:
            return 'excel'
        return 'otro'
