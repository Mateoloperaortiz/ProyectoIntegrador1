"""
AI Tools views for the catalog app.

This module contains views related to AI tool details and comparisons.
"""
import uuid
from typing import Any, Dict, List, Optional
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import DetailView

from catalog.models import AITool,Rating
from catalog.forms import RatingForm
from django.contrib import messages
from django.urls import reverse

# Using CustomUser.favorites directly


class AIToolDetailView(DetailView):
    """
    View for displaying the details of an AI tool.
    
    This view renders a detailed page for a specific AI tool.
    """
    model = AITool
    template_name = 'catalog/ai_tool_detail.html'
    context_object_name = 'ai_tool'
    pk_url_kwarg = 'id'  # Match the URL pattern parameter name
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Get the context data for the template.
        
        Args:
            **kwargs: Additional keyword arguments
            
        Returns:
            Context data dictionary
        """
        context = super().get_context_data(**kwargs)
        
        # Check if the user has favorited this AI tool
        if self.request.user.is_authenticated:
            context['is_favorite'] = self.request.user.favorites.filter(id=self.object.id).exists()
        else:
            context['is_favorite'] = False
        
        # Get related AI tools in the same category
        context['related_tools'] = AITool.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        
        return context


# Make a rating with stars and reviews.  
def presentationAI(request: HttpRequest, id: uuid.UUID) -> HttpResponse:
    """View for displaying a presentation-style page for an AI tool."""
    
    # Get AI tool with prefetched ratings
    ai_tool = get_object_or_404(
        AITool.objects.prefetch_related('ratings'), 
        id=id
    )
    
    # Get related tools
    related_tools = AITool.objects.filter(category=ai_tool.category).exclude(id=ai_tool.id)[:4]
    
    # Check if the user has it in favorites
    is_favorite = request.user.is_authenticated and request.user.favorites.filter(id=ai_tool.id).exists()

    # Manage rating submission
    if request.method == "POST" and request.user.is_authenticated:
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                user=request.user,
                ai_tool=ai_tool,
                defaults={
                    'stars': form.cleaned_data['stars'],
                    'comment': form.cleaned_data['comment']
                }
            )
            messages.success(request, '¡Rating saved successfully!')
            return redirect('catalog:presentationAI', id=id)
        else:
            messages.error(request, 'Error saving rating.')
    else:
        form = RatingForm()

    # Prepare context with all necessary data
    return render(request, 'catalog/PresentationAI.html', {
        'ai_tool': ai_tool,
        'is_favorite': is_favorite,
        'related_tools': related_tools,
        'ratings': ai_tool.ratings.select_related('user'),
        'average_rating': ai_tool.popularity,  # Using popularity field directly
        'popularity': ai_tool.popularity,  # For consistency
        'form': form
    })




def compare_tools(request: HttpRequest) -> HttpResponse:
    """
    View for comparing multiple AI tools.
    
    This view renders a comparison page for multiple AI tools,
    allowing users to compare features and capabilities.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered comparison page
    """
    # Get all AI tools for selection
    all_tools = AITool.objects.all().order_by('category', 'name')
    
    # Get the tool IDs from the request - supports both tool_id[] and tool1, tool2, etc.
    tool_ids = request.GET.getlist('tool_id')
    
    # Also check for tool1, tool2, etc. parameters
    tool1 = None
    tool2 = None
    
    for key, value in request.GET.items():
        if key == 'tool1':
            try:
                tool1_id = uuid.UUID(value)
                tool1 = AITool.objects.filter(id=tool1_id).first()
            except (ValueError, AttributeError):
                pass
        elif key == 'tool2':
            try:
                tool2_id = uuid.UUID(value)
                tool2 = AITool.objects.filter(id=tool2_id).first()
            except (ValueError, AttributeError):
                pass
        elif key.startswith('tool') and key != 'tool_id':
            try:
                # Try to convert to UUID to validate it's a proper tool ID
                uuid.UUID(value)
                tool_ids.append(value)
            except (ValueError, AttributeError):
                pass
    
    # Get the AI tools for comparison from tool_id parameters
    tools = []
    if tool_ids:
        tools = AITool.objects.filter(id__in=tool_ids)
    
    # If we have specific tool1/tool2 parameters, use those for comparison
    if tool1 or tool2:
        selected_tools = [t for t in [tool1, tool2] if t is not None]
        if selected_tools:
            tools = selected_tools
    
    # If no tools are selected, show a selection page
    if not tools:
        return render(request, 'catalog/compare_select.html', {
            'all_tools': all_tools
        })
    
    # Organize features for comparison
    features = [
        'name', 'provider', 'category', 'popularity', 'api_type',
        'api_model', 'is_featured'
    ]
    
    # Create a comparison table
    comparison = {}
    for feature in features:
        # Use a try-except block to handle missing attributes gracefully
        feature_values = []
        for tool in tools:
            try:
                feature_values.append(getattr(tool, feature))
            except AttributeError:
                # If the attribute doesn't exist, use a placeholder value
                feature_values.append('N/A')
        comparison[feature] = feature_values
    
    return render(request, 'catalog/compare.html', {
        'tools': tools,
        'tool1': tool1,
        'tool2': tool2,
        'all_tools': all_tools,
        'features': features,
        'comparison': comparison
    })
