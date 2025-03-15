"""
Service functions for the catalog app.

This module contains business logic for the catalog app, including filtering and sorting of AI tools.
"""
from typing import Any, Dict, List, Optional, Union
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.utils import timezone

from catalog.models import AITool


def filter_ai_tools(
    request: Optional[HttpRequest] = None,
    queryset: Optional[QuerySet] = None,
    search_query: str = '',
    category: str = '',
    pricing: str = '',
    sort_by: str = 'popularity'
) -> tuple[QuerySet, Dict[str, Any]]:
    """
    Filter and sort AI tools based on provided parameters.
    
    This function handles all the filtering and sorting logic for AI tools,
    and can be used by both class-based and function-based views.
    
    Args:
        request: Optional HTTP request object to extract parameters from
        queryset: Optional base queryset to filter (defaults to all AITools)
        search_query: Text to search in name, description, and provider
        category: Category to filter by
        pricing: Pricing filter ('free', 'paid', or empty for all)
        sort_by: Field to sort by ('name', 'popularity', 'newest')
        
    Returns:
        Tuple of (filtered queryset, context dict with filter parameters)
    """
    # Extract parameters from request if provided
    if request:
        search_query = request.GET.get('q', search_query)
        category = request.GET.get('category', category)
        pricing = request.GET.get('pricing', pricing)
        sort_by = request.GET.get('sort', sort_by)
    
    # Start with base queryset or all AI tools
    if queryset is None:
        queryset = AITool.objects.all()
    
    # Apply search filter
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(provider__icontains=search_query)
        )
        
    # Apply category filter
    if category:
        queryset = queryset.filter(category=category)
        
    # Apply pricing filter
    if pricing == 'free':
        queryset = queryset.filter(is_free=True)
    elif pricing == 'paid':
        queryset = queryset.filter(is_free=False)
        
    # Apply sorting
    if sort_by == 'name':
        queryset = queryset.order_by('name')
    elif sort_by == 'popularity':
        queryset = queryset.order_by('-popularity')
    elif sort_by == 'newest':
        # Since 'created_at' might not be available in the database yet,
        # catch any exception and fall back to popularity
        try:
            queryset = queryset.order_by('-created_at')
        except Exception:
            queryset = queryset.order_by('-popularity')
    
    # Get categories for filter dropdown
    categories = AITool.objects.values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]
    
    # Create context with filter parameters
    context = {
        'search_query': search_query,
        'selected_category': category,
        'selected_pricing': pricing,
        'sort_by': sort_by,
        'categories': categories
    }
    
    return queryset, context


def get_ai_models() -> QuerySet:
    """
    Get all AI tools with category 'Model'.
    
    Returns:
        QuerySet of AI models sorted by popularity
    """
    return AITool.objects.filter(category='Model').order_by('-popularity')