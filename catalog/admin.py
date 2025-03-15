from django.contrib import admin
from .models import AITool, Rating
from inspireIA.admin import admin_site
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpRequest
from django.core.management import call_command
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable, Type, cast
from django.db.models.query import QuerySet
from utils.admin_utils import (
    OptimizedQuerysetMixin, 
    AdminActionMessageMixin, 
    DuplicateModelMixin, 
    ExportModelMixin,
    admin_display
)


class AIToolAdmin(OptimizedQuerysetMixin, AdminActionMessageMixin, DuplicateModelMixin, admin.ModelAdmin):
    list_display = ('name', 'provider', 'category', 'popularity', 'api_type', 'is_featured', 'view_favorites_count', 'image_preview')
    list_filter = ('category', 'api_type', 'is_featured', 'provider')
    search_fields = ('name', 'provider', 'description', 'category')
    list_editable = ('is_featured',)
    list_per_page = 20
    
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
    
    # OptimizedQuerysetMixin configuration
    prefetch_related_fields = ['favorited_by']
    
    # DuplicateModelMixin configuration
    duplicate_name_field = 'name'
    duplicate_name_prefix = 'Copy of'
    duplicate_reset_fields = {
        'popularity': 0,
        'is_featured': False,
    }
    duplicate_file_fields = ['image']
    
    actions = [
        'feature_tools', 
        'unfeature_tools', 
        'increase_popularity', 
        'reset_popularity',
        'duplicate_objects',  # From DuplicateModelMixin
        'refresh_logos'
    ]
    
    @admin_display(description='Favorited by')
    def view_favorites_count(self, obj: AITool) -> str:
        """Display the number of users who have favorited this tool"""
        count = obj.favorited_by.count()
        url = reverse('admin:users_customuser_changelist') + f'?favorites__id__exact={obj.id}'
        return format_html('<a href="{}">{} users</a>', url, count)
    
    @admin_display(description='Logo')
    def image_preview(self, obj: AITool) -> str:
        """Display a thumbnail of the AI tool image"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        # If no image, display a placeholder with the first letter of the tool name
        return format_html(
            '<div style="width:50px; height:50px; border-radius:8px; background:linear-gradient(135deg, #5f4b8b, #9168c0); color:white; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:20px;">{}</div>',
            obj.name[0].upper()
        )
    
    def feature_tools(self, request, queryset):
        """Mark selected tools as featured"""
        updated = queryset.update(is_featured=True)
        self.message_custom_result(
            request, 
            updated, 
            "marked as featured and will appear prominently in the catalog", 
            "AI tool was", 
            "AI tools were"
        )
    feature_tools.short_description = "✨ Feature selected AI tools"
    
    def unfeature_tools(self, request, queryset):
        """Unmark selected tools as featured"""
        updated = queryset.update(is_featured=False)
        self.message_custom_result(
            request, 
            updated, 
            "unmarked as featured and will no longer appear in featured sections", 
            "AI tool was", 
            "AI tools were"
        )
    unfeature_tools.short_description = "⬇️ Unfeature selected AI tools"
    
    def increase_popularity(self, request, queryset):
        """Increase popularity of selected tools by 10"""
        for tool in queryset:
            tool.popularity += 10
            tool.save()
        self.message_custom_result(
            request, 
            queryset.count(), 
            "increased in popularity by 10 points", 
            "AI tool", 
            "AI tools"
        )
    increase_popularity.short_description = "📈 Increase popularity by 10"
    
    def reset_popularity(self, request, queryset):
        """Reset popularity of selected tools to 0"""
        updated = queryset.update(popularity=0)
        self.message_custom_result(
            request, 
            updated, 
            "reset to 0 popularity", 
            "AI tool", 
            "AI tools"
        )
    reset_popularity.short_description = "🔄 Reset popularity to 0"
    
    def refresh_logos(self, request, queryset):
        """Refresh logos for selected AI tools using high-quality sources"""
        try:
            # Note which tools were selected
            selected_names = list(queryset.values_list('name', flat=True))
            
            # We'll use our management command to refresh logos
            call_command('fetch_ai_tool_logos', force=True)
            
            # Report success
            self.message_user(
                request,
                f"Successfully refreshed logos for {len(selected_names)} AI tools: {', '.join(selected_names)}.",
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f"Error refreshing logos: {str(e)}",
                messages.ERROR
            )
    refresh_logos.short_description = "🖼️ Refresh logos for selected tools"


class RatingAdmin(OptimizedQuerysetMixin, admin.ModelAdmin):
    # Display fields in list view
    list_display = ('get_user_info', 'get_tool_info', 'stars', 'comment', 'created_at')
    
    # Filtering and search
    list_filter = ('stars', 'created_at')
    search_fields = ('user__email', 'ai_tool__name', 'comment')
    
    # Read-only fields
    readonly_fields = ('id', 'created_at')
    
    # OptimizedQuerysetMixin configuration
    select_related_fields = ['user', 'ai_tool']
    
    # Field organization
    fieldsets = (
        ('Rating Information', {
            'fields': ('user', 'ai_tool', 'stars')
        }),
        ('Review', {
            'fields': ('comment',),
            'description': 'Optional text review'
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )

    @admin_display(description='User')
    def get_user_info(self, obj):
        """Display user ID and email"""
        return f"{obj.user.email} (ID: {obj.user.id})"

    @admin_display(description='AI Tool')
    def get_tool_info(self, obj):
        """Display tool name and ID"""
        return f"{obj.ai_tool.name} (ID: {obj.ai_tool.id})"

    
# Register models with our custom admin site
admin_site.register(AITool, AIToolAdmin)

# Also register with the default admin site for backward compatibility
admin.site.register(AITool, AIToolAdmin)
admin.site.register(Rating, RatingAdmin)

