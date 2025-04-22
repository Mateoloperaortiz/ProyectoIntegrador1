from django.urls import path
from . import views

app_name = 'gemini_integration'

urlpatterns = [
    # File management endpoints
    path('files/', views.file_list, name='file_list'),
    path('files/upload/', views.file_upload, name='file_upload'),
    path('files/<int:file_id>/', views.file_detail, name='file_detail'),
    path('files/<int:file_id>/delete/', views.file_delete, name='file_delete'),
    path('file-manager/', views.file_manager, name='file_manager'),
]
