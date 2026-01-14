"""
Modelos para PAMEC - Programa de Auditoría para el Mejoramiento de la Calidad en Salud
Este módulo está reservado para desarrollo futuro.
"""

from django.db import models
from django.conf import settings


class ProgramaPAMEC(models.Model):
    """
    Programa de Auditoría para el Mejoramiento de la Calidad.
    Placeholder para desarrollo futuro.
    """
    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.CASCADE,
        related_name='programas_pamec',
        verbose_name='Entidad'
    )
    nombre = models.CharField('Nombre del programa', max_length=200)
    periodo = models.CharField('Período', max_length=50)
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin')
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=[
            ('PLANIFICACION', 'En Planificación'),
            ('EJECUCION', 'En Ejecución'),
            ('SEGUIMIENTO', 'En Seguimiento'),
            ('FINALIZADO', 'Finalizado'),
        ],
        default='PLANIFICACION'
    )
    observaciones = models.TextField('Observaciones', blank=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Programa PAMEC'
        verbose_name_plural = 'Programas PAMEC'
        ordering = ['entidad', '-fecha_inicio']

    def __str__(self):
        return f"PAMEC {self.periodo} - {self.entidad.razon_social}"


class CicloPHVA(models.Model):
    """
    Ciclo PHVA (Planear, Hacer, Verificar, Actuar) del PAMEC.
    Placeholder para desarrollo futuro.
    """
    programa = models.ForeignKey(
        ProgramaPAMEC,
        on_delete=models.CASCADE,
        related_name='ciclos',
        verbose_name='Programa'
    )
    fase = models.CharField(
        'Fase',
        max_length=20,
        choices=[
            ('PLANEAR', 'Planear'),
            ('HACER', 'Hacer'),
            ('VERIFICAR', 'Verificar'),
            ('ACTUAR', 'Actuar'),
        ]
    )
    descripcion = models.TextField('Descripción')
    fecha_inicio = models.DateField('Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateField('Fecha de fin', null=True, blank=True)
    porcentaje_avance = models.DecimalField(
        'Porcentaje de avance',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ciclos_pamec'
    )

    class Meta:
        verbose_name = 'Ciclo PHVA'
        verbose_name_plural = 'Ciclos PHVA'
        ordering = ['programa', 'fase']

    def __str__(self):
        return f"{self.get_fase_display()} - {self.programa}"
