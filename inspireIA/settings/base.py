"""
Base settings for inspireIA project.
Contains settings common to all environments.
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Note: BASE_DIR is also defined in __init__.py for dotenv loading
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Helper function to get environment variables with defaults
def get_env_value(env_variable: str, default_value: Any = None) -> Any:
    """
    Get an environment variable or return a default value
    """
    return os.environ.get(env_variable, default_value)

# Application definition
INSTALLED_APPS: List[str] = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    
    # Core app
    'core',
    
    # Project apps
    'catalog',
    'users',
    'interaction',
    'api',
    'auth_app',
    'profile_app',
]

MIDDLEWARE: List[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'inspireIA.middleware.RequestLogMiddleware',
]

ROOT_URLCONF: str = 'inspireIA.urls'

TEMPLATES: List[Dict[str, Any]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'inspireIA' / 'templates',
            BASE_DIR / 'core' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'catalog.context_processors.ai_categories',
            ],
        },
    },
]

WSGI_APPLICATION: str = 'inspireIA.wsgi.application'

# Database
# Default to SQLite, but can be overridden in environment-specific settings
DATABASES: Dict[str, Dict[str, Any]] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security settings
# Salt for encryption key derivation - should be set in environment variables
ENCRYPTION_KEY_SALT = get_env_value('ENCRYPTION_KEY_SALT', None)

# Password validation
AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': int(get_env_value('MIN_PASSWORD_LENGTH', 8)),
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
LANGUAGE_CODE: str = get_env_value('LANGUAGE_CODE', 'en-us')
TIME_ZONE: str = get_env_value('TIME_ZONE', 'UTC')
USE_I18N: bool = True
USE_TZ: bool = True

# Default primary key field type
DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

# Static files (CSS, JavaScript, Images)
STATIC_URL: str = get_env_value('STATIC_URL', 'static/')
STATIC_ROOT: Path = BASE_DIR / 'staticfiles'
STATICFILES_DIRS: List[Path] = [BASE_DIR / 'static']

# Media files
MEDIA_URL: str = get_env_value('MEDIA_URL', '/media/')
MEDIA_ROOT: Path = BASE_DIR / 'media'

# Custom user model
AUTH_USER_MODEL: str = 'users.CustomUser'

# Authentication settings
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'

# Logging configuration
# Ensure logs directory exists
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': '{\'time\':\'{asctime}\', \'level\':\'{levelname}\', \'name\':\'{name}\', \'module\':\'{module}\', \'message\':\'{message}\'}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'general.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
        'file_security': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
        'file_requests': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'requests.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
        'file_db': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'db.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True,
        },
    },
    'loggers': {
        # Root logger
        '': {
            'handlers': ['console', 'file_general', 'file_errors'],
            'level': 'INFO',
        },
        # Django loggers
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_requests', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file_requests'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_db'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        # Application loggers
        'inspireIA': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'inspireIA.request': {
            'handlers': ['console', 'file_requests'],
            'level': 'INFO',
            'propagate': False,
        },
        'catalog': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'interaction': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
