from django.urls import path
from .views import (
    toggle_favorite, ConversationListView, ConversationDetailView,
    start_conversation, send_message, update_conversation_title,
    delete_conversation
)

app_name = 'interaction'

urlpatterns = [
    path('favorite/toggle/<int:tool_id>/', toggle_favorite, name='toggle_favorite'),
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<uuid:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/start/<int:tool_id>/', start_conversation, name='start_conversation'),
    path('conversations/<uuid:conversation_id>/send/', send_message, name='send_message'),
    path('conversations/<uuid:conversation_id>/update-title/', update_conversation_title, name='update_title'),
    path('conversations/<uuid:conversation_id>/delete/', delete_conversation, name='delete_conversation'),
]