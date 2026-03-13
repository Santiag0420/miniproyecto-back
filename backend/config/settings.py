"""
Configuración principal del proyecto Django.
Las variables sensibles se cargan desde el archivo .env ubicado en miniproyecto-back/.env
"""
from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# BASE_DIR apunta a la carpeta backend/ (donde está manage.py).
# .env se carga desde el nivel superior (miniproyecto-back/).
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / '.env')

# Clave secreta de Django — nunca exponerla en producción.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# En producción establecer DEBUG=False en las variables de entorno de Render.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Render termina SSL en su proxy y reenvía las requests como HTTP.
# Estas dos configuraciones le dicen a Django que confíe en los headers del proxy.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True


# --- Aplicaciones instaladas ---
# Se incluyen las apps de Django, librerías de terceros y nuestras propias apps.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',             # WebSockets con Django Channels
    'rest_framework',       # API REST con Django REST Framework
    'drf_spectacular',      # Generación automática de documentación OpenAPI
    'corsheaders',          # Permite solicitudes cross-origin desde el frontend
    'backend.apps.users.apps.UsersConfig',       # App de usuarios: modelos, vistas y endpoints
    'backend.apps.activities',                   # App de actividades evaluativas y subtareas
]

# --- Middleware ---
# CorsMiddleware debe estar lo más arriba posible para manejar preflight requests.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # sirve archivos estáticos (admin CSS)
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Módulo que contiene el router principal de URLs del proyecto.
ROOT_URLCONF = 'backend.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Punto de entrada para servidores WSGI (producción con Gunicorn, etc.).
WSGI_APPLICATION = 'backend.config.wsgi.application'


# --- Base de datos ---
# Conexión a PostgreSQL en Supabase. SSL obligatorio con el certificado de Supabase.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'verify-full',
            'sslrootcert': BASE_DIR.parent / 'prod-ca-2021.crt',
        },
    }
}


# --- Validación de contraseñas ---
# Django rechaza contraseñas débiles, muy cortas, numéricas o similares al usuario.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Internacionalización ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# Directorio donde collectstatic agrupa todos los archivos estáticos para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- CORS ---
# En desarrollo se permiten todos los orígenes. En producción usar CORS_ALLOWED_ORIGINS.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# --- Django REST Framework ---
# Usa JWT para autenticar todas las requests a la API por defecto.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'backend.apps.activities.exception_handler.custom_exception_handler',
}

# --- Configuración de tokens JWT ---
# Access token: válido 15 minutos. El frontend debe renovarlo automáticamente
# mientras el usuario esté activo (antes de que expire).
#
# Refresh token: válido 30 minutos y se rota en cada uso.
# Esto simula inactividad: si el usuario no usa la app durante 30 minutos,
# el refresh token caduca y debe volver a iniciar sesión.
# Mientras el usuario esté activo, el frontend renueva el token
# cada ~14 min y el contador de 30 min se reinicia.
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=30),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': False,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Mi MINIPROYECTO API',
    'DESCRIPTION': 'Documentación detallada de los endpoints',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# --- Django Channels ---
# Punto de entrada ASGI que maneja HTTP y WebSockets.
ASGI_APPLICATION = 'backend.config.asgi.application'

# Capa de canales en memoria — ideal para desarrollo y un solo proceso.
# En producción con múltiples workers, reemplazar por RedisChannelLayer.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}