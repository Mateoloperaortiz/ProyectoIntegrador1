"""
URL patterns for the profile app.

This module contains URL patterns for the profile app, including dashboard and settings.
"""
from typing import List, Union
from django.urls import path, URLPattern, URLResolver
from django.views.generic.base import RedirectView
from profile_app.views import dashboard

app_name = 'profile_app'

# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Dashboard URL
    path('', dashboard.dashboard_view, name='dashboard'),
    
    # Profile updates
    path('update/', dashboard.update_profile, name='update_profile'),
    path('change-password/', dashboard.change_password, name='change_password'),
    
    # Favorites
    path('toggle-favorite/<uuid:ai_id>/', dashboard.toggle_favorite, name='toggle_favorite'),
    
    # Additional settings
    path('notifications/', dashboard.notification_settings, name='notification_settings'),
    
    # Legacy redirects - catch any old URLs from users app
    path('settings/', RedirectView.as_view(pattern_name='profile_app:dashboard', query_string=True), name='settings'),
    path('security/', RedirectView.as_view(url='/?tab=security', permanent=True), name='security'),
]