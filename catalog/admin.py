from django.contrib import admin
from django.utils.html import format_html
from .models import AITool


@admin.register(AITool)
class AIToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'category', 'popularity_display', 'created_at', 'updated_at')
    list_filter = ('category', 'provider', 'created_at')
    search_fields = ('name', 'provider', 'description')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'provider', 'category')
        }),
        ('Details', {
            'fields': ('description', 'endpoint', 'popularity')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def popularity_display(self, obj):
        """Display popularity as a colored bar based on the value."""
        # Define color based on popularity
        if obj.popularity >= 80:
            color = 'green'
        elif obj.popularity >= 50:
            color = 'orange'
        else:
            color = 'red'
            
        return format_html(
            '<div style="width:100px; height:10px; background-color:#f0f0f0;">'
            '<div style="width:{}px; height:10px; background-color:{};">&nbsp;</div>'
            '</div> {}%',
            obj.popularity, color, obj.popularity
        )
    
    popularity_display.short_description = 'Popularity'
    
    def image_preview(self, obj):
        """Display a preview of the image in the admin."""
        if obj.image:
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No image available"
    
    image_preview.short_description = 'Image Preview'
