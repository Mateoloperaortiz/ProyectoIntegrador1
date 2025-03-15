"""
Core context processors for templates.

This module contains context processors that add common data to all templates.
"""
from typing import Dict, Any
import datetime
from django.http import HttpRequest
from django.conf import settings


def global_settings(request: HttpRequest) -> Dict[str, Any]:
    """
    Add global settings to all templates.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Dictionary of global settings
    """
    return {
        'site_name': 'InspireIA',
        'site_description': 'Your AI Tools Catalog',
        'current_year': request.META.get('current_year', 2025),
    }


def user_context(request: HttpRequest) -> Dict[str, Any]:
    """
    Add user-related context to all templates.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Dictionary of user context
    """
    context = {
        'is_authenticated': request.user.is_authenticated,
    }
    
    if request.user.is_authenticated:
        context.update({
            'user_display_name': request.user.get_full_name() or request.user.username,
            'user_email': request.user.email,
        })
        
    return context


def version_info(request: HttpRequest) -> Dict[str, Any]:
    """
    Add version information to all templates.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Dictionary with version information
    """
    # Get environment type or default to development
    environment = getattr(settings, 'ENVIRONMENT', 'development')
    
    # Get build date (example implementation - in production this might
    # be populated by the CI/CD pipeline)
    build_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Get debug status
    debug_mode = getattr(settings, 'DEBUG', False)
    
    return {
        'app_version': '1.0.0',  # Update as needed for your versioning scheme
        'build_date': build_date,
        'environment': environment,
        'debug_mode': debug_mode,
    }
