
""" Django settings for Ordering System project. """

from pathlib import Path
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
DJANGO_FEATURES__MANUAL_SEAL = env_bool("DJANGO_FEATURES__MANUAL_SEAL", default=False)
DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING = env_bool("DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING", default=False)
DJANGO_FEATURES__SUMMARIZE_CONTENT = env_bool("DJANGO_FEATURES__SUMMARIZE_CONTENT", default=False)
DJANGO_FEATURES__ORDER_WEIGHT = env_bool("DJANGO_FEATURES__ORDER_WEIGHT", default=False)

# Dynamic content properties (used when DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING is on)
DJANGO_DYNAMIC_CONTENT__SEARCH_MIN_LENGTH = env_int(
    "DJANGO_DYNAMIC_CONTENT__SEARCH_MIN_LENGTH", default=2
)
DJANGO_DYNAMIC_CONTENT__SEARCH_DEBOUNCE_MS = env_int(
    "DJANGO_DYNAMIC_CONTENT__SEARCH_DEBOUNCE_MS", default=700
)
DJANGO_DYNAMIC_CONTENT__ORDERS_SYNC_INTERVAL_MS = env_int(
    "DJANGO_DYNAMIC_CONTENT__ORDERS_SYNC_INTERVAL_MS", default=4000
)
DJANGO_DYNAMIC_CONTENT__LOCAL_MUTATION_SKIP_MS = env_int(
    "DJANGO_DYNAMIC_CONTENT__LOCAL_MUTATION_SKIP_MS", default=60000
)
DJANGO_DYNAMIC_CONTENT__RANGE_FILTER_DEBOUNCE_MS = env_int(
    "DJANGO_DYNAMIC_CONTENT__RANGE_FILTER_DEBOUNCE_MS", default=300
)
DJANGO_DYNAMIC_CONTENT__SYNC_HIGHLIGHT_MS = env_int(
    "DJANGO_DYNAMIC_CONTENT__SYNC_HIGHLIGHT_MS", default=120000
)

# Directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

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
    'common.apps.CommonConfig',
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
    'common.middleware.AjaxLoginRedirectMiddleware.AjaxLoginRedirectMiddleware',
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
                'accounts.helpers.context_processors.accounts_roles',
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

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env_str("DJANGO_EMAIL_HOST", required=not DEBUG)
EMAIL_PORT = env_int("DJANGO_EMAIL_PORT", default=587)
EMAIL_HOST_USER = env_str("DJANGO_EMAIL_HOST_USER", required=not DEBUG)
EMAIL_HOST_PASSWORD = env_str("DJANGO_EMAIL_HOST_PASSWORD", required=not DEBUG)
EMAIL_USE_SSL = env_bool("DJANGO_EMAIL_USE_SSL", default=False)
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_USE_TLS", default=not EMAIL_USE_SSL)
EMAIL_FROM_ADDRESS = env_str("DJANGO_EMAIL_FROM_ADDRESS", default="webmaster@localhost", required=not DEBUG)
PASSWORD_RESET_TIMEOUT = 60 * 60

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Sofia'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGOUT_REDIRECT_URL = 'accounts/login/'