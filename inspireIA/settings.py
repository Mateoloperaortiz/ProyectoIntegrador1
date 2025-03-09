"""
Django settings for inspireIA project.

This file imports and uses the appropriate settings module based on environment.
"""
import os
import sys
from pathlib import Path

# Default to development settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inspireIA.settings.development')

# Import the appropriate settings module
from .settings.base import *

# Use development settings by default
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    from .settings.development import *
elif os.environ['DJANGO_SETTINGS_MODULE'] == 'inspireIA.settings.production':
    from .settings.production import *
elif os.environ['DJANGO_SETTINGS_MODULE'] == 'inspireIA.settings.development':
    from .settings.development import *
