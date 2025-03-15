from typing import List, Union
from django.urls import path, URLPattern, URLResolver
from .views import chat, conversations, favorites, sharing

# Register the app namespace
app_name = 'interaction'

# Type hint for URL patterns
urlpatterns: List[Union[URLPattern, URLResolver]] = [    
    # Direct chat URLs
    path('direct-chat/', chat.direct_chat, name='direct_chat'),
    path('direct-chat/message/', chat.direct_chat_message, name='direct_chat_message'),
    # Unified chat templates
    path('unified/chat/', chat.direct_chat, {'template': 'interaction/unified/direct_chat.html'}, name='unified_chat'),
    path('unified/chat/modern/', chat.direct_chat, {'template': 'interaction/unified/modern_chat.html'}, name='modern_chat'),
    path('unified/chat/minimal/', chat.direct_chat, {'template': 'interaction/unified/minimal_debug_chat.html'}, name='minimal_chat'),
    path('unified/chat/enhanced/', chat.direct_chat, {'template': 'interaction/unified/enhanced_chat.html'}, name='enhanced_chat'),
    # Chat URLs
    path('chat/', chat.chat_selection, name='chat_selection'),
    # Important: Order matters! More specific patterns should come first
    path('chat/conversation/<uuid:conversation_id>/', chat.chat_view, name='continue_conversation'),
    path('chat/conversation/<uuid:conversation_id>/send/', chat.send_message, name='send_message'),
    path('chat/<uuid:ai_id>/', chat.chat_view, name='chat'),
    path('conversations/', conversations.conversation_history, name='conversation_history'),
    path('conversations/<uuid:conversation_id>/delete/', conversations.delete_conversation, name='delete_conversation'),
    path('conversations/<uuid:conversation_id>/download/<str:format>/', conversations.download_conversation, name='download_conversation'),
    
    # Favorite prompts URLs
    path('prompts/', favorites.favorite_prompts, name='favorite_prompts'),
    path('prompts/ai/<uuid:ai_id>/', favorites.favorite_prompts, name='ai_favorite_prompts'),
    path('prompts/save/', favorites.save_favorite_prompt, name='save_favorite_prompt'),
    path('prompts/<uuid:prompt_id>/delete/', favorites.delete_favorite_prompt, name='delete_favorite_prompt'),
    
    # Sharing URLs
    path('share/<uuid:conversation_id>/', sharing.share_conversation_form, name='share_conversation_form'),
    path('share/<uuid:conversation_id>/submit/', sharing.share_conversation, name='share_conversation'),
    path('shared/<str:access_token>/', sharing.view_shared_chat, name='view_shared_chat'),
    path('shared/conversation/<str:access_token>/', sharing.shared_conversation, name='shared_conversation'),
    path('shared/manage/', sharing.manage_shared_chats, name='manage_shared_chats'),
    path('shared/<uuid:shared_chat_id>/delete/', sharing.delete_shared_chat, name='delete_shared_chat'),
    path('shared/expired/', sharing.shared_expired, name='shared_expired'),
    path('shared/access-denied/', sharing.shared_access_denied, name='shared_access_denied'),
] 