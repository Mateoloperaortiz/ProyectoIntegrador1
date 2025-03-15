"""
Dashboard views for the profile app.

This module contains views for the user dashboard, profile management, and related functionality.
"""
from typing import Any, Dict, Optional, Union
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from catalog.models import AITool
from users.forms import UserProfileForm
from profile_app.services import get_user_profile_data


User = get_user_model()


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    View for the user dashboard.
    
    This view renders the user's dashboard, showing profile information, favorites,
    recent conversations, and statistics.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered dashboard page
    """
    # Get the active tab from the query string, default to 'overview'
    active_tab = request.GET.get('tab', 'overview')
    
    # Get user profile data from service
    profile_data = get_user_profile_data(request.user.id)
    
    # Add active tab to context
    profile_data['active_tab'] = active_tab
    
    # Add forms to context
    profile_data['profile_form'] = UserProfileForm(instance=request.user)
    
    return render(request, 'profile_app/dashboard.html', profile_data)


@login_required
@require_http_methods(["POST"])
def update_profile(request: HttpRequest) -> HttpResponse:
    """
    View for updating the user's profile.
    
    This view handles processing the profile update form.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Redirect to dashboard with success/error message
    """
    form = UserProfileForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your profile was successfully updated!')
        return redirect('profile_app:dashboard')
    else:
        messages.error(request, 'There was an error updating your profile. Please check the form.')
        
    # If form is invalid, redirect back to dashboard with profile tab active
    return redirect('profile_app:dashboard') + '?tab=profile'


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request: HttpRequest, ai_id: str) -> JsonResponse:
    """
    View for toggling an AI tool as a favorite.
    
    This view handles adding or removing an AI tool from the user's favorites.
    
    Args:
        request: The HTTP request object
        ai_id: The ID of the AI tool
        
    Returns:
        JSON response with the new favorite status
    """
    user = request.user
    ai_tool = get_object_or_404(AITool, id=ai_id)
    
    # Check if the AI tool is already a favorite
    is_favorite = user.favorites.filter(id=ai_tool.id).exists()
    
    if is_favorite:
        # Remove from favorites
        user.favorites.remove(ai_tool)
        is_favorite = False
    else:
        # Add to favorites
        user.favorites.add(ai_tool)
        is_favorite = True
    
    return JsonResponse({
        'is_favorite': is_favorite
    })