"""
Modelos de Estándares y Criterios de Habilitación
Basado en la Resolución 3100 de 2019 - Anexo Técnico
"""

from django.db import models


class GrupoEstandar(models.Model):
    """
    Grupos principales de estándares según la Resolución 3100.
    Ejemplos:
    - 11.1 Estándares aplicables a todos los servicios
    - 11.2 Grupo Consulta Externa
    - 11.3 Grupo Apoyo Diagnóstico y Complementación Terapéutica
    - 11.4 Grupo Internación
    - 11.5 Grupo Quirúrgico
    - 11.6 Grupo Atención Inmediata
    """
    codigo = models.CharField('Código', max_length=10, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    aplica_todos = models.BooleanField(
        'Aplica a todos los servicios',
        default=False,
        help_text='Indica si este grupo aplica a todos los servicios (como el grupo 11.1)'
    )
    orden = models.PositiveIntegerField('Orden de presentación', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Grupo de Estándares'
        verbose_name_plural = 'Grupos de Estándares'
        ordering = ['orden', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Estandar(models.Model):
    """
    Estándares de habilitación dentro de cada grupo.
    Ejemplos para grupo 11.1:
    - 11.1.1 Talento Humano
    - 11.1.2 Infraestructura
    - 11.1.3 Dotación
    - 11.1.4 Medicamentos, Dispositivos Médicos e Insumos
    - 11.1.5 Procesos Prioritarios
    - 11.1.6 Historia Clínica y Registros
    - 11.1.7 Interdependencia
    """
    grupo = models.ForeignKey(
        GrupoEstandar,
        on_delete=models.CASCADE,
        related_name='estandares',
        verbose_name='Grupo'
    )
    codigo = models.CharField('Código', max_length=20)
    codigo_corto = models.CharField(
        'Código corto',
        max_length=20,
        blank=True,
        help_text='Código abreviado para uso interno (ej: TSTH, INF, DOT)'
    )
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    paginas_resolucion = models.CharField(
        'Páginas en resolución',
        max_length=20,
        blank=True,
        help_text='Referencia a páginas en la resolución original'
    )
    orden = models.PositiveIntegerField('Orden de presentación', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Estándar'
        verbose_name_plural = 'Estándares'
        ordering = ['grupo', 'orden', 'codigo']
        unique_together = ['grupo', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def total_criterios(self):
        """Retorna el total de criterios en este estándar"""
        return self.criterios.filter(activo=True).count()


class Servicio(models.Model):
    """
    Servicios de salud habilitables según la Resolución 3100.
    Cada servicio tiene sus propios estándares específicos.
    Ejemplos:
    - 11.2.1 Servicio de Consulta Externa General
    - 11.3.2 Servicio Farmacéutico
    - 11.4.1 Servicio de Hospitalización
    - 11.6.1 Servicio de Urgencias
    """
    grupo = models.ForeignKey(
        GrupoEstandar,
        on_delete=models.CASCADE,
        related_name='servicios',
        verbose_name='Grupo'
    )
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombre = models.CharField('Nombre del servicio', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)

    # Referencia a la hoja del Excel original
    codigo_hoja_excel = models.CharField(
        'Código hoja Excel',
        max_length=50,
        blank=True,
        help_text='Referencia a la hoja en el archivo Excel de autoevaluación'
    )

    # Indica si es obligatorio para todas las entidades (grupo 11.1)
    es_obligatorio = models.BooleanField(
        'Es obligatorio',
        default=False,
        help_text='Los servicios del grupo 11.1 son obligatorios para todas las entidades'
    )

    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['grupo', 'orden', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class EstandarServicio(models.Model):
    """
    Estándares específicos por servicio.
    Cada servicio tiene sus propios estándares de:
    - Talento Humano (TH)
    - Infraestructura (INF)
    - Dotación (DOT)
    - etc.
    """

    TIPOS_ESTANDAR = [
        ('TH', 'Talento Humano'),
        ('INF', 'Infraestructura'),
        ('DOT', 'Dotación'),
        ('MD', 'Medicamentos y Dispositivos'),
        ('PP', 'Procesos Prioritarios'),
        ('HCR', 'Historia Clínica y Registros'),
        ('INT', 'Interdependencia'),
    ]

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='estandares_especificos',
        verbose_name='Servicio'
    )
    tipo = models.CharField('Tipo de estándar', max_length=10, choices=TIPOS_ESTANDAR)
    codigo = models.CharField(
        'Código',
        max_length=30,
        help_text='Código específico del estándar para este servicio (ej: URG_TH)'
    )
    descripcion = models.TextField('Descripción', blank=True)
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Estándar de Servicio'
        verbose_name_plural = 'Estándares de Servicios'
        ordering = ['servicio', 'orden']
        unique_together = ['servicio', 'tipo']

    def __str__(self):
        return f"{self.codigo} - {self.get_tipo_display()} - {self.servicio.nombre}"


class Criterio(models.Model):
    """
    Criterios específicos de evaluación.
    Cada estándar tiene múltiples criterios que deben cumplirse.
    """

    TIPOS_CRITERIO = [
        ('CRITERIO', 'Criterio Evaluable'),
        ('TITULO', 'Título de Sección'),
        ('SUBTITULO', 'Subtítulo'),
        ('NOTA', 'Nota o Aclaración'),
    ]

    # Puede pertenecer a un estándar general o a un estándar de servicio
    estandar = models.ForeignKey(
        Estandar,
        on_delete=models.CASCADE,
        related_name='criterios',
        verbose_name='Estándar general',
        null=True,
        blank=True
    )
    estandar_servicio = models.ForeignKey(
        EstandarServicio,
        on_delete=models.CASCADE,
        related_name='criterios',
        verbose_name='Estándar de servicio',
        null=True,
        blank=True
    )

    numero = models.CharField('Número', max_length=20, help_text='Numeración del criterio (ej: 1, 1.1, 1.1.1)')
    texto = models.TextField('Texto del criterio')

    tipo_criterio = models.CharField(
        'Tipo',
        max_length=20,
        choices=TIPOS_CRITERIO,
        default='CRITERIO',
        help_text='Indica si es un criterio evaluable, título o subtítulo'
    )
    es_titulo = models.BooleanField(
        'Es título/sección',
        default=False,
        help_text='Indica si es un título de sección y no requiere evaluación'
    )

    # Información adicional
    complejidad_aplica = models.CharField(
        'Complejidad aplicable',
        max_length=100,
        blank=True,
        help_text='Indica a qué complejidades aplica (baja, media, alta)'
    )
    modalidad_aplica = models.CharField(
        'Modalidad aplicable',
        max_length=200,
        blank=True,
        help_text='Indica a qué modalidades aplica'
    )
    observaciones = models.TextField('Observaciones', blank=True)

    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Criterio'
        verbose_name_plural = 'Criterios'
        ordering = ['orden', 'numero']

    def __str__(self):
        texto_corto = self.texto[:100] + '...' if len(self.texto) > 100 else self.texto
        return f"{self.numero}. {texto_corto}"

    @property
    def estandar_padre(self):
        """Retorna el estándar al que pertenece (general o de servicio)"""
        return self.estandar or self.estandar_servicio

    @property
    def es_evaluable(self):
        """Indica si el criterio requiere evaluación (C/NC/NA)"""
        return self.tipo_criterio == 'CRITERIO' and not self.es_titulo


class PlantillaDocumento(models.Model):
    """
    Plantillas de documentos de ejemplo para cada criterio.
    Pueden ser editadas y personalizadas por cada entidad.
    """
    criterio = models.ForeignKey(
        Criterio,
        on_delete=models.CASCADE,
        related_name='plantillas',
        verbose_name='Criterio'
    )
    nombre = models.CharField('Nombre de la plantilla', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    contenido_html = models.TextField(
        'Contenido HTML',
        blank=True,
        help_text='Contenido de la plantilla en formato HTML'
    )
    archivo_plantilla = models.FileField(
        'Archivo plantilla',
        upload_to='plantillas/',
        blank=True,
        null=True,
        help_text='Archivo Word/PDF de plantilla'
    )
    es_ejemplo = models.BooleanField(
        'Es ejemplo',
        default=True,
        help_text='Indica si es una plantilla de ejemplo del sistema'
    )

    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)

    class Meta:
        verbose_name = 'Plantilla de Documento'
        verbose_name_plural = 'Plantillas de Documentos'
        ordering = ['criterio', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.criterio}"
