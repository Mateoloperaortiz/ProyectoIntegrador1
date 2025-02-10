# catalog/urls.py
from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.IAListView.as_view(), name='ia_list'),
]

