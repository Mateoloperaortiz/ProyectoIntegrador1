"""
Django settings module for inspireIA project.
"""
import os

# Default to development settings
from .development import *

# Use production settings if DJANGO_ENV is set to 'production'
if os.environ.get('DJANGO_ENV') == 'production':
    from .production import *
