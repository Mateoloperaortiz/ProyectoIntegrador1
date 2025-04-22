from django.urls import path
from . import views

app_name = 'openai_integration'

urlpatterns = [
    # File management
    path('files/', views.file_list_view, name='file_list'),
    path('files/upload/', views.file_upload_view, name='file_upload'),
    path('files/<str:file_id>/', views.file_detail_view, name='file_detail'),
    path('files/<str:file_id>/content/', views.file_content_view, name='file_content'),
    path('files/<str:file_id>/delete/', views.file_delete_view, name='file_delete'),
    
    # Text-to-Speech
    path('tts/', views.text_to_speech_view, name='tts'),
    
    # Speech-to-Text
    path('stt/', views.speech_to_text_view, name='stt'),
    
    # AJAX endpoints
    path('api/files/upload/', views.ajax_file_upload, name='ajax_file_upload'),
    path('api/stt/', views.ajax_speech_to_text, name='ajax_stt'),
]
