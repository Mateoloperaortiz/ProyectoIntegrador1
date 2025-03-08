"""
Development settings for inspireIA project.
"""
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6)gdd^&=840x=7@6yd7+47m-mi3q+fjg55xd%nyhhk8d-h__@2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Additional development-specific apps
INSTALLED_APPS += [
    # 'debug_toolbar',  # Uncomment to enable Django Debug Toolbar
]

# Additional development middleware
# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # Uncomment for Django Debug Toolbar

# Show emails in the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configure logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
AUTH_USER_MODEL = 'users.CustomUser'
