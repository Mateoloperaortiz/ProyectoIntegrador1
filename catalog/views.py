from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.urls import reverse

from .models import AITool

# Constants
ITEMS_PER_PAGE = 9  # Number of AI tools per page
SEARCH_FIELDS = ['name', 'description', 'provider']  # Fields that will be searched

class HomeView(TemplateView):
    """
    Display the home page.
    """
    template_name = 'catalog/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.get_categories()
        # Add featured tools - using the most popular ones
        context['featured_tools'] = AITool.objects.order_by('-popularity')[:3]
        return context
    
    def get_categories(self):
        """
        Return all unique categories from the database.
        """
        return [choice[0] for choice in AITool.Category.choices]


class AIToolDetailView(DetailView):
    """
    Display detailed information about a specific AI tool.
    """
    model = AITool
    template_name = 'catalog/presentationAI.html'  # Will be renamed in future
    context_object_name = 'ai_tool'
    
    def get_object(self):
        """
        Get the object based on either pk or id for backward compatibility
        """
        if 'pk' in self.kwargs:
            return get_object_or_404(AITool, pk=self.kwargs['pk'])
        elif 'id' in self.kwargs:
            return get_object_or_404(AITool, id=self.kwargs['id'])
        else:
            raise Http404("AI Tool not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related AI tools in the same category
        related_tools = AITool.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        context['related_tools'] = related_tools
        return context


class CatalogView(ListView):
    """
    Display a list of AI tools with filtering, sorting, and pagination.
    """
    model = AITool
    template_name = 'catalog/catalog.html'
    context_object_name = 'ai_tools'
    paginate_by = ITEMS_PER_PAGE
    
    def get_queryset(self):
        """
        Return the filtered and sorted queryset based on parameters.
        """
        queryset = AITool.objects.all()
        
        # Filter by category
        category = self.kwargs.get('category') or self.request.GET.get('category')
        if category and category in self.get_categories():
            queryset = queryset.filter(category=category)
        
        # Search functionality (supporting both old and new parameter names)
        search_term = self.request.GET.get('search', '') or self.request.GET.get('searchAITool', '')
        if search_term:
            # Create a Q object for each search field
            search_query = Q()
            for field in SEARCH_FIELDS:
                search_query |= Q(**{f"{field}__icontains": search_term})
            queryset = queryset.filter(search_query)
        
        # Sorting
        sort_by = self.request.GET.get('sort_by', '-popularity')
        valid_sort_fields = ['name', '-name', 'popularity', '-popularity', 'provider', '-provider', 
                             'created_at', '-created_at', 'updated_at', '-updated_at']
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-popularity', 'name')  # Default sorting
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data for the template.
        """
        context = super().get_context_data(**kwargs)
        
        # Add search and filter parameters to context
        context['categories'] = self.get_categories()
        
        # Support for both old and new parameter names for backward compatibility
        search_term = self.request.GET.get('search', '') or self.request.GET.get('searchAITool', '')
        context['searchTerm'] = search_term
        
        # Get category from URL kwargs or query parameters
        category = self.kwargs.get('category') or self.request.GET.get('category', '')
        context['current_category'] = category
        
        context['current_sort'] = self.request.GET.get('sort_by', '-popularity')
        
        # Add pagination parameters
        if context['is_paginated']:
            paginator = context['paginator']
            page_obj = context['page_obj']
            
            # Create page range for pagination display
            page_range = self.get_page_range(paginator, page_obj)
            context['page_range'] = page_range
        
        return context
    
    @staticmethod
    def get_categories():
        """
        Return all unique categories from the database or use predefined list.
        """
        return [choice[0] for choice in AITool.Category.choices]
    
    @staticmethod
    def get_page_range(paginator, page_obj, adjacent_pages=2):
        """
        Generate a list of page numbers to show in the pagination controls.
        """
        page_number = page_obj.number
        total_pages = paginator.num_pages
        
        # Create a range of page numbers to display
        start_page = max(page_number - adjacent_pages, 1)
        end_page = min(page_number + adjacent_pages + 1, total_pages + 1)
        
        page_range = range(start_page, end_page)
        
        # Add first and last page indicators if needed
        if start_page > 1:
            page_range = [1, '...'] + list(page_range)
        if end_page <= total_pages:
            page_range = list(page_range) + ['...', total_pages]
            
        return page_range


# Function-based view alternatives (for reference and backward compatibility)
def home(request):
    """Legacy function-based home view for backward compatibility."""
    return HomeView.as_view()(request)


def presentationAI(request, id):
    """Legacy function-based detail view for backward compatibility."""
    view = AIToolDetailView.as_view()
    return view(request, id=id)


def catalog_view(request):
    """Legacy function-based catalog view for backward compatibility."""
    return CatalogView.as_view()(request)
