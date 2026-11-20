"""
Django settings for config project.
Production-ready configuration for Hugging Face Spaces + Neon PostgreSQL.
"""

from pathlib import Path
import os

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

try:
    import whitenoise  # noqa: F401
    HAS_WHITENOISE = True
except ImportError:
    HAS_WHITENOISE = False

BASE_DIR = Path(__file__).resolve().parent.parent

# Security & Environment
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-s19e47bcw2kcs&jwh1xq@a8f5-y89k%2#@mcx!!tqh17l$75#6'
)
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1')

# Allowed Hosts (Accepts all in container environments like HF Spaces)
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    *(['whitenoise.runserver_nostatic'] if HAS_WHITENOISE else []),
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
    'accounts',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    *(['whitenoise.middleware.WhiteNoiseMiddleware'] if HAS_WHITENOISE else []),
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# CORS Configuration (Production Frontend + Local Dev)
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1')

env_cors = [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
CORS_ALLOWED_ORIGINS = env_cors or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF Configuration (Trust Hugging Face Spaces + Frontend)
env_csrf = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
CSRF_TRUSTED_ORIGINS = env_csrf or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://localhost:7860",
    "https://*.hf.space",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration (Neon PostgreSQL via DATABASE_URL or Fallback)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and dj_database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
    }
elif os.getenv('DB_ENGINE', 'sqlite').lower() == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'biuuser'),
            'USER': os.getenv('POSTGRES_USER', 'biuuser'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'roth123'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files & WhiteNoise Configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media storage
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Google OAuth2 Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

# Session & Redis Cache Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
USE_REDIS = os.getenv('USE_REDIS', 'false').lower() in ('true', '1')

if USE_REDIS:
    try:
        import django_redis  # noqa: F401
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
    except ImportError:
        SESSION_ENGINE = 'django.contrib.sessions.backends.db'
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Email SMTP Configuration (Gmail Production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('MAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('MAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('MAIL_USERNAME', '')
EMAIL_HOST_PASSWORD = os.getenv('MAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('MAIL_FROM', 'noreply@beltei.edu.kh')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
