""" urls.py in inspireIA project
URL configuration for inspireIA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from catalog import views as catalog_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main pages
    path('', catalog_views.home, name='home'),
    path('catalog/', catalog_views.catalog_view, name='catalog'),
    path('catalog/presentation/<uuid:id>/', catalog_views.presentationAI, name='presentationAI'),
    path('catalog/compare/', catalog_views.compare_tools, name='compare'),
    
    # User authentication
    path('register/', catalog_views.register_view, name='register'),
    path('login/', catalog_views.login_view, name='login'),
    path('logout/', catalog_views.logout_view, name='logout'),
    path('profile/', catalog_views.profile_view, name='profile'),
    
    # API Integration - Chat
    path('chat/', catalog_views.openrouter_chat_view, name='openrouter_chat'),
    path('chat/<uuid:ai_id>/', catalog_views.chat_view, name='chat'),
    path('chat/<uuid:conversation_id>/send/', catalog_views.send_message, name='send_message'),
    path('conversation/<uuid:conversation_id>/download/<str:format>/', catalog_views.download_conversation, name='download_conversation'),
    
    # Favorites
    path('ai/<uuid:ai_id>/favorite/', catalog_views.toggle_favorite, name='toggle_favorite'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

