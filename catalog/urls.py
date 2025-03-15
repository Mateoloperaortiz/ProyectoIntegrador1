from django.urls import path
from .views import (
    HomeView, CatalogView, ToolDetailView, 
    SearchView, StatisticsView, rate_tool
)

app_name = 'catalog'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('search/', SearchView.as_view(), name='search'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('tool/<slug:slug>/', ToolDetailView.as_view(), name='tool_detail'),
    path('tool/<slug:slug>/rate/', rate_tool, name='rate_tool'),
]