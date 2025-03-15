"""
Authentication views for the catalog app.

This module contains views related to user authentication, including registration, login, and logout.
These functions now redirect to the centralized auth_app views.
"""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

def register_view(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the centralized register view.
    """
    return redirect('auth_app:register')

def login_view(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the centralized login view.
    """
    return redirect('auth_app:login')

def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the centralized logout view.
    """
    return redirect('auth_app:logout')