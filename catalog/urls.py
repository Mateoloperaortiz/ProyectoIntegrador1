from django.urls import path
from . import views

app_name = 'catalog'  # Application namespace for URL naming

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Catalog list with filtering options
    path('tools/', views.CatalogView.as_view(), name='tool_list'),
    
    # Tool detail view
    path('tools/<uuid:pk>/', views.AIToolDetailView.as_view(), name='tool_detail'),
    
    # Category-specific tool list
    path('category/<str:category>/', views.CatalogView.as_view(), name='category_list'),
    
    # Search results
    path('search/', views.CatalogView.as_view(), name='search'),
    
    # Legacy URLs (for backward compatibility)
    path('presentation/<uuid:id>/', views.AIToolDetailView.as_view(), name='presentationAI'),
]
