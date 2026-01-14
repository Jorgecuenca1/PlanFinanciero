"""
Django settings for habilitacion_project project.

Sistema de Gestión de Habilitación de Servicios de Salud
Basado en la Resolución 3100 de 2019 - MinSalud Colombia
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-^*52rhm06dn2=0dzk#ytjhx(ql7we2n4rsm&jm2zhio8)kcnkp')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*', 'habilitacion.corpofuturo.org']


# Application definition
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://habilitacion.corpofuturo.org",
    'habilitacion.corpofuturo.org',
]

CSRF_TRUSTED_ORIGINS = [
    "https://finan_poai.corpofuturo.org",
 "https://habilitacion.corpofuturo.org",

]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third party apps
    "crispy_forms",
    "crispy_bootstrap5",

    # Local apps
    "core.apps.CoreConfig",
    "entidades.apps.EntidadesConfig",
    "usuarios.apps.UsuariosConfig",
    "estandares.apps.EstandaresConfig",
    "evaluacion.apps.EvaluacionConfig",
    "documentos.apps.DocumentosConfig",
    "reportes.apps.ReportesConfig",
    "pamec.apps.PamecConfig",
    "siau.apps.SiauConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "habilitacion_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.global_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "habilitacion_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "es-co"

TIME_ZONE = "America/Bogota"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = 'usuarios.Usuario'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login settings
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Configuración del sistema de habilitación
HABILITACION_CONFIG = {
    'VIGENCIA_DIAS': 1460,  # 4 años según Resolución 3100
    'DIAS_ALERTA_VENCIMIENTO': 90,  # Alertar 90 días antes del vencimiento
    'TIPOS_PRESTADOR': [
        ('IPS', 'Institución Prestadora de Servicios de Salud'),
        ('PI', 'Profesional Independiente'),
        ('PSA', 'Prestación de Servicios Asistenciales'),
        ('OSD', 'Objeto Social Diferente'),
    ],
    'ESTADOS_EVALUACION': [
        ('C', 'Cumple'),
        ('NC', 'No Cumple'),
        ('NA', 'No Aplica'),
    ],
    'ESTADOS_DOCUMENTO': [
        ('NT', 'No Trabajado'),
        ('ED', 'En Desarrollo'),
        ('AP', 'Aprobado'),
    ],
}
