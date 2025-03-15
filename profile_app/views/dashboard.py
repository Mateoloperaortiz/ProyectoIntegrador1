"""
Dashboard views for the profile app.

This module contains views for the user dashboard, profile management, and related functionality.
It consolidates functionality previously spread across multiple apps (users and profile_app).
"""
from typing import Any, Dict, Optional, Union
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from catalog.models import AITool
from interaction.models import Conversation
from users.forms import UserProfileForm
from profile_app.services import get_user_profile_data


User = get_user_model()


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    View for the user dashboard.
    
    This view renders the user's dashboard, showing profile information, favorites,
    recent conversations, and statistics based on the selected tab.
    
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
    profile_data['password_form'] = PasswordChangeForm(request.user)
    
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
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        messages.error(request, 'There was an error updating your profile. Please check the form.')
    
    # Redirect back to dashboard with profile tab active
    return redirect(f"{redirect('profile_app:dashboard')}?tab=profile")


@login_required
@require_http_methods(["POST"])
def change_password(request: HttpRequest) -> HttpResponse:
    """
    View for changing the user's password.
    
    This view handles changing the user's password.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Redirect to dashboard with success/error message
    """
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        # Update the session to prevent the user from being logged out
        update_session_auth_hash(request, user)
        messages.success(request, 'Your password was successfully updated!')
    else:
        # Add specific field errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        messages.error(request, 'Please correct the errors in the form.')
    
    # Redirect back to dashboard with security tab active
    return redirect(f"{redirect('profile_app:dashboard')}?tab=security")


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request: HttpRequest, ai_id: str) -> Union[JsonResponse, HttpResponse]:
    """
    View for toggling an AI tool as a favorite.
    
    This view handles adding or removing an AI tool from the user's favorites.
    
    Args:
        request: The HTTP request object
        ai_id: The ID of the AI tool
        
    Returns:
        JSON response with the new favorite status or redirect to dashboard
    """
    user = request.user
    ai_tool = get_object_or_404(AITool, id=ai_id)
    
    # Check if the AI tool is already a favorite
    is_favorite = user.favorites.filter(id=ai_tool.id).exists()
    
    if is_favorite:
        # Remove from favorites
        user.favorites.remove(ai_tool)
        is_favorite = False
        messages.success(request, f'"{ai_tool.name}" removed from favorites')
    else:
        # Add to favorites
        user.favorites.add(ai_tool)
        is_favorite = True
        messages.success(request, f'"{ai_tool.name}" added to favorites')
    
    # Check if the request expects JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': is_favorite
        })
    
    # Otherwise redirect back to the favorites tab
    return redirect(f"{redirect('profile_app:dashboard')}?tab=favorites")


@login_required
@require_http_methods(["GET", "POST"])
def notification_settings(request: HttpRequest) -> HttpResponse:
    """
    View for managing notification settings.
    
    This view handles updating notification preferences.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Redirect to dashboard or rendered settings page
    """
    # Placeholder view for future implementation
    if request.method == 'POST':
        # Process notification settings
        messages.success(request, 'Notification settings updated successfully!')
        return redirect(f"{redirect('profile_app:dashboard')}?tab=notifications")
    
    # If GET request, just redirect to the dashboard with notifications tab
    return redirect(f"{redirect('profile_app:dashboard')}?tab=notifications")