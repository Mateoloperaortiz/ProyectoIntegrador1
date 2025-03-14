from django.urls import path, URLPattern, URLResolver
from typing import List, Union
from . import views

app_name = 'catalog'

# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    # Main pages
    path('', views.home, name='home'),
    path('models/', views.CatalogView.as_view(), name='catalog'),
    path(' presentation/<uuid:id>/', views.presentationAI, name='presentationAI'),
    path('compare/', views.compare_tools, name='compare'),
    
    # User authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    
    # Favorites
    path('ai/<uuid:ai_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
]
