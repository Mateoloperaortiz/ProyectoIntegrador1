from django.contrib import admin
from .models import Conversation, Message, FavoritePrompt, SharedChat
from inspireIA.admin import admin_site
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.http import HttpRequest
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable, Type, cast
from django.db.models.query import QuerySet
from utils.admin_utils import (
    OptimizedQuerysetMixin, 
    AdminActionMessageMixin, 
    ContentPreviewMixin, 
    ExportModelMixin,
    admin_display
)

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('timestamp', 'content_preview')
    fields = ('is_user', 'content_preview', 'timestamp')
    
    @admin_display(description='Content')
    def content_preview(self, obj: Message) -> str:
        """Display a preview of the message content"""
        if len(obj.content) > 100:
            return obj.content[:100] + '...'
        return obj.content
    
    def has_add_permission(self, request: HttpRequest, obj: Optional[Conversation] = None) -> bool:
        return False

class ConversationAdmin(OptimizedQuerysetMixin, AdminActionMessageMixin, ExportModelMixin, admin.ModelAdmin):
    list_display = ('title', 'user', 'ai_tool', 'message_count', 'created_at', 'updated_at')
    list_filter = ('ai_tool', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'user__email', 'ai_tool__name')
    readonly_fields = ('created_at', 'updated_at', 'id')
    date_hierarchy = 'created_at'
    inlines = [MessageInline]
    raw_id_fields = ('user', 'ai_tool')
    
    # OptimizedQuerysetMixin configuration
    select_related_fields = ['user', 'ai_tool']
    prefetch_related_fields = ['message_set']
    
    # ExportModelMixin configuration
    export_filename = 'conversations'
    export_formats = ['csv', 'json']
    export_fields = [
        'id', 'title', 'user__username', 'ai_tool__name', 
        'created_at', 'updated_at'
    ]
    export_headers = [
        'ID', 'Title', 'User', 'AI Tool', 
        'Created At', 'Updated At'
    ]
    
    actions = [
        'mark_as_important',
        'archive_conversations'
    ]
    
    @admin_display(description='Messages')
    def message_count(self, obj: Conversation) -> int:
        """Display the number of messages in this conversation"""
        return obj.message_set.count()
    
    def mark_as_important(self, request, queryset):
        """Mark selected conversations as important by adding '[IMPORTANT]' to the title"""
        count = 0
        for conversation in queryset:
            if not conversation.title.startswith('[IMPORTANT]'):
                conversation.title = f'[IMPORTANT] {conversation.title}'
                conversation.save()
                count += 1
        
        self.message_custom_result(
            request, 
            count, 
            "marked as important", 
            "conversation", 
            "conversations"
        )
    mark_as_important.short_description = "⭐ Mark as important"
    
    def archive_conversations(self, request, queryset):
        """Archive selected conversations by adding '[ARCHIVED]' to the title"""
        count = 0
        for conversation in queryset:
            if not conversation.title.startswith('[ARCHIVED]'):
                conversation.title = f'[ARCHIVED] {conversation.title}'
                conversation.save()
                count += 1
        
        self.message_custom_result(
            request, 
            count, 
            "archived", 
            "conversation", 
            "conversations"
        )
    archive_conversations.short_description = "📦 Archive conversations"

class MessageAdmin(OptimizedQuerysetMixin, ContentPreviewMixin, admin.ModelAdmin):
    list_display = ('conversation_link', 'is_user', 'content_preview', 'timestamp')
    list_filter = ('is_user', 'timestamp', 'conversation__ai_tool')
    search_fields = ('content', 'conversation__title', 'conversation__user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    raw_id_fields = ('conversation',)
    
    # OptimizedQuerysetMixin configuration
    select_related_fields = ['conversation', 'conversation__user', 'conversation__ai_tool']
    
    # ContentPreviewMixin configuration
    preview_fields = {
        'content_preview': {
            'field': 'content', 
            'max_length': 50, 
            'description': 'Content Preview'
        }
    }
    
    @admin_display(description='Conversation', ordering='conversation__title')
    def conversation_link(self, obj):
        """Display a link to the conversation"""
        url = reverse('admin:interaction_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, obj.conversation.title)

class FavoritePromptAdmin(OptimizedQuerysetMixin, ContentPreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'user', 'ai_tools_list', 'prompt_preview', 'created_at')
    list_filter = ('ai_tools', 'created_at')
    search_fields = ('title', 'prompt_text', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'id')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    filter_horizontal = ('ai_tools',)
    
    # OptimizedQuerysetMixin configuration
    select_related_fields = ['user']
    prefetch_related_fields = ['ai_tools']
    
    # ContentPreviewMixin configuration
    preview_fields = {
        'prompt_preview': {
            'field': 'prompt_text', 
            'max_length': 50, 
            'description': 'Prompt Preview'
        }
    }
    
    @admin_display(description='AI Tools')
    def ai_tools_list(self, obj):
        """Display a comma-separated list of AI tools"""
        return ", ".join([tool.name for tool in obj.ai_tools.all()])

class SharedChatAdmin(OptimizedQuerysetMixin, admin.ModelAdmin):
    list_display = ('conversation_link', 'created_by_display', 'recipient_display', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('conversation__title', 'created_by__username', 'recipient__username')
    readonly_fields = ('created_at', 'access_token', 'id')
    date_hierarchy = 'created_at'
    raw_id_fields = ('conversation', 'created_by', 'recipient')
    
    # OptimizedQuerysetMixin configuration
    select_related_fields = ['conversation', 'created_by', 'recipient']
    
    @admin_display(description='Conversation', ordering='conversation__title')
    def conversation_link(self, obj):
        """Display a link to the conversation"""
        url = reverse('admin:interaction_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, obj.conversation.title)
    
    @admin_display(description='Shared By', ordering='created_by__username')
    def created_by_display(self, obj):
        """Display the user who created the shared chat"""
        if obj.created_by:
            url = reverse('admin:users_customuser_change', args=[obj.created_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.created_by.username)
        return '-'
    
    @admin_display(description='Shared With', ordering='recipient__username')
    def recipient_display(self, obj):
        """Display the user the conversation is shared with"""
        if obj.recipient:
            url = reverse('admin:users_customuser_change', args=[obj.recipient.id])
            return format_html('<a href="{}">{}</a>', url, obj.recipient.username)
        return 'Public' if obj.is_public else '-'

# Register the models
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(FavoritePrompt, FavoritePromptAdmin)
admin.site.register(SharedChat, SharedChatAdmin)

# Also register with our custom admin site
admin_site.register(Conversation, ConversationAdmin)
admin_site.register(Message, MessageAdmin)
admin_site.register(FavoritePrompt, FavoritePromptAdmin)
admin_site.register(SharedChat, SharedChatAdmin)
