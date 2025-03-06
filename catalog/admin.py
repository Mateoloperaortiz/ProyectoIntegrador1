from django.contrib import admin
from .models import AITool, UserFavorite, Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('timestamp',)

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'ai_tool', 'user', 'created_at', 'updated_at')
    list_filter = ('ai_tool', 'created_at')
    search_fields = ('title', 'user__username', 'ai_tool__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]

class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ai_tool', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'ai_tool__name')

class AIToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'category', 'popularity', 'api_type', 'is_featured')
    list_filter = ('category', 'api_type', 'is_featured')
    search_fields = ('name', 'provider', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'provider', 'category', 'description', 'popularity', 'image', 'endpoint')
        }),
        ('API Integration', {
            'fields': ('api_type', 'api_model', 'api_endpoint', 'is_featured'),
            'classes': ('collapse',),
            'description': 'Configure external API integrations for this AI tool'
        }),
    )
    readonly_fields = ('id',)

# Register models
admin.site.register(AITool, AIToolAdmin)
admin.site.register(UserFavorite, UserFavoriteAdmin)
admin.site.register(Conversation, ConversationAdmin)
