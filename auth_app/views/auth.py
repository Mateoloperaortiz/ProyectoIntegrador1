"""
Authentication views for the auth_app.

This module contains views related to user authentication, including registration, login, and logout.
It centralizes authentication functionality that was previously duplicated across multiple apps.
"""
from typing import Any, Dict, Optional, Union
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core.logging_utils import get_client_ip, log_user_activity, get_logger

# Get a logger for this module
logger = get_logger(__name__)
from auth_app.forms import CustomUserCreationForm, CustomUserLoginForm


@require_http_methods(["GET", "POST"])
def register(request: HttpRequest, template_name: str = 'auth_app/register.html', 
             success_redirect: str = 'auth_app:login', 
             authenticated_redirect: str = 'profile_app:dashboard') -> HttpResponse:
    """
    View for user registration.
    
    This view handles user registration, displaying the registration form
    and processing form submissions.
    
    Args:
        request: The HTTP request object
        template_name: The template to render
        success_redirect: Where to redirect after successful registration
        authenticated_redirect: Where to redirect authenticated users
        
    Returns:
        Rendered registration page or redirect to login
    """
    if request.user.is_authenticated:
        return redirect(authenticated_redirect)
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the registration using centralized logging
            ip_address = get_client_ip(request)
            
            # Log user activity
            log_user_activity(
                logger=logger,
                user_id=user.id,
                action="user_registered",
                details={
                    'username': user.username,
                    'email': user.email
                },
                ip_address=ip_address
            )
            
            # Redirect to login page
            return redirect(success_redirect)
    else:
        form = CustomUserCreationForm()
        
    return render(request, template_name, {
        'form': form
    })


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest, 
               template_name: str = 'auth_app/login.html',
               success_redirect: str = 'profile_app:dashboard',
               authenticated_redirect: str = 'profile_app:dashboard') -> HttpResponse:
    """
    View for user login.
    
    This view handles user login, displaying the login form
    and processing form submissions.
    
    Args:
        request: The HTTP request object
        template_name: The template to render
        success_redirect: Where to redirect after successful login
        authenticated_redirect: Where to redirect authenticated users
        
    Returns:
        Rendered login page or redirect to dashboard
    """
    if request.user.is_authenticated:
        return redirect(authenticated_redirect)
        
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Log the login using centralized logging
                ip_address = get_client_ip(request)
                
                # Log user activity
                log_user_activity(
                    logger=logger,
                    user_id=user.id,
                    action="user_login",
                    details={
                        'username': username,
                        'method': 'password'
                    },
                    ip_address=ip_address
                )
                
                # Redirect to dashboard or next page
                next_page = request.GET.get('next', success_redirect)
                return redirect(next_page)
    else:
        form = CustomUserLoginForm()
        
    return render(request, template_name, {
        'form': form
    })


def logout_view(request: HttpRequest, success_redirect: str = 'catalog:home') -> HttpResponse:
    """
    View for user logout.
    
    This view handles user logout, logging the user out and redirecting to the home page.
    
    Args:
        request: The HTTP request object
        success_redirect: Where to redirect after logout
        
    Returns:
        Redirect to home
    """
    if request.user.is_authenticated:
        # Get user data before logout
        user_id = request.user.id
        username = request.user.username
        
        # Log the logout using centralized logging
        ip_address = get_client_ip(request)
        
        # Logout the user
        logout(request)
        
        # Log user activity after logout
        log_user_activity(
            logger=logger,
            user_id=user_id,
            action="user_logout",
            details={
                'username': username
            },
            ip_address=ip_address
        )
        
    return redirect(success_redirect)