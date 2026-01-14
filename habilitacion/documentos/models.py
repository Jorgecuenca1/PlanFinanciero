"""
Modelos para Gestión de Documentos con IA
Integración con OpenAI/ChatGPT para generación y ajuste de documentos
"""

from django.db import models
from django.conf import settings


class ConfiguracionIA(models.Model):
    """
    Configuración de la integración con IA por entidad.
    Permite personalizar el comportamiento de la IA.
    """
    entidad = models.OneToOneField(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        related_name='config_ia',
        verbose_name='Entidad'
    )
    api_key_personalizada = models.CharField(
        'API Key personalizada',
        max_length=200,
        blank=True,
        help_text='API Key propia de la entidad (opcional, si no usa la global)'
    )
    modelo_preferido = models.CharField(
        'Modelo preferido',
        max_length=50,
        default='gpt-4o',
        help_text='Modelo de OpenAI a utilizar'
    )
    max_tokens = models.PositiveIntegerField(
        'Máximo de tokens',
        default=4000
    )
    temperatura = models.DecimalField(
        'Temperatura',
        max_digits=2,
        decimal_places=1,
        default=0.7,
        help_text='Controla la creatividad (0.0 = conservador, 1.0 = creativo)'
    )
    prompt_sistema = models.TextField(
        'Prompt del sistema',
        blank=True,
        default='Eres un experto en habilitación de servicios de salud en Colombia, '
                'especializado en la Resolución 3100 de 2019. Ayudas a las instituciones '
                'a generar documentos que cumplan con los estándares de habilitación.'
    )
    activo = models.BooleanField('IA activa', default=True)

    class Meta:
        verbose_name = 'Configuración de IA'
        verbose_name_plural = 'Configuraciones de IA'

    def __str__(self):
        return f"Configuración IA - {self.entidad.razon_social}"


class PromptTemplate(models.Model):
    """
    Plantillas de prompts para diferentes tipos de documentos.
    Facilita la generación consistente de documentos.
    """

    TIPOS_PROMPT = [
        ('GENERAR', 'Generar documento'),
        ('MEJORAR', 'Mejorar documento existente'),
        ('REVISAR', 'Revisar y corregir'),
        ('ADAPTAR', 'Adaptar normatividad'),
        ('RESUMIR', 'Resumir contenido'),
    ]

    nombre = models.CharField('Nombre', max_length=200)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS_PROMPT)
    descripcion = models.TextField('Descripción', blank=True)
    prompt = models.TextField(
        'Prompt',
        help_text='Usa {variables} para campos dinámicos como {criterio}, {entidad}, {servicio}'
    )

    # Asociación opcional con criterios específicos
    estandar = models.ForeignKey(
        'estandares.Estandar',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prompts'
    )
    criterio = models.ForeignKey(
        'estandares.Criterio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prompts'
    )

    es_global = models.BooleanField(
        'Es global',
        default=True,
        help_text='Si es global, está disponible para todas las entidades'
    )
    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='prompts_personalizados'
    )

    activo = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha de modificación', auto_now=True)

    class Meta:
        verbose_name = 'Plantilla de Prompt'
        verbose_name_plural = 'Plantillas de Prompts'
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"


class SolicitudIA(models.Model):
    """
    Registro de solicitudes a la IA.
    Para auditoría y control de uso.
    """

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PROCESANDO', 'Procesando'),
        ('COMPLETADA', 'Completada'),
        ('ERROR', 'Error'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='solicitudes_ia'
    )
    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.SET_NULL,
        null=True,
        related_name='solicitudes_ia'
    )
    evaluacion = models.ForeignKey(
        'evaluacion.Evaluacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_ia'
    )

    prompt_template = models.ForeignKey(
        PromptTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    prompt_enviado = models.TextField('Prompt enviado')
    respuesta = models.TextField('Respuesta', blank=True)

    modelo_usado = models.CharField('Modelo usado', max_length=50, blank=True)
    tokens_prompt = models.PositiveIntegerField('Tokens del prompt', default=0)
    tokens_respuesta = models.PositiveIntegerField('Tokens de respuesta', default=0)
    tokens_total = models.PositiveIntegerField('Tokens totales', default=0)
    costo_estimado = models.DecimalField(
        'Costo estimado USD',
        max_digits=10,
        decimal_places=6,
        default=0
    )

    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='PENDIENTE')
    mensaje_error = models.TextField('Mensaje de error', blank=True)

    fecha_solicitud = models.DateTimeField('Fecha de solicitud', auto_now_add=True)
    fecha_respuesta = models.DateTimeField('Fecha de respuesta', null=True, blank=True)
    tiempo_procesamiento = models.DecimalField(
        'Tiempo de procesamiento (segundos)',
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Solicitud de IA'
        verbose_name_plural = 'Solicitudes de IA'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud {self.id} - {self.usuario} - {self.estado}"


class NormativaReferencia(models.Model):
    """
    Base de conocimiento de normatividad para que la IA pueda referenciar.
    Permite incluir fragmentos de resoluciones, leyes y normas relevantes.
    """

    TIPOS = [
        ('RESOLUCION', 'Resolución'),
        ('LEY', 'Ley'),
        ('DECRETO', 'Decreto'),
        ('CIRCULAR', 'Circular'),
        ('GUIA', 'Guía'),
        ('OTRO', 'Otro'),
    ]

    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS)
    numero = models.CharField('Número', max_length=50)
    anio = models.PositiveIntegerField('Año')
    titulo = models.CharField('Título', max_length=300)
    entidad_emisora = models.CharField('Entidad emisora', max_length=200)
    fecha_expedicion = models.DateField('Fecha de expedición')
    vigente = models.BooleanField('Vigente', default=True)

    # Contenido
    resumen = models.TextField('Resumen', blank=True)
    contenido_completo = models.TextField(
        'Contenido completo',
        blank=True,
        help_text='Texto completo de la norma para referencia de la IA'
    )
    archivo = models.FileField(
        'Archivo',
        upload_to='normatividad/',
        blank=True,
        null=True
    )
    url_oficial = models.URLField('URL oficial', blank=True)

    # Relación con estándares
    estandares_relacionados = models.ManyToManyField(
        'estandares.Estandar',
        blank=True,
        related_name='normativas'
    )

    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Normativa de Referencia'
        verbose_name_plural = 'Normativas de Referencia'
        ordering = ['-anio', 'numero']
        unique_together = ['tipo', 'numero', 'anio']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero} de {self.anio}"
