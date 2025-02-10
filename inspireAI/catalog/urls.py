# catalog/urls.py
from django.urls import path
from catalog.views import IAListView, IADetailView, IACreateView, IAUpdateView, IADeleteView

app_name = 'catalog'

urlpatterns = [
    path('', IAListView.as_view(), name='ia_list'),
    path('<int:pk>/', IADetailView.as_view(), name='ia_detail'),
    path('create/', IACreateView.as_view(), name='ia_create'),
    path('<int:pk>/edit/', IAUpdateView.as_view(), name='ia_edit'),
    path('<int:pk>/delete/', IADeleteView.as_view(), name='ia_delete'),

]

