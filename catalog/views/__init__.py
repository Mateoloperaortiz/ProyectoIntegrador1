"""
Views package for the catalog app.

This package contains all views for the catalog app, organized into logical modules.
"""
# Import constants
from ..constants import CATEGORIES

# Import views for easy access
from .catalog import CatalogView, catalog_view, ModelsView, models_view
from .ai_tools import AIToolDetailView, presentationAI, compare_tools
from .home import home

# Import profile views - redirects to profile_app
from .profile import profile_view, toggle_favorite

# Import auth views (DEPRECATED) - these are now handled by direct URL redirects
# but kept for backward compatibility
import warnings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

def register_view(request: HttpRequest) -> HttpResponse:
    """DEPRECATED: Use URL pattern with RedirectView instead."""
    warnings.warn(
        "catalog.views.register_view is deprecated. Use RedirectView in urls.py instead.",
        DeprecationWarning, stacklevel=2
    )
    return redirect('auth_app:register')

def login_view(request: HttpRequest) -> HttpResponse:
    """DEPRECATED: Use URL pattern with RedirectView instead."""
    warnings.warn(
        "catalog.views.login_view is deprecated. Use RedirectView in urls.py instead.",
        DeprecationWarning, stacklevel=2
    )
    return redirect('auth_app:login')

def logout_view(request: HttpRequest) -> HttpResponse:
    """DEPRECATED: Use URL pattern with RedirectView instead."""
    warnings.warn(
        "catalog.views.logout_view is deprecated. Use RedirectView in urls.py instead.",
        DeprecationWarning, stacklevel=2
    )
    return redirect('auth_app:logout')
