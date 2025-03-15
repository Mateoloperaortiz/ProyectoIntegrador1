"""
Views package for the users app.

This package contains all views for the users app, organized into logical modules.
Dashboard and profile functionality has been moved to profile_app.
"""
# Import views for easy access
from .auth import register, login_view, logout_view
