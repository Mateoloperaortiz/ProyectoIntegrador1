"""
Core mixins for class-based views.

This module contains mixins that can be used across different apps
to provide common functionality to class-based views.
"""
from typing import Any, Dict, List, Optional, TypeVar, Union, cast
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.query import QuerySet
from django.http import HttpRequest


class PaginationMixin:
    """
    Mixin for handling pagination in list views.
    
    This mixin provides methods for paginating querysets and adding
    pagination context to templates.
    
    Attributes:
        paginate_by (int): Number of items per page
        page_kwarg (str): The name of the URL query parameter for the page number
    """
    paginate_by = 10
    page_kwarg = 'page'
    
    # These attributes are expected to be provided by the view that uses this mixin
    request: HttpRequest
    
    def get_queryset(self) -> QuerySet:
        # This method is expected to be implemented by the view that uses this mixin
        raise NotImplementedError("Subclasses must implement get_queryset()")
    
    def paginate_queryset(self, queryset: QuerySet, page_size: Optional[int] = None) -> tuple:
        """
        Paginate the queryset.
        
        Args:
            queryset: The queryset to paginate
            page_size (int, optional): Number of items per page. Defaults to self.paginate_by.
            
        Returns:
            tuple: (paginator, page, page_obj, is_paginated)
        """
        page_size = page_size or self.paginate_by
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get(self.page_kwarg, 1)
        
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
            
        is_paginated = paginator.num_pages > 1
        return (paginator, page, page.object_list, is_paginated)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add pagination context data.
        
        Returns:
            dict: Context data with pagination information
        """
        # Using Any for the parent class since we don't know what it is
        # This is a mixin that can be used with different view types
        context = super().get_context_data(**kwargs)  # type: ignore
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset)
        
        context.update({
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': is_paginated,
            'object_list': queryset
        })
        
        # Add pagination range for better navigation
        if is_paginated:
            # Calculate page range to display (show 5 pages around current page)
            current_page = page.number
            
            # Calculate page range to display (show 5 pages around current page)
            page_range_start = max(current_page - 2, 1)
            page_range_end = min(current_page + 2, paginator.num_pages)
            
            # Ensure we always show 5 pages if possible
            if page_range_end - page_range_start < 4 and paginator.num_pages > 4:
                if page_range_start == 1:
                    page_range_end = min(5, paginator.num_pages)
                elif page_range_end == paginator.num_pages:
                    page_range_start = max(paginator.num_pages - 4, 1)
                    
            context['page_range'] = range(page_range_start, page_range_end + 1)
            context['show_first'] = page_range_start > 1
            context['show_last'] = page_range_end < paginator.num_pages
            
        return context
        
    def get_pagination_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Separate method to add pagination context to an existing context dict.
        
        Args:
            context: Existing context dictionary
            
        Returns:
            The updated context with pagination data
        """
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset)
        
        context.update({
            'paginator': paginator,
            'page_obj': page,
            'is_paginated': is_paginated,
            'object_list': queryset
        })
        
        # Add pagination range for better navigation
        if is_paginated:
            # Calculate page range to display (show 5 pages around current page)
            current_page = page.number
            
            # Calculate page range to display (show 5 pages around current page)
            page_range_start = max(current_page - 2, 1)
            page_range_end = min(current_page + 2, paginator.num_pages)
            
            # Ensure we always show 5 pages if possible
            if page_range_end - page_range_start < 4 and paginator.num_pages > 4:
                if page_range_start == 1:
                    page_range_end = min(5, paginator.num_pages)
                elif page_range_end == paginator.num_pages:
                    page_range_start = max(paginator.num_pages - 4, 1)
                    
            context['page_range'] = range(page_range_start, page_range_end + 1)
            context['show_first'] = page_range_start > 1
            context['show_last'] = page_range_end < paginator.num_pages
            
        return context


class FilterMixin:
    """
    Mixin for handling filtering in list views.
    
    This mixin provides methods for filtering querysets based on
    request parameters and adding filter context to templates.
    """
    
    def get_filter_params(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Extract filter parameters from the request.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Dictionary of filter parameters
        """
        params = {}
        
        # Extract query parameters
        query = request.GET.get('q', '')
        if query:
            params['q'] = query
            
        # Extract category filters
        category = request.GET.get('category', '')
        if category:
            params['category'] = category
            
        # Extract sort parameters
        sort = request.GET.get('sort', '')
        if sort:
            params['sort'] = sort
            
        return params
    
    def apply_filters(self, queryset: QuerySet, params: Dict[str, Any]) -> QuerySet:
        """
        Apply filters to the queryset based on parameters.
        
        Args:
            queryset: The base queryset to filter
            params: Dictionary of filter parameters
            
        Returns:
            Filtered queryset
        """
        # This is a base implementation that should be overridden
        # by subclasses to provide specific filtering logic
        return queryset
    
    def get_filter_context(self, context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add filter context to the template context.
        
        Args:
            context: The existing context dictionary
            params: Dictionary of filter parameters
            
        Returns:
            The updated context dictionary with filter information
        """
        # Add filter parameters to context
        context.update(params)
        
        # Add query string for pagination links
        query_items = []
        for key, value in params.items():
            if key != 'page' and value:  # Exclude page from query string
                query_items.append(f"{key}={value}")
                
        context['query_string'] = '&'.join(query_items)
        
        return context


class UserFavoriteMixin:
    """
    Mixin for handling user favorites in views.
    
    This mixin provides methods for checking and adding user favorite
    information to the template context.
    """
    
    def get_user_favorites(self, user: Any) -> List[str]:
        """
        Get list of user's favorite item IDs.
        
        Args:
            user: The user object
            
        Returns:
            List of favorite item IDs as strings
        """
        if not user or not user.is_authenticated:
            return []
            
        # This is a base implementation that should be overridden
        # by subclasses to provide specific favorite retrieval logic
        return []
    
    def add_favorites_to_context(self, context: Dict[str, Any], user: Any) -> Dict[str, Any]:
        """
        Add user favorites information to the template context.
        
        Args:
            context: The existing context dictionary
            user: The user object
            
        Returns:
            The updated context dictionary with favorites information
        """
        if user and user.is_authenticated:
            context['user_favorites'] = self.get_user_favorites(user)
            
        return context
