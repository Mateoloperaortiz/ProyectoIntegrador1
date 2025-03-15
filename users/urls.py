from typing import List, Union
from django.urls import path, URLPattern, URLResolver
from django.views.generic.base import RedirectView
# Import directly from the module file
from users.views_admin import check_user_permissions

app_name = 'users'


# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Authentication URLs - Redirect to centralized auth_app
    path('login/', RedirectView.as_view(pattern_name='auth_app:login', query_string=True), name='login'),
    path('logout/', RedirectView.as_view(pattern_name='auth_app:logout', query_string=True), name='logout'),
    path('register/', RedirectView.as_view(pattern_name='auth_app:register', query_string=True), name='register'),
    
    # Redirect dashboard and profile URLs to profile_app
    path('dashboard/', RedirectView.as_view(pattern_name='profile_app:dashboard', query_string=True), name='dashboard'),
    path('profile/', RedirectView.as_view(pattern_name='profile_app:dashboard', query_string=False), name='profile'),
    path('profile/update/', RedirectView.as_view(url='/profile/?tab=profile', permanent=True), name='update_profile'),
    path('profile/change-password/', RedirectView.as_view(url='/profile/?tab=security', permanent=True), name='change_password'),
    
    # Admin URLs
    path('admin/users/<uuid:user_id>/permissions/', check_user_permissions, name='check_user_permissions'),
]