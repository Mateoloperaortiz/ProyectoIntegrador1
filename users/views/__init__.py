"""
Views package for the users app.

This package contains all views for the users app, organized into logical modules.
Dashboard and profile functionality has been moved to profile_app.
Authentication functionality has been moved to auth_app.
"""
# Import auth views (DEPRECATED) - these are now handled by direct URL redirects
# but kept for backward compatibility
import warnings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

def register(request: HttpRequest) -> HttpResponse:
    """DEPRECATED: Use URL pattern with RedirectView instead."""
    warnings.warn(
        "users.views.register is deprecated. Use RedirectView in urls.py instead.",
        DeprecationWarning, stacklevel=2
    )
    return redirect('auth_app:register')

def login_view(request: HttpRequest) -> HttpResponse:
    """DEPRECATED: Use URL pattern with RedirectView instead."""
    warnings.warn(
        "users.views.login_view is deprecated. Use RedirectView in urls.py instead.",
        DeprecationWarning, stacklevel=2
    )
    return redirect('auth_app:login')

def logout_view(request: HttpRequest) -> HttpResponse:
    """DEPRECATED: Use URL pattern with RedirectView instead."""
    warnings.warn(
        "users.views.logout_view is deprecated. Use RedirectView in urls.py instead.",
        DeprecationWarning, stacklevel=2
    )
    return redirect('auth_app:logout')
