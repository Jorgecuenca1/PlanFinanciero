"""
Modelos de usuarios del Sistema de Habilitación
Gestión de usuarios, roles y permisos por entidad
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('rol', 'SUPER')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado para el sistema de habilitación.
    Cada usuario pertenece a una entidad prestadora y tiene un rol específico.
    """

    ROLES = [
        ('SUPER', 'Super Administrador'),
        ('ADMIN', 'Administrador de Entidad'),
        ('AUDITOR', 'Auditor (Solo lectura)'),
        ('CALIDAD', 'Responsable de Calidad'),
        ('EVALUADOR', 'Evaluador'),
        ('APROBADOR', 'Aprobador'),
        ('CONSULTOR', 'Consultor (Solo lectura)'),
    ]

    username = None  # Deshabilitamos username, usamos email
    email = models.EmailField('Correo electrónico', unique=True)

    # Información personal
    primer_nombre = models.CharField('Primer nombre', max_length=50)
    segundo_nombre = models.CharField('Segundo nombre', max_length=50, blank=True)
    primer_apellido = models.CharField('Primer apellido', max_length=50)
    segundo_apellido = models.CharField('Segundo apellido', max_length=50, blank=True)
    documento_identidad = models.CharField('Documento de identidad', max_length=20, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    cargo = models.CharField('Cargo', max_length=100, blank=True)

    # Rol y entidad
    rol = models.CharField('Rol', max_length=20, choices=ROLES, default='CONSULTOR')
    entidad = models.ForeignKey(
        'entidades.EntidadPrestadora',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Entidad Prestadora'
    )

    # Sedes asignadas (un usuario puede tener acceso a varias sedes de su entidad)
    sedes = models.ManyToManyField(
        'entidades.Sede',
        blank=True,
        related_name='usuarios',
        verbose_name='Sedes asignadas'
    )

    # Foto de perfil
    foto = models.ImageField('Foto de perfil', upload_to='usuarios/fotos/', blank=True, null=True)

    # Auditoría
    fecha_ultimo_acceso = models.DateTimeField('Último acceso', null=True, blank=True)
    creado_por = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_creados'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['primer_nombre', 'primer_apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['primer_apellido', 'primer_nombre']

    def __str__(self):
        return f"{self.nombre_completo} ({self.email})"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        nombres = f"{self.primer_nombre} {self.segundo_nombre}".strip()
        apellidos = f"{self.primer_apellido} {self.segundo_apellido}".strip()
        return f"{nombres} {apellidos}".strip()

    @property
    def es_administrador(self):
        """Verifica si el usuario es administrador"""
        return self.rol in ['SUPER', 'ADMIN']

    @property
    def puede_aprobar(self):
        """Verifica si el usuario puede aprobar documentos"""
        return self.rol in ['SUPER', 'ADMIN', 'APROBADOR']

    @property
    def puede_editar(self):
        """Verifica si el usuario puede editar evaluaciones"""
        return self.rol in ['SUPER', 'ADMIN', 'CALIDAD', 'EVALUADOR']

    @property
    def es_auditor(self):
        """Verifica si el usuario es auditor (solo lectura)"""
        return self.rol == 'AUDITOR'

    @property
    def solo_lectura(self):
        """Verifica si el usuario tiene acceso de solo lectura"""
        return self.rol in ['AUDITOR', 'CONSULTOR']

    def registrar_acceso(self):
        """Registra el último acceso del usuario"""
        self.fecha_ultimo_acceso = timezone.now()
        self.save(update_fields=['fecha_ultimo_acceso'])

    def tiene_acceso_sede(self, sede):
        """Verifica si el usuario tiene acceso a una sede específica"""
        if self.rol == 'SUPER':
            return True
        if self.rol == 'ADMIN' and self.entidad == sede.entidad:
            return True
        return self.sedes.filter(pk=sede.pk).exists()


class RegistroActividad(models.Model):
    """
    Registro de actividades de los usuarios en el sistema.
    Para auditoría y trazabilidad.
    """

    TIPOS_ACTIVIDAD = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('ELIMINAR', 'Eliminación'),
        ('APROBAR', 'Aprobación'),
        ('RECHAZAR', 'Rechazo'),
        ('EXPORTAR', 'Exportación'),
        ('IMPORTAR', 'Importación'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actividades'
    )
    tipo = models.CharField('Tipo de actividad', max_length=20, choices=TIPOS_ACTIVIDAD)
    descripcion = models.TextField('Descripción')
    modelo_afectado = models.CharField('Modelo afectado', max_length=100, blank=True)
    objeto_id = models.PositiveIntegerField('ID del objeto', null=True, blank=True)
    datos_anteriores = models.JSONField('Datos anteriores', null=True, blank=True)
    datos_nuevos = models.JSONField('Datos nuevos', null=True, blank=True)
    ip_address = models.GenericIPAddressField('Dirección IP', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    fecha = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de actividad'
        verbose_name_plural = 'Registros de actividad'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} - {self.tipo} - {self.fecha}"
