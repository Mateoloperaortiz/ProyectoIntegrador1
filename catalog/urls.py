from django.urls import path, URLPattern, URLResolver
from typing import List, Union
from django.views.generic.base import RedirectView
from . import views

app_name = 'catalog'

# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Main pages
    path('', views.home, name='home'),
    path('list/', views.CatalogView.as_view(), name='catalog'),  # /catalog/list/ for catalog view
    path('presentation/<uuid:id>/', views.presentationAI, name='presentationAI'),  # Fixed space in URL
    path('compare/', views.compare_tools, name='compare'),
    
    # User authentication - Redirects to centralized auth_app
    path('register/', RedirectView.as_view(pattern_name='auth_app:register', query_string=True), name='register'),
    path('login/', RedirectView.as_view(pattern_name='auth_app:login', query_string=True), name='login'),
    path('logout/', RedirectView.as_view(pattern_name='auth_app:logout', query_string=True), name='logout'),
    path('profile/', RedirectView.as_view(pattern_name='profile_app:dashboard', query_string=True), name='profile'),
    
    # Favorites - Redirect to profile_app
    path('ai/<uuid:ai_id>/favorite/', RedirectView.as_view(pattern_name='profile_app:toggle_favorite', query_string=True), name='toggle_favorite'),
]
