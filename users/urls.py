from typing import List, Union
from django.urls import path, URLPattern, URLResolver
from django.views.generic.base import RedirectView
# Authentication views are now in auth_app
from .views.auth import login_view, logout_view, register
from .views.dashboard import dashboard
# Import directly from the module file
from users.views_admin import check_user_permissions

app_name = 'users'


# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    
    # Redirect old profile URLs to dashboard with appropriate tabs
    path('profile/', RedirectView.as_view(pattern_name='users:dashboard', query_string=False), name='profile'),
    path('profile/update/', RedirectView.as_view(url='/users/dashboard/?tab=profile', permanent=True), name='update_profile'),
    path('profile/change-password/', RedirectView.as_view(url='/users/dashboard/?tab=security', permanent=True), name='change_password'),
    
    # Dashboard URL
    path('dashboard/', dashboard, name='dashboard'),
    
    # Admin URLs
    path('admin/users/<uuid:user_id>/permissions/', check_user_permissions, name='check_user_permissions'),
]

