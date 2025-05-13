from django.urls import path
from .views import (
    toggle_favorite, HomeView, CatalogView, ToolDetailView, 
    SearchView, StatisticsView
)

app_name = 'catalog'

urlpatterns = [
    path('favorite/toggle/<int:tool_id>/', toggle_favorite, name='toggle_favorite'),
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('search/', SearchView.as_view(), name='search'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('tool/<slug:slug>/', ToolDetailView.as_view(), name='tool_detail'),
]