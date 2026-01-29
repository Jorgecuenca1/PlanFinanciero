from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal


class OrganoEjecutor(models.Model):
    """Catálogo de Órganos Ejecutores"""
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Órgano Ejecutor"
        verbose_name_plural = "Órganos Ejecutores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class IngresoAgregado(models.Model):
    """Catálogo de Ingresos Agregados (Fuentes de Financiación)"""
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ingreso Agregado"
        verbose_name_plural = "Ingresos Agregados"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoIngreso(models.Model):
    """Catálogo de Tipos de Ingreso"""
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Ingreso"
        verbose_name_plural = "Tipos de Ingreso"
        ordering = ['codigo']

    def __str__(self):
        return self.nombre


class Rubro(models.Model):
    """
    Maestra de Rubros Presupuestales
    Soporta estructura jerárquica (rubros padre/hijo)
    """
    NIVEL_CHOICES = [
        ('AC', 'Administración Central'),
        ('EP', 'Establecimientos Públicos'),
    ]

    CLASE_INGRESO_CHOICES = [
        ('CORRIENTE', 'Corriente'),
        ('CAPITAL', 'Capital'),
    ]

    # Código y nombre
    codigo = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Código Presupuestal",
        help_text="Código único del rubro (ej: 0301 - 1.1.01.01.100.01 - 14)"
    )
    nombre = models.CharField(
        max_length=500,
        verbose_name="Concepto del Ingreso"
    )

    # Estructura jerárquica
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hijos',
        verbose_name="Rubro Padre"
    )
    es_totalizador = models.BooleanField(
        default=False,
        verbose_name="Es Totalizador",
        help_text="Si es True, es un rubro padre que agrupa otros rubros"
    )

    # Clasificadores (solo para rubros de detalle)
    nivel = models.CharField(
        max_length=10,
        choices=NIVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Nivel"
    )
    organo_ejecutor = models.ForeignKey(
        OrganoEjecutor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rubros",
        verbose_name="Órgano Ejecutor"
    )
    ingreso_agregado = models.ForeignKey(
        IngresoAgregado,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rubros",
        verbose_name="Ingreso Agregado"
    )
    clase_ingreso = models.CharField(
        max_length=20,
        choices=CLASE_INGRESO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Clase de Ingreso"
    )
    tipo_ingreso = models.ForeignKey(
        TipoIngreso,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="rubros",
        verbose_name="Tipo de Ingreso"
    )
    codigo_fuente = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código Fuente"
    )

    # Metadata
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rubros_creados'
    )

    class Meta:
        verbose_name = "Rubro Presupuestal"
        verbose_name_plural = "Rubros Presupuestales"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def tiene_movimientos(self):
        """Verifica si el rubro tiene movimientos asociados"""
        return self.movimientos.exists()

    @property
    def presupuesto_inicial(self):
        """Calcula el presupuesto inicial del rubro"""
        # Usar valor anotado si existe (mas eficiente)
        if hasattr(self, '_presupuesto_inicial'):
            return self._presupuesto_inicial or Decimal('0')
        if self.es_totalizador:
            return sum(h.presupuesto_inicial for h in self.hijos.filter(activo=True))
        total = self.movimientos.filter(
            tipo='INICIAL',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_adiciones(self):
        """Calcula el total de adiciones del rubro"""
        if hasattr(self, '_total_adiciones'):
            return self._total_adiciones or Decimal('0')
        if self.es_totalizador:
            return sum(h.total_adiciones for h in self.hijos.filter(activo=True))
        total = self.movimientos.filter(
            tipo='ADICION',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_reducciones(self):
        """Calcula el total de reducciones del rubro"""
        if hasattr(self, '_total_reducciones'):
            return self._total_reducciones or Decimal('0')
        if self.es_totalizador:
            return sum(h.total_reducciones for h in self.hijos.filter(activo=True))
        total = self.movimientos.filter(
            tipo='REDUCCION',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_traslados_credito(self):
        """Total de traslados a favor (crédito)"""
        if hasattr(self, '_traslados_credito'):
            return self._traslados_credito or Decimal('0')
        if self.es_totalizador:
            return sum(h.total_traslados_credito for h in self.hijos.filter(activo=True))
        total = self.movimientos.filter(
            tipo='TRASLADO_CREDITO',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_traslados_debito(self):
        """Total de traslados en contra (débito)"""
        if hasattr(self, '_traslados_debito'):
            return self._traslados_debito or Decimal('0')
        if self.es_totalizador:
            return sum(h.total_traslados_debito for h in self.hijos.filter(activo=True))
        total = self.movimientos.filter(
            tipo='TRASLADO_DEBITO',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def saldo_actual(self):
        """
        Calcula el saldo actual usando la fórmula:
        Saldo = Presupuesto Inicial + Adiciones - Reducciones + Traslados Crédito - Traslados Débito
        """
        return (
            self.presupuesto_inicial +
            self.total_adiciones -
            self.total_reducciones +
            self.total_traslados_credito -
            self.total_traslados_debito
        )

    def puede_reducir(self, monto):
        """Verifica si se puede reducir el monto indicado sin quedar en negativo"""
        return self.saldo_actual >= monto

    def get_nivel_jerarquico(self):
        """Retorna el nivel jerárquico basado en el código"""
        return self.codigo.count('.')


class Movimiento(models.Model):
    """
    Tabla Transaccional de Movimientos
    Registra todas las operaciones sobre los rubros presupuestales
    """
    TIPO_CHOICES = [
        ('INICIAL', 'Presupuesto Inicial'),
        ('ADICION', 'Adición'),
        ('REDUCCION', 'Reducción'),
        ('TRASLADO_CREDITO', 'Traslado (Crédito)'),
        ('TRASLADO_DEBITO', 'Traslado (Débito)'),
    ]

    rubro = models.ForeignKey(
        Rubro,
        on_delete=models.PROTECT,
        verbose_name="Rubro",
        related_name="movimientos"
    )
    fecha = models.DateField(verbose_name="Fecha de Operación")
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )
    documento_soporte = models.CharField(
        max_length=200,
        verbose_name="Documento Soporte",
        help_text="Número de Ordenanza, Decreto o Acto Administrativo"
    )
    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor (COP)"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    numero_ajuste = models.IntegerField(
        default=0,
        verbose_name="Número de Ajuste",
        help_text="0 para inicial, 1 para ajuste #1, etc."
    )
    movimiento_relacionado = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_relacionados',
        verbose_name="Movimiento Relacionado"
    )

    # Auditoría
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_registrados'
    )

    # Control de anulación
    anulado = models.BooleanField(default=False, verbose_name="Anulado")
    motivo_anulacion = models.TextField(blank=True, verbose_name="Motivo de Anulación")
    fecha_anulacion = models.DateTimeField(null=True, blank=True)
    anulado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_anulados'
    )

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ['-fecha', '-fecha_registro']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.rubro.codigo} - ${self.valor:,.2f}"

    def clean(self):
        """Validaciones de negocio"""
        if self.valor is not None and self.valor <= 0:
            raise ValidationError({'valor': 'El valor debe ser mayor a cero.'})

        if self.tipo in ['REDUCCION', 'TRASLADO_DEBITO'] and not self.anulado:
            if self.pk:
                saldo_sin_actual = self.rubro.saldo_actual
                mov_actual = Movimiento.objects.filter(pk=self.pk).first()
                if mov_actual and mov_actual.tipo in ['REDUCCION', 'TRASLADO_DEBITO']:
                    saldo_sin_actual += mov_actual.valor
            else:
                saldo_sin_actual = self.rubro.saldo_actual

            if self.valor > saldo_sin_actual:
                raise ValidationError({
                    'valor': f'No se puede reducir ${self.valor:,.2f}. '
                            f'El saldo disponible es ${saldo_sin_actual:,.2f}'
                })

    def save(self, *args, **kwargs):
        # Saltar validación de saldo para carga masiva inicial
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)


