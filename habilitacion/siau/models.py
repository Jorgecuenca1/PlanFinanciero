"""
Modelos para SIAU - Sistema de Información y Atención al Usuario
Este módulo está reservado para desarrollo futuro.
"""

from django.db import models
from django.conf import settings


class ConfiguracionSIAU(models.Model):
    """
    Configuración del SIAU por entidad.
    Placeholder para desarrollo futuro.
    """
    entidad = models.OneToOneField(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        related_name='config_siau',
        verbose_name='Entidad'
    )
    telefono_atencion = models.CharField('Teléfono de atención', max_length=50, blank=True)
    email_atencion = models.EmailField('Email de atención', blank=True)
    horario_atencion = models.CharField('Horario de atención', max_length=200, blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='siau_responsable'
    )
    activo = models.BooleanField('SIAU activo', default=True)

    class Meta:
        verbose_name = 'Configuración SIAU'
        verbose_name_plural = 'Configuraciones SIAU'

    def __str__(self):
        return f"SIAU - {self.entidad.razon_social}"


class PQRS(models.Model):
    """
    Peticiones, Quejas, Reclamos y Sugerencias.
    Placeholder para desarrollo futuro.
    """

    TIPOS = [
        ('PETICION', 'Petición'),
        ('QUEJA', 'Queja'),
        ('RECLAMO', 'Reclamo'),
        ('SUGERENCIA', 'Sugerencia'),
        ('FELICITACION', 'Felicitación'),
    ]

    ESTADOS = [
        ('RECIBIDA', 'Recibida'),
        ('EN_PROCESO', 'En Proceso'),
        ('RESPONDIDA', 'Respondida'),
        ('CERRADA', 'Cerrada'),
    ]

    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        related_name='pqrs',
        verbose_name='Entidad'
    )
    sede = models.ForeignKey(
        'entidades.Sede',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pqrs'
    )

    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS)
    radicado = models.CharField('Número de radicado', max_length=50, unique=True)

    # Datos del solicitante
    nombre_solicitante = models.CharField('Nombre del solicitante', max_length=200)
    documento_solicitante = models.CharField('Documento', max_length=20, blank=True)
    telefono_solicitante = models.CharField('Teléfono', max_length=50, blank=True)
    email_solicitante = models.EmailField('Email', blank=True)

    # Contenido
    asunto = models.CharField('Asunto', max_length=300)
    descripcion = models.TextField('Descripción')
    archivo_adjunto = models.FileField(
        'Archivo adjunto',
        upload_to='siau/pqrs/',
        blank=True,
        null=True
    )

    # Estado y gestión
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='RECIBIDA')
    fecha_radicacion = models.DateTimeField('Fecha de radicación', auto_now_add=True)
    fecha_vencimiento = models.DateField('Fecha de vencimiento respuesta')
    fecha_respuesta = models.DateTimeField('Fecha de respuesta', null=True, blank=True)
    respuesta = models.TextField('Respuesta', blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pqrs_asignadas'
    )

    class Meta:
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        ordering = ['-fecha_radicacion']

    def __str__(self):
        return f"{self.radicado} - {self.get_tipo_display()}"


class EncuestaSatisfaccion(models.Model):
    """
    Encuestas de satisfacción al usuario.
    Placeholder para desarrollo futuro.
    """
    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        related_name='encuestas',
        verbose_name='Entidad'
    )
    sede = models.ForeignKey(
        'entidades.Sede',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='encuestas'
    )
    servicio = models.ForeignKey(
        'estandares.Servicio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    calificacion_general = models.PositiveIntegerField(
        'Calificación general',
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comentarios = models.TextField('Comentarios', blank=True)

    class Meta:
        verbose_name = 'Encuesta de Satisfacción'
        verbose_name_plural = 'Encuestas de Satisfacción'
        ordering = ['-fecha']

    def __str__(self):
        return f"Encuesta {self.fecha.date()} - {self.entidad.razon_social}"
