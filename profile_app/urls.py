"""
URL patterns for the profile app.

This module contains URL patterns for the profile app, including dashboard and settings.
"""
from typing import List, Union
from django.urls import path, URLPattern, URLResolver
from . import views

app_name = 'profile_app'

# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Dashboard URL
    path('', views.dashboard_view, name='dashboard'),
    
    # Profile updates
    path('update/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Favorites
    path('toggle-favorite/<uuid:ai_id>/', views.toggle_favorite, name='toggle_favorite'),
]