class Vigencia(models.Model):
    """Año fiscal para organizar los presupuestos"""
    ano = models.IntegerField(unique=True, verbose_name="Año")
    activa = models.BooleanField(default=False, verbose_name="Vigencia Activa")
    fecha_apertura = models.DateField(verbose_name="Fecha de Apertura")
    fecha_cierre = models.DateField(null=True, blank=True, verbose_name="Fecha de Cierre")

    class Meta:
        verbose_name = "Vigencia"
        verbose_name_plural = "Vigencias"
        ordering = ['-ano']

    def __str__(self):
        estado = "Activa" if self.activa else "Cerrada"
        return f"Vigencia {self.ano} ({estado})"

    def save(self, *args, **kwargs):
        if self.activa:
            Vigencia.objects.exclude(pk=self.pk).update(activa=False)
        super().save(*args, **kwargs)


# Mantener compatibilidad con el código existente
class FuenteFinanciacion(IngresoAgregado):
    """Alias para compatibilidad - usar IngresoAgregado"""
    class Meta:
        proxy = True
        verbose_name = "Fuente de Financiación"
        verbose_name_plural = "Fuentes de Financiación"


# ==========================================
# PLAN FINANCIERO DE GASTOS
# ==========================================

class RubroGasto(models.Model):
    """
    Rubros del Plan Financiero de Gastos
    Centralizados: Funcionamiento, Deuda, Inversión
    Descentralizados: Funcionamiento, Deuda, Inversión, Gastos de Operación
    """
    TIPO_ENTIDAD_CHOICES = [
        ('CENTRALIZADO', 'Centralizado'),
        ('DESCENTRALIZADO', 'Descentralizado'),
    ]

    RUBRO_CHOICES = [
        ('FUNCIONAMIENTO', 'Funcionamiento'),
        ('DEUDA', 'Deuda'),
        ('INVERSION', 'Inversión'),
        ('GASTOS_OPERACION', 'Gastos de Operación'),
    ]

    tipo_entidad = models.CharField(
        max_length=20,
        choices=TIPO_ENTIDAD_CHOICES,
        default='CENTRALIZADO',
        verbose_name="Tipo de Entidad"
    )
    codigo = models.CharField(
        max_length=30,
        verbose_name="Código Rubro"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rubro de Gasto"
        verbose_name_plural = "Rubros de Gastos"
        ordering = ['tipo_entidad', 'codigo']
        unique_together = ['tipo_entidad', 'codigo']

    def __str__(self):
        return f"{self.get_tipo_entidad_display()} - {self.nombre}"

    @property
    def presupuesto_inicial(self):
        """Presupuesto inicial del rubro"""
        if hasattr(self, '_presupuesto_inicial'):
            return self._presupuesto_inicial or Decimal('0')
        total = self.movimientos.filter(
            tipo='INICIAL',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_adiciones(self):
        """Total de adiciones"""
        if hasattr(self, '_total_adiciones'):
            return self._total_adiciones or Decimal('0')
        total = self.movimientos.filter(
            tipo='ADICION',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_reducciones(self):
        """Total de reducciones"""
        if hasattr(self, '_total_reducciones'):
            return self._total_reducciones or Decimal('0')
        total = self.movimientos.filter(
            tipo='REDUCCION',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_creditos(self):
        """Total de créditos (suma)"""
        if hasattr(self, '_total_creditos'):
            return self._total_creditos or Decimal('0')
        total = self.movimientos.filter(
            tipo='CREDITO',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def total_contracreditos(self):
        """Total de contracréditos (resta)"""
        if hasattr(self, '_total_contracreditos'):
            return self._total_contracreditos or Decimal('0')
        total = self.movimientos.filter(
            tipo='CONTRACREDITO',
            anulado=False
        ).aggregate(total=Sum('valor'))['total']
        return total or Decimal('0')

    @property
    def saldo_actual(self):
        """
        Saldo = Inicial + Adiciones - Reducciones + Créditos - Contracréditos
        """
        return (
            self.presupuesto_inicial +
            self.total_adiciones -
            self.total_reducciones +
            self.total_creditos -
            self.total_contracreditos
        )


class MovimientoGasto(models.Model):
    """
    Movimientos del Plan Financiero de Gastos
    """
    TIPO_CHOICES = [
        ('INICIAL', 'Presupuesto Inicial'),
        ('ADICION', 'Adición'),
        ('REDUCCION', 'Reducción'),
        ('CREDITO', 'Crédito'),
        ('CONTRACREDITO', 'Contracrédito'),
    ]

    rubro = models.ForeignKey(
        RubroGasto,
        on_delete=models.PROTECT,
        verbose_name="Rubro",
        related_name="movimientos"
    )
    fecha = models.DateField(verbose_name="Fecha de Operación")
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )
    documento_soporte = models.CharField(
        max_length=200,
        verbose_name="Documento Soporte",
        help_text="Número de Ordenanza, Decreto o Acto Administrativo"
    )
    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor (COP)"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    # Auditoría
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_gasto_registrados'
    )

    # Control de anulación
    anulado = models.BooleanField(default=False, verbose_name="Anulado")
    motivo_anulacion = models.TextField(blank=True, verbose_name="Motivo de Anulación")
    fecha_anulacion = models.DateTimeField(null=True, blank=True)
    anulado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_gasto_anulados'
    )

    class Meta:
        verbose_name = "Movimiento de Gasto"
        verbose_name_plural = "Movimientos de Gastos"
        ordering = ['-fecha', '-fecha_registro']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.rubro.nombre} - ${self.valor:,.2f}"

    def clean(self):
        if self.valor is not None and self.valor <= 0:
            raise ValidationError({'valor': 'El valor debe ser mayor a cero.'})
