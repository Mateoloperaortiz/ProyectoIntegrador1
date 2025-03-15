"""
Catalog views for the catalog app.

This module contains views related to browsing and filtering the catalog of AI tools.
"""
from typing import Any, Dict, List, Optional
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView

from catalog.models import AITool
from catalog.services import filter_ai_tools, get_ai_models
from core.mixins import PaginationMixin, FilterMixin


class CatalogView(PaginationMixin, FilterMixin, ListView):
    """
    View for displaying the catalog of AI tools with filtering and pagination.
    
    This view renders a list of AI tools with various filtering options and pagination.
    Using the OpenRouter-inspired template for a modern card-based layout.
    """
    model = AITool
    template_name = 'catalog/catalog.html'
    context_object_name = 'ai_tools'
    paginate_by = 12
    
    def get_queryset(self) -> Any:
        """
        Get the queryset with applied filters.
        
        Returns:
            Filtered queryset of AI tools
        """
        queryset = super().get_queryset()
        filtered_queryset, _ = filter_ai_tools(request=self.request, queryset=queryset)
        return filtered_queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get the context data for the template.
        
        Args:
            **kwargs: Additional keyword arguments
            
        Returns:
            Context data dictionary
        """
        context = super().get_context_data(**kwargs)
        
        # Get filter context
        _, filter_context = filter_ai_tools(request=self.request)
        context.update(filter_context)
        
        # Add pagination context
        context = self.get_pagination_context(context)
        
        return context


def catalog_view(request: HttpRequest) -> HttpResponse:
    """
    Function-based view for the catalog page.
    
    This is a simpler alternative to the class-based CatalogView.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered catalog page
    """
    # Use the shared service function to filter AI tools
    queryset, context = filter_ai_tools(request=request)
    
    # Add AI tools to the context
    context['ai_tools'] = queryset
    
    return render(request, 'catalog/catalog.html', context)


class ModelsView(PaginationMixin, ListView):
    """
    View for displaying AI models with pagination.
    
    This view renders a list of AI models, which are a subset of AI tools.
    """
    model = AITool
    template_name = 'catalog/models.html'
    context_object_name = 'ai_models'
    paginate_by = 12
    
    def get_queryset(self) -> Any:
        """
        Get the queryset of AI models.
        
        Returns:
            Filtered queryset of AI models
        """
        # Use the shared service function to get AI models
        return get_ai_models()
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get the context data for the template.
        
        Args:
            **kwargs: Additional keyword arguments
            
        Returns:
            Context data dictionary
        """
        context = super().get_context_data(**kwargs)
        
        # Add pagination context
        context = self.get_pagination_context(context)
        
        return context


def models_view(request: HttpRequest) -> HttpResponse:
    """
    Function-based view for the models page.
    
    This is a simpler alternative to the class-based ModelsView.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered models page
    """
    # Use the shared service function to get AI models
    ai_models = get_ai_models()
    
    return render(request, 'catalog/models.html', {
        'ai_models': ai_models
    })