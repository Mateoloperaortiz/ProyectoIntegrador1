""" urls.py in inspireIA project
URL configuration for inspireIA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from typing import List, Union, cast
from django.contrib import admin
from django.urls import path, include, URLPattern, URLResolver
from catalog.views.home import home
from django.conf import settings
from django.conf.urls.static import static
from .admin import admin_site
from core.views import service_worker

# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Admin sites
    path('admin/', admin.site.urls),  # Default admin site (for backward compatibility)
    path('inspire-admin/', admin_site.urls, name='inspire_admin'),  # Custom admin site
    
    # Service worker at root level
    path('service-worker.js', service_worker, name='service_worker'),
    
    # Home page
    path('', home, name='home'),
    
    # Catalog app - includes all catalog-related URLs
    path('catalog/', include('catalog.urls', namespace='catalog')),
    
    # Interaction app - handles chats, favorites, sharing
    path('interaction/', include('interaction.urls', namespace='interaction')),
    
    # Authentication app - centralized auth functionality
    path('auth/', include('auth_app.urls', namespace='auth_app')),
    
    # Profile app - unified profile functionality
    path('profile/', include('profile_app.urls', namespace='profile_app')),
    
    # Users app
    path('users/', include('users.urls')),
    
    # API app
    path('api/', include('api.urls')),
    
    # Core app - includes utilities and demos
    path('core/', include('core.urls', namespace='core')),
]

# Serve media files in development
if settings.DEBUG:
    # The static() function returns a list of URLPatterns
    static_patterns: List[URLPattern] = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static_patterns