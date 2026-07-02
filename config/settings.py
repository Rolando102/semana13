"""
config/settings.py
FASE 1 — Setup & Configuración DRF
Concepto profundo: configuración centralizada de API (separación de concerns).
Nada de permisos/paginación/throttling se hardcodea en las vistas: todo vive
aquí como default global y se sobrescribe solo cuando una vista lo necesite
explícitamente (regla de la guía).
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-secret-key-cambiar-en-produccion"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "rest_framework",
    "django_filters",
    "corsheaders",
    "drf_spectacular",

    # App propia
    "tareas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # debe ir ANTES de CommonMiddleware
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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# DJANGO REST FRAMEWORK — configuración centralizada (Fase 1 + Fase 4)
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # Autenticación: sesión (navegable) + básica para pruebas con curl/Postman
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    # Permisos GLOBALES (prohibido hardcodear permisos en vistas)
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    # Filtrado backend (Fase 4)
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Paginación estándar (Fase 4)
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
    # Throttling (Fase 4) — protección contra scraping/abuso
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/min",
        "user": "60/min",
    },
    # Documentación OpenAPI (Fase 5)
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# ---------------------------------------------------------------------------
# CORS (Fase 5) — nunca "*" en dev sin justificación explícita
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite/SPA típico
]
CORS_ALLOW_CREDENTIALS = True  # necesario si el SPA envía cookies de sesión

# ---------------------------------------------------------------------------
# CSRF (Fase 5) — obligatorio porque usamos SessionAuthentication
# ---------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ---------------------------------------------------------------------------
# drf-spectacular (Fase 5) — contrato OpenAPI 3.0 máquina-legible
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "API de Gestión de Tareas",
    "DESCRIPTION": "API RESTful production-ready — Guía Práctica Semana 12 (DAW/IS093A)",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# IA: ¿cómo estructurar REST_FRAMEWORK para que paginación, throttling y
# permisos sean globales sin tocar cada vista?
# Solución manual: se definieron todos los defaults en settings.py
# (DEFAULT_PAGINATION_CLASS, DEFAULT_THROTTLE_CLASSES, DEFAULT_PERMISSION_CLASSES)
# y las vistas solo importan lo necesario, sin sobrescribir salvo un caso
# puntual (ver @action en views.py), cumpliendo la restricción de la Fase 1.
