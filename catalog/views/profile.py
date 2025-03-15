"""
Profile views for the catalog app.

This module now redirects to the centralized profile_app views.
"""
from typing import Any, Dict, Optional, Union
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404

from catalog.models import AITool

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
def toggle_favorite(request: HttpRequest, ai_id: str) -> HttpResponse:
    """
    Redirects to the centralized toggle favorite view.
    
    Args:
        request: The HTTP request object
        ai_id: The ID of the AI tool
        
    Returns:
        Redirect to profile toggle favorite
    """
    return redirect('profile_app:toggle_favorite', ai_id=ai_id)
