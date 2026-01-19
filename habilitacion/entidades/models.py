"""
Modelos de Entidades Prestadoras de Servicios de Salud
Gestión de entidades, sedes, servicios habilitados y vigencias
Basado en la Resolución 3100 de 2019
"""

from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class TipoPrestador(models.Model):
    """
    Tipos de prestadores según la Resolución 3100 de 2019:
    - IPS: Institución Prestadora de Servicios de Salud
    - Profesionales Independientes
    - Prestación de Servicios Asistenciales
    - Objeto Social Diferente
    """
    codigo = models.CharField('Código', max_length=10, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Tipo de Prestador'
        verbose_name_plural = 'Tipos de Prestador'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    """Departamentos de Colombia para ubicación geográfica"""
    codigo = models.CharField('Código DANE', max_length=2, unique=True)
    nombre = models.CharField('Nombre', max_length=100)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    """Municipios de Colombia para ubicación geográfica"""
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='municipios'
    )
    codigo = models.CharField('Código DANE', max_length=5, unique=True)
    nombre = models.CharField('Nombre', max_length=100)

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['departamento__nombre', 'nombre']

    def __str__(self):
        return f"{self.nombre}, {self.departamento.nombre}"


class EntidadPrestadora(models.Model):
    """
    Entidad Prestadora de Servicios de Salud.
    Puede tener múltiples sedes y servicios habilitados.
    """

    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('EN_PROCESO', 'En proceso de habilitación'),
    ]

    # Información básica
    tipo_prestador = models.ForeignKey(
        TipoPrestador,
        on_delete=models.PROTECT,
        verbose_name='Tipo de prestador'
    )
    razon_social = models.CharField('Razón social', max_length=300)
    nombre_comercial = models.CharField('Nombre comercial', max_length=300, blank=True)
    nit = models.CharField('NIT', max_length=20, unique=True)
    digito_verificacion = models.CharField('Dígito de verificación', max_length=1)
    codigo_reps = models.CharField('Código REPS', max_length=20, unique=True, blank=True, null=True)

    # Representante legal
    representante_legal = models.CharField('Representante legal', max_length=200)
    documento_representante = models.CharField('Documento representante', max_length=20)

    # Ubicación sede principal
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        verbose_name='Departamento'
    )
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        verbose_name='Municipio'
    )
    direccion = models.CharField('Dirección', max_length=300)
    telefono = models.CharField('Teléfono', max_length=50)
    email = models.EmailField('Correo electrónico')
    sitio_web = models.URLField('Sitio web', blank=True)

    # Logo e imagen
    logo = models.ImageField('Logo', upload_to='entidades/logos/', blank=True, null=True)

    # Información de gestión
    gerente = models.CharField('Gerente/Director', max_length=200, blank=True)
    responsable_calidad = models.CharField('Responsable de calidad', max_length=200, blank=True)

    # Estado y vigencia
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='EN_PROCESO')
    fecha_inscripcion_reps = models.DateField('Fecha inscripción REPS', null=True, blank=True)
    fecha_vencimiento_habilitacion = models.DateField('Fecha vencimiento habilitación', null=True, blank=True)

    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entidades_creadas'
    )

    class Meta:
        verbose_name = 'Entidad Prestadora'
        verbose_name_plural = 'Entidades Prestadoras'
        ordering = ['razon_social']

    def __str__(self):
        return f"{self.razon_social} ({self.codigo_reps or 'Sin REPS'})"

    @property
    def nombre_display(self):
        """Nombre para mostrar (comercial si existe, sino razón social)"""
        return self.nombre_comercial or self.razon_social

    @property
    def nit_completo(self):
        """NIT con dígito de verificación"""
        return f"{self.nit}-{self.digito_verificacion}"

    @property
    def dias_para_vencimiento(self):
        """Días restantes para el vencimiento de la habilitación"""
        if not self.fecha_vencimiento_habilitacion:
            return None
        delta = self.fecha_vencimiento_habilitacion - timezone.now().date()
        return delta.days

    @property
    def esta_por_vencer(self):
        """Indica si la habilitación está próxima a vencer"""
        dias = self.dias_para_vencimiento
        if dias is None:
            return False
        return 0 < dias <= settings.HABILITACION_CONFIG['DIAS_ALERTA_VENCIMIENTO']

    @property
    def esta_vencida(self):
        """Indica si la habilitación está vencida"""
        dias = self.dias_para_vencimiento
        if dias is None:
            return False
        return dias <= 0

    def calcular_fecha_vencimiento(self):
        """Calcula la fecha de vencimiento basada en la fecha de inscripción"""
        if self.fecha_inscripcion_reps:
            vigencia_dias = settings.HABILITACION_CONFIG['VIGENCIA_DIAS']
            self.fecha_vencimiento_habilitacion = self.fecha_inscripcion_reps + timedelta(days=vigencia_dias)
            self.save(update_fields=['fecha_vencimiento_habilitacion'])


