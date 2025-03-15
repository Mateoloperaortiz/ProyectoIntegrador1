"""
Settings views for the profile app.

This module contains views for user settings, including password management,
notification preferences, and account settings.
"""
from typing import Any, Dict, Optional, Union
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request: HttpRequest) -> HttpResponse:
    """
    View for changing the user's password.
    
    This view handles changing the user's password.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered password change page or redirect to dashboard
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile_app:dashboard') + '?tab=security'
        else:
            # Add specific field errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            messages.error(request, 'Please correct the errors in the form.')
            return redirect('profile_app:dashboard') + '?tab=security'
    else:
        # If GET request, just redirect to the dashboard with security tab
        return redirect('profile_app:dashboard') + '?tab=security'


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
        return redirect('profile_app:dashboard') + '?tab=notifications'
    
    return render(request, 'profile_app/notification_settings.html', {
        'user': request.user
    })