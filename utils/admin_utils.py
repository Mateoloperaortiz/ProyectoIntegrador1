"""
Utility functions and mixins for Django admin classes with proper type annotations.

This module provides type-safe wrappers around Django admin decorators and utilities
to ensure proper type checking while maintaining Django admin functionality.

Example:
    ```python
    from utils.admin_utils import admin_display, OptimizedQuerysetMixin
    
    class MyModelAdmin(OptimizedQuerysetMixin, admin.ModelAdmin):
        @admin_display(description="User's full name", ordering="last_name")
        def get_full_name(self, obj):
            return f"{obj.first_name} {obj.last_name}"
    ```
"""
import csv
import datetime
import json
from typing import Any, Callable, Dict, List, Optional, TypeVar, Type, cast, Set, Union, Tuple
from django.contrib import admin, messages
from django.db.models import Model, QuerySet
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html

F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T', bound=Model)

def admin_display(
    description: Optional[str] = None,
    boolean: Optional[bool] = None,
    ordering: Optional[str] = None,
    admin_order_field: Optional[str] = None,
    allow_tags: Optional[bool] = None,
    empty_value_display: Optional[str] = None,
) -> Callable[[F], F]:
    """
    A type-aware version of Django's admin display decorator.
    This helps mypy understand that admin display attributes are valid.
    
    Args:
        description: Short description for the admin
        boolean: Whether to display as a boolean
        ordering: Field to use for ordering
        admin_order_field: Field to use for ordering (alias for ordering)
        allow_tags: Whether to allow HTML tags
        empty_value_display: What to display when empty
        
    Returns:
        A decorator that preserves the function's type
    """
    def decorator(func: F) -> F:
        if description is not None:
            func.short_description = description  # type: ignore
        if boolean is not None:
            func.boolean = boolean  # type: ignore
        if ordering is not None:
            func.admin_order_field = ordering  # type: ignore
        if admin_order_field is not None:
            func.admin_order_field = admin_order_field  # type: ignore
        if allow_tags is not None:
            func.allow_tags = allow_tags  # type: ignore
        if empty_value_display is not None:
            func.empty_value_display = empty_value_display  # type: ignore
        return func
    return decorator