class Sede(models.Model):
    """
    Sede de una entidad prestadora.
    Cada sede puede tener diferentes servicios habilitados.
    """

    TIPOS_SEDE = [
        ('PRINCIPAL', 'Sede Principal'),
        ('SECUNDARIA', 'Sede Secundaria'),
        ('AMBULANCIA', 'Base de ambulancia'),
        ('MOVIL', 'Unidad móvil'),
    ]

    entidad = models.ForeignKey(
        EntidadPrestadora,
        on_delete=models.CASCADE,
        related_name='sedes',
        verbose_name='Entidad'
    )
    nombre = models.CharField('Nombre de la sede', max_length=200)
    tipo = models.CharField('Tipo de sede', max_length=20, choices=TIPOS_SEDE, default='SECUNDARIA')
    codigo_reps_sede = models.CharField('Código REPS Sede', max_length=30, blank=True)

    # Ubicación
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        verbose_name='Departamento'
    )
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        verbose_name='Municipio'
    )
    direccion = models.CharField('Dirección', max_length=300)
    telefono = models.CharField('Teléfono', max_length=50)
    email = models.EmailField('Correo electrónico', blank=True)

    # Responsables
    director = models.CharField('Director/Coordinador', max_length=200, blank=True)
    responsable_sede = models.CharField('Responsable de la sede', max_length=200, blank=True)

    # Estado
    activa = models.BooleanField('Sede activa', default=True)

    # Auditoría
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)

    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['entidad', 'tipo', 'nombre']
        unique_together = ['entidad', 'codigo_reps_sede']

    def __str__(self):
        return f"{self.nombre} - {self.entidad.razon_social}"

    @property
    def ubicacion_completa(self):
        """Retorna la ubicación completa de la sede"""
        return f"{self.direccion}, {self.municipio.nombre}, {self.departamento.nombre}"


class ServicioHabilitado(models.Model):
    """
    Servicios habilitados por cada sede.
    Relación con los servicios definidos en la Resolución 3100.
    """

    COMPLEJIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]

    MODALIDADES = [
        ('INTRAMURAL', 'Intramural'),
        ('EXTRAMURAL', 'Extramural'),
        ('TELEMEDICINA_REMISOR', 'Telemedicina - Prestador Remisor'),
        ('TELEMEDICINA_REFERENCIA', 'Telemedicina - Prestador de Referencia'),
    ]

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='servicios_habilitados',
        verbose_name='Sede'
    )
    servicio = models.ForeignKey(
        'estandares.Servicio',
        on_delete=models.PROTECT,
        related_name='sedes_habilitadas',
        verbose_name='Servicio'
    )
    complejidad = models.CharField('Complejidad', max_length=10, choices=COMPLEJIDADES)
    modalidad = models.CharField('Modalidad', max_length=30, choices=MODALIDADES, default='INTRAMURAL')
    fecha_habilitacion = models.DateField('Fecha de habilitación', null=True, blank=True)
    activo = models.BooleanField('Activo', default=True)
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Servicio Habilitado'
        verbose_name_plural = 'Servicios Habilitados'
        ordering = ['sede', 'servicio']
        unique_together = ['sede', 'servicio', 'modalidad']

    def __str__(self):
        return f"{self.servicio.nombre} - {self.sede.nombre}"


class DocumentoEntidad(models.Model):
    """
    Documentos legales y administrativos de la entidad.
    Control de vigencia de documentación.
    """

    TIPOS_DOCUMENTO = [
        ('CAMARA_COMERCIO', 'Cámara de Comercio'),
        ('RUT', 'RUT'),
        ('CEDULA_RL', 'Cédula Representante Legal'),
        ('RESOLUCION_HAB', 'Resolución de Habilitación'),
        ('LICENCIA_SANITARIA', 'Licencia Sanitaria'),
        ('POLIZA_RC', 'Póliza de Responsabilidad Civil'),
        ('CERTIFICADO_PARAFISCALES', 'Certificado de Parafiscales'),
        ('OTRO', 'Otro'),
    ]

    entidad = models.ForeignKey(
        EntidadPrestadora,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Entidad'
    )
    tipo = models.CharField('Tipo de documento', max_length=30, choices=TIPOS_DOCUMENTO)
    nombre = models.CharField('Nombre del documento', max_length=200)
    archivo = models.FileField('Archivo', upload_to='entidades/documentos/')
    fecha_expedicion = models.DateField('Fecha de expedición')
    fecha_vencimiento = models.DateField('Fecha de vencimiento', null=True, blank=True)
    observaciones = models.TextField('Observaciones', blank=True)

    # Auditoría
    fecha_subida = models.DateTimeField('Fecha de subida', auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos_subidos'
    )

    class Meta:
        verbose_name = 'Documento de Entidad'
        verbose_name_plural = 'Documentos de Entidad'
        ordering = ['entidad', 'tipo', '-fecha_expedicion']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.entidad.razon_social}"

    @property
    def esta_vencido(self):
        """Indica si el documento está vencido"""
        if not self.fecha_vencimiento:
            return False
        return self.fecha_vencimiento < timezone.now().date()

    @property
    def dias_para_vencimiento(self):
        """Días restantes para el vencimiento"""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - timezone.now().date()
        return delta.days


