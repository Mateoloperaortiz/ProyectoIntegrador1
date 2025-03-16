from django.contrib import admin
from .models import AITool, Rating

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ('id', 'user', 'stars', 'comment', 'created_at')
    can_delete = False
    max_num = 0  # Don't allow adding new inline ratings from admin

@admin.register(AITool)
class AIToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'category', 'popularity', 'is_featured', 'api_type', 'created_at')
    list_filter = ('category', 'api_type', 'is_featured')
    search_fields = ('name', 'description', 'provider')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RatingInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'provider', 'website_url', 'category', 'image')
        }),
        ('Status', {
            'fields': ('is_featured', 'popularity', 'created_at', 'updated_at')
        }),
        ('API Integration', {
            'fields': ('api_type', 'api_endpoint', 'api_model'),
            'classes': ('collapse',),
        }),
    )

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tool', 'stars', 'created_at')
    list_filter = ('stars', 'created_at', 'tool')
    search_fields = ('user__username', 'user__email', 'tool__name', 'comment')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Rating Information', {
            'fields': ('id', 'user', 'tool', 'stars')
        }),
        ('Additional Information', {
            'fields': ('comment', 'created_at')
        }),
    )
