from typing import List, Union
from django.urls import path, URLPattern, URLResolver
from django.views.generic.base import RedirectView
# Authentication views are now in auth_app
from .views.auth import login_view, logout_view, register
# Import directly from the module file
from users.views_admin import check_user_permissions

app_name = 'users'


# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    
    # Redirect dashboard and profile URLs to profile_app
    path('dashboard/', RedirectView.as_view(pattern_name='profile_app:dashboard', query_string=True), name='dashboard'),
    path('profile/', RedirectView.as_view(pattern_name='profile_app:dashboard', query_string=False), name='profile'),
    path('profile/update/', RedirectView.as_view(url='/profile/?tab=profile', permanent=True), name='update_profile'),
    path('profile/change-password/', RedirectView.as_view(url='/profile/?tab=security', permanent=True), name='change_password'),
    
    # Admin URLs
    path('admin/users/<uuid:user_id>/permissions/', check_user_permissions, name='check_user_permissions'),
]