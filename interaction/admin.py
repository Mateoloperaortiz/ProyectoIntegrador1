from django.contrib import admin
from .models import Conversation, Message, Favorite

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tool', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'tool')
    search_fields = ('user__username', 'user__email', 'tool__name', 'title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [MessageInline]
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'is_from_user', 'content_preview', 'timestamp')
    list_filter = ('is_from_user', 'timestamp')
    search_fields = ('content', 'conversation__user__username')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'user__email', 'tool__name')
