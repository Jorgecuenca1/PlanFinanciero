"""
Django settings para Sistema de Gestion del Plan Financiero
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-gl^9_db@_-_532hiw0#4oag8u!&sg1+v-op$qlpme_96+z9(sp')

DEBUG = os.environ.get('DEBUG', '1') == '1'

ALLOWED_HOSTS = [
    'pf.corpofuturo.org',
    'www.pf.corpofuturo.org',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# CSRF para HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://pf.corpofuturo.org',
    'https://www.pf.corpofuturo.org',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8020',
    'http://127.0.0.1:8020',
]

# CORS
CORS_ALLOWED_ORIGINS = [
    'https://pf.corpofuturo.org',
    'https://www.pf.corpofuturo.org',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:8020',
    'http://127.0.0.1:8020',
]

CORS_ALLOW_CREDENTIALS = True

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Third party
    "corsheaders",
    # Apps locales
    "accounts",
    "core",
    "planfinanciero",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Static files
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Login/Logout redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'planfinanciero:dashboard'
LOGOUT_REDIRECT_URL = 'core:landing'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Formato de numeros para Colombia
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
USE_THOUSAND_SEPARATOR = True

# Seguridad en produccion
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