class OptimizedQuerysetMixin:
    """
    Mixin to optimize admin querysets with select_related and prefetch_related.
    
    Usage:
        class MyModelAdmin(OptimizedQuerysetMixin, admin.ModelAdmin):
            select_related_fields = ['foreign_key1', 'foreign_key2']
            prefetch_related_fields = ['many_to_many1', 'many_to_many2']
    """
    select_related_fields: List[str] = []
    prefetch_related_fields: List[str] = []
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Optimize query by using select_related and prefetch_related."""
        queryset = super().get_queryset(request)
        
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
            
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
            
        return queryset

class ContentPreviewMixin:
    """
    Mixin to handle content preview for text fields.
    
    Usage:
        class MyModelAdmin(ContentPreviewMixin, admin.ModelAdmin):
            preview_fields = {
                'content_preview': {'field': 'content', 'max_length': 50},
                'title_preview': {'field': 'title', 'max_length': 30}
            }
    """
    preview_fields: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_preview_methods()
    
    def _add_preview_methods(self):
        """Dynamically add preview methods for fields defined in preview_fields."""
        for method_name, config in self.preview_fields.items():
            field_name = config['field']
            max_length = config.get('max_length', 50)
            description = config.get('description', f'{field_name.replace("_", " ").title()} Preview')
            
            def create_preview_method(field, length):
                def preview_method(self, obj):
                    value = getattr(obj, field, '')
                    if isinstance(value, str) and len(value) > length:
                        return value[:length] + '...'
                    return value
                return preview_method
            
            preview_method = create_preview_method(field_name, max_length)
            setattr(self.__class__, method_name, preview_method)
            
            # Add short_description to the method
            method = getattr(self.__class__, method_name)
            method.short_description = description  # type: ignore

class AdminActionMessageMixin:
    """
    Mixin to provide standardized admin action messages.
    
    Usage:
        class MyModelAdmin(AdminActionMessageMixin, admin.ModelAdmin):
            pass
            
        def my_action(self, request, queryset):
            count = queryset.update(active=True)
            self.message_action_result(request, count, "activated")
    """
    
    def message_action_result(self, request: HttpRequest, count: int, action_description: str) -> None:
        """Display a standardized message for an admin action result."""
        item_description = self.model._meta.verbose_name if count == 1 else self.model._meta.verbose_name_plural
        self.message_user(
            request,
            f"{count} {item_description} {action_description} successfully.",
            messages.SUCCESS
        )
    
    def message_custom_result(self, request: HttpRequest, count: int, action_description: str, 
                              singular_name: str, plural_name: str) -> None:
        """Display a custom message for an admin action result with specified names."""
        item_description = singular_name if count == 1 else plural_name
        self.message_user(
            request,
            f"{count} {item_description} {action_description} successfully.",
            messages.SUCCESS
        )

class ExportModelMixin:
    """
    Mixin to provide export functionality for admin models.
    
    Usage:
        class MyModelAdmin(ExportModelMixin, admin.ModelAdmin):
            export_fields = ['id', 'name', 'created_at']
            export_headers = ['ID', 'Name', 'Creation Date']
            export_filename = 'my_model_export'
    """
    export_fields: List[str] = []
    export_headers: List[str] = []
    export_filename: str = 'export'
    export_formats: List[str] = ['csv']  # supported: 'csv', 'json'
    
    def export_as_csv(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        """Export selected objects as CSV."""
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.export_filename}_{timestamp}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Use export_headers if defined, otherwise use export_fields
        headers = self.export_headers if self.export_headers else self.export_fields
        writer.writerow(headers)
        
        # Write data rows
        for obj in queryset:
            row = []
            for field in self.export_fields:
                # Handle nested field access with double underscores
                if '__' in field:
                    parts = field.split('__')
                    value = obj
                    for part in parts:
                        if value is None:
                            break
                        value = getattr(value, part, None)
                else:
                    value = getattr(obj, field, None)
                
                # Format dates and boolean values
                if isinstance(value, datetime.datetime):
                    value = value.isoformat()
                elif isinstance(value, bool):
                    value = 'Yes' if value else 'No'
                elif hasattr(value, 'all') and callable(value.all):
                    # Handle M2M relationships
                    try:
                        value = ', '.join(str(v) for v in value.all())
                    except:
                        value = str(value)
                
                row.append(value)
            writer.writerow(row)
        
        count = queryset.count()
        model_name = self.model._meta.verbose_name if count == 1 else self.model._meta.verbose_name_plural
        self.message_user(
            request,
            f"Exported {count} {model_name} to CSV.",
            messages.SUCCESS
        )
        return response
    export_as_csv.short_description = "📄 Export selected items to CSV"  # type: ignore
    
    def export_as_json(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        """Export selected objects as JSON."""
        response = HttpResponse(content_type='application/json')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.export_filename}_{timestamp}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        data = []
        for obj in queryset:
            item = {}
            for field in self.export_fields:
                # Handle nested field access with double underscores
                if '__' in field:
                    parts = field.split('__')
                    value = obj
                    for part in parts:
                        if value is None:
                            break
                        value = getattr(value, part, None)
                else:
                    value = getattr(obj, field, None)
                
                # Format values for JSON serialization
                if isinstance(value, datetime.datetime):
                    value = value.isoformat()
                elif hasattr(value, 'all') and callable(value.all):
                    # Handle M2M relationships
                    try:
                        value = [str(v) for v in value.all()]
                    except:
                        value = str(value)
                elif isinstance(value, Model):
                    # For FK relationships, use string representation
                    value = str(value)
                
                # Use field name as the key in the JSON
                item[field] = value
            data.append(item)
        
        json_data = json.dumps(data, indent=2)
        response.write(json_data)
        
        count = queryset.count()
        model_name = self.model._meta.verbose_name if count == 1 else self.model._meta.verbose_name_plural
        self.message_user(
            request,
            f"Exported {count} {model_name} to JSON.",
            messages.SUCCESS
        )
        return response
    export_as_json.short_description = "📤 Export selected items to JSON"  # type: ignore
    
    def get_actions(self, request: HttpRequest) -> Dict[str, Any]:
        """Add export actions to the admin based on export_formats."""
        actions = super().get_actions(request)
        
        if hasattr(self, 'export_fields') and self.export_fields:
            if 'csv' in self.export_formats:
                actions['export_as_csv'] = (self.export_as_csv, 'export_as_csv', self.export_as_csv.short_description)
            if 'json' in self.export_formats:
                actions['export_as_json'] = (self.export_as_json, 'export_as_json', self.export_as_json.short_description)
                
        return actions

class DuplicateModelMixin:
    """
    Mixin to provide model duplication functionality for admin.
    
    Usage:
        class MyModelAdmin(DuplicateModelMixin, admin.ModelAdmin):
            # Fields to exclude from duplication (e.g., unique fields)
            duplicate_exclude_fields = ['slug', 'unique_id']
            
            # Fields to reset to default values when duplicating
            duplicate_reset_fields = {
                'is_active': False,
                'views_count': 0,
            }
            
            # Prefix for duplicated object name (if applicable)
            duplicate_name_prefix = "Copy of"
            
            # Field to use as the name for the "Copy of" prefix
            duplicate_name_field = "title"
    """
    duplicate_exclude_fields: List[str] = []
    duplicate_reset_fields: Dict[str, Any] = {}
    duplicate_name_prefix: str = "Copy of"
    duplicate_name_field: str = "name"
    duplicate_file_fields: List[str] = []  # Fields containing files that need special handling
    
    def duplicate_objects(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Duplicate selected objects."""
        count = 0
        model_class = self.model
        
        for obj in queryset:
            # Get all field values from the original object
            field_values = {}
            
            for field in model_class._meta.fields:
                field_name = field.name
                
                # Skip primary key and fields in exclude list
                if field.primary_key or field_name in self.duplicate_exclude_fields:
                    continue
                
                # Check if this field should be reset to a default value
                if field_name in self.duplicate_reset_fields:
                    field_values[field_name] = self.duplicate_reset_fields[field_name]
                    continue
                
                # Handle name/title field with prefix
                if field_name == self.duplicate_name_field:
                    original_name = getattr(obj, field_name)
                    field_values[field_name] = f"{self.duplicate_name_prefix} {original_name}"
                    continue
                
                # Get the value from the original object
                value = getattr(obj, field_name)
                
                # Skip file fields for initial creation
                if field_name in self.duplicate_file_fields:
                    continue
                
                field_values[field_name] = value
            
            # Create the duplicate object
            duplicate = model_class(**field_values)
            duplicate.save()
            
            # Handle file fields separately after the object is created
            for file_field in self.duplicate_file_fields:
                original_file = getattr(obj, file_field)
                if original_file:
                    setattr(duplicate, file_field, original_file)
            
            # Save again if we had file fields
            if self.duplicate_file_fields:
                duplicate.save()
                
            # Handle many-to-many relationships
            for m2m_field in model_class._meta.many_to_many:
                field_name = m2m_field.name
                if field_name not in self.duplicate_exclude_fields:
                    source = getattr(obj, field_name)
                    destination = getattr(duplicate, field_name)
                    
                    # Add all related objects
                    for related_obj in source.all():
                        destination.add(related_obj)
            
            count += 1
            
        model_name = model_class._meta.verbose_name if count == 1 else model_class._meta.verbose_name_plural
        self.message_user(
            request,
            f"Successfully duplicated {count} {model_name}.",
            messages.SUCCESS
        )
    duplicate_objects.short_description = "🔄 Duplicate selected objects"  # type: ignore