class VigenciaHabilitacion(models.Model):
    """
    Control de vigencias de habilitación por entidad.
    Mantiene historial de períodos de habilitación.
    """

    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('VENCIDA', 'Vencida'),
        ('SUSPENDIDA', 'Suspendida'),
        ('CANCELADA', 'Cancelada'),
    ]

    entidad = models.ForeignKey(
        EntidadPrestadora,
        on_delete=models.CASCADE,
        related_name='vigencias',
        verbose_name='Entidad'
    )
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin')
    numero_resolucion = models.CharField('Número de resolución', max_length=50, blank=True)
    fecha_resolucion = models.DateField('Fecha de resolución', null=True, blank=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='ACTIVA')
    observaciones = models.TextField('Observaciones', blank=True)

    # Porcentaje de cumplimiento al momento del registro
    porcentaje_cumplimiento = models.DecimalField(
        'Porcentaje de cumplimiento',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)

    class Meta:
        verbose_name = 'Vigencia de Habilitación'
        verbose_name_plural = 'Vigencias de Habilitación'
        ordering = ['entidad', '-fecha_inicio']

    def __str__(self):
        return f"Vigencia {self.fecha_inicio} - {self.fecha_fin} ({self.entidad.razon_social})"

    @property
    def es_vigente(self):
        """Indica si la vigencia está actualmente activa"""
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin and self.estado == 'ACTIVA'


class ConfiguracionEvaluacionSede(models.Model):
    """
    Configuración de grupos de criterios habilitados para evaluación por SEDE.
    El grupo 11.1 es obligatorio y siempre está activo.
    Los grupos 11.2 a 11.6 son opcionales y se habilitan aquí según los servicios de la sede.
    """
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='configuraciones_evaluacion',
        verbose_name='Sede'
    )
    grupo_estandar = models.ForeignKey(
        'estandares.GrupoEstandar',
        on_delete=models.CASCADE,
        related_name='configuraciones_sede',
        verbose_name='Grupo de Estándares'
    )
    activo = models.BooleanField('Activo', default=True)
    fecha_activacion = models.DateTimeField('Fecha de activación', auto_now_add=True)
    activado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grupos_activados'
    )
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Configuración de Evaluación por Sede'
        verbose_name_plural = 'Configuraciones de Evaluación por Sede'
        unique_together = ['sede', 'grupo_estandar']
        ordering = ['sede', 'grupo_estandar__orden']

    def __str__(self):
        estado = 'Activo' if self.activo else 'Inactivo'
        return f"{self.sede.nombre} - {self.grupo_estandar.nombre} ({estado})"

    @classmethod
    def crear_configuracion_obligatoria(cls, sede, usuario=None):
        """Crea la configuración obligatoria (11.1) para una sede nueva"""
        from estandares.models import GrupoEstandar
        grupo_obligatorio = GrupoEstandar.objects.filter(codigo='11.1').first()
        if grupo_obligatorio:
            cls.objects.get_or_create(
                sede=sede,
                grupo_estandar=grupo_obligatorio,
                defaults={'activo': True, 'activado_por': usuario}
            )


class ConfiguracionEstandarSede(models.Model):
    """
    Configuración de estándares (sub-estándares) habilitados para evaluación por SEDE.
    Permite un control más granular que ConfiguracionEvaluacionSede.
    Ejemplo: Dentro del grupo 11.2, se pueden activar solo algunos estándares específicos.
    """
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='configuraciones_estandar',
        verbose_name='Sede'
    )
    estandar = models.ForeignKey(
        'estandares.Estandar',
        on_delete=models.CASCADE,
        related_name='configuraciones_sede',
        verbose_name='Estándar'
    )
    activo = models.BooleanField('Activo', default=True)
    fecha_activacion = models.DateTimeField('Fecha de activación', auto_now_add=True)
    activado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estandares_activados'
    )
    observaciones = models.TextField('Observaciones', blank=True)

    class Meta:
        verbose_name = 'Configuración de Estándar por Sede'
        verbose_name_plural = 'Configuraciones de Estándar por Sede'
        unique_together = ['sede', 'estandar']
        ordering = ['sede', 'estandar__grupo__orden', 'estandar__orden']

    def __str__(self):
        estado = 'Activo' if self.activo else 'Inactivo'
        return f"{self.sede.nombre} - {self.estandar.codigo} ({estado})"

    @classmethod
    def crear_configuracion_grupo(cls, sede, grupo, usuario=None, activo=True):
        """Crea configuración para todos los estándares de un grupo"""
        from estandares.models import Estandar
        estandares = Estandar.objects.filter(grupo=grupo, activo=True)
        for estandar in estandares:
            cls.objects.get_or_create(
                sede=sede,
                estandar=estandar,
                defaults={'activo': activo, 'activado_por': usuario}
            )
