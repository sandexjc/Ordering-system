
""" Django settings for Ordering System project. """

from pathlib import Path
import os
from .env import env_bool, env_str, env_list, env_int


# Environment configuration
DJANGO_ENVIRONMENT = env_str("DJANGO_ENVIRONMENT", required=True)
DJANGO_SECURITY_ENABLE = env_bool("DJANGO_SECURITY_ENABLE", required=True)

# Security settings
DEBUG = env_bool("DJANGO_DEBUG", required=True)
SECRET_KEY = env_str("DJANGO_SECRET_KEY", required=True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["*"])

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=DJANGO_SECURITY_ENABLE)
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https") if DJANGO_SECURITY_ENABLE else None
)

SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", default=DJANGO_SECURITY_ENABLE)
SESSION_SAVE_EVERY_REQUEST = env_bool("DJANGO_SESSION_SAVE_EVERY_REQUEST", default=DJANGO_SECURITY_ENABLE)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool("DJANGO_SESSION_EXPIRE_AT_BROWSER_CLOSE", default=DJANGO_SECURITY_ENABLE)
SESSION_COOKIE_AGE = env_int("DJANGO_SESSION_COOKIE_AGE", default=43200)

CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", default=DJANGO_SECURITY_ENABLE)
CSRF_COOKIE_AGE = env_int("DJANGO_CSRF_COOKIE_AGE", default=43200)

# Features
DJANGO_FEATURES__AUTO_SEAL_SELECT = env_bool("DJANGO_FEATURES__AUTO_SEAL_SELECT", default=False)

# Directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
DATE_FORMAT = '%d/%m/%Y'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'common',
    'accounts',
    'table',
    'vitrine'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "main" / "templates",
            BASE_DIR / "common" / "templates",
            ],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'main.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Sofia'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGOUT_REDIRECT_URL = 'accounts/login/'