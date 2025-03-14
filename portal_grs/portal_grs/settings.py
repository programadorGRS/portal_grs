"""
Django settings for portal_grs project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%pyujf0qts@ihh=p9gpm$&r&-3&caa#l_#35aa=a1yp1k(#*=7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'dashboard', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dashboard.middleware.SessionControlMiddleware',  # Middleware personalizado
]

ROOT_URLCONF = 'portal_grs.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Deixe vazio, o Django irá procurar automaticamente nos diretórios de templates dos apps
        'APP_DIRS': True,  # Isso permite que o Django procure em app_name/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portal_grs.wsgi.application'
    

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
 
# Configuração para SQLite3 (ambiente de teste)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'portal_grs_db',
        'USER': 'portal_grs_db_user',
        'PASSWORD': 'BivlVcaMNRMbRVpbGudnZ9Q5ghkwFaQa',
        'HOST': 'dpg-cv9sfgtumphs73aaul6g-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

# Configuração de segurança para senhas
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Configurações de segurança para validação de senhas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'  # Alterado para português do Brasil

TIME_ZONE = 'America/Sao_Paulo'  # Alterado para o fuso horário do Brasil

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração do modelo de usuário personalizado
AUTH_USER_MODEL = 'dashboard.Usuario'

# Configuração de cache simplificada para ambiente de teste
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Para ambiente de teste, usar cache_db é mais seguro (combina cache com banco)
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'

# Timeout de sessão em segundos (30 minutos)
SESSION_COOKIE_AGE = 1800

# Configurações para administração
ADMIN_URL = 'adminGRS/'  # URL personalizada para o admin (mais segura)

# Configuração para usar REST Framework e JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# Configurações para JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Token expira em 30 minutos
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Refresh token expira em 1 dia
    'ROTATE_REFRESH_TOKENS': True,                  # Gera um novo refresh token quando usado
    'BLACKLIST_AFTER_ROTATION': True,               # Blacklist tokens antigos
    
    'ALGORITHM': 'HS256',                           # Algoritmo de assinatura
    'SIGNING_KEY': SECRET_KEY,                      # Chave para assinatura
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),               # Tipo de header de autenticação
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',       # Nome do header de autenticação
    'USER_ID_FIELD': 'id',                          # Campo de ID do usuário no modelo
    'USER_ID_CLAIM': 'user_id',                     # Claim para ID do usuário no token
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Configurações para CSRF
CSRF_COOKIE_SECURE = not DEBUG  # True em produção, False em desenvolvimento
CSRF_COOKIE_HTTPONLY = True     # JavaScript não pode acessar o cookie CSRF
CSRF_USE_SESSIONS = True        # Armazenar CSRF token na sessão
CSRF_COOKIE_SAMESITE = 'Strict' # Prevenir ataques CSRF em outros sites

# Configurações de Sessão
SESSION_COOKIE_SECURE = not DEBUG  # True em produção, False em desenvolvimento
SESSION_COOKIE_HTTPONLY = True     # JavaScript não pode acessar o cookie de sessão
SESSION_COOKIE_SAMESITE = 'Strict' # Prevenir ataques session hijacking
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Sessão expira quando o navegador é fechado

# Configuração de login
LOGIN_URL = 'login'                # URL para login
LOGIN_REDIRECT_URL = 'dashboard'   # Redirecionamento após login
LOGOUT_REDIRECT_URL = 'login'      # Redirecionamento após logout

# Configurações CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# Garantir que as mensagens são armazenadas em cookies se a sessão não estiver disponível
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'
