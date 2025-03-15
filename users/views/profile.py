"""
Profile views for the users app.

This module now redirects to the centralized profile_app views.
"""
from typing import Any, Dict, Optional, Union
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the centralized profile dashboard.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Redirect to profile dashboard
    """
    return redirect('profile_app:dashboard')


@login_required
def update_profile(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the centralized profile update view.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Redirect to profile update
    """
    return redirect('profile_app:update_profile')


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the centralized password change view.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Redirect to change password
    """
    return redirect('profile_app:change_password')
