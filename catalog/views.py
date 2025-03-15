from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from .models import AITool, Rating
from .forms import RatingForm, SearchForm
from .constants import CATEGORY_CHOICES
from interaction.models import Favorite


class HomeView(TemplateView):
    """
    View for the home page.
    """
    template_name = 'catalog/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_tools'] = AITool.objects.filter(is_featured=True)[:6]
        context['popular_tools'] = AITool.objects.all().order_by('-popularity')[:6]
        context['latest_tools'] = AITool.objects.all().order_by('-created_at')[:6]
        context['total_tools'] = AITool.objects.count()
        
        # Get the most popular categories based on tool count
        categories = []
        for code, name in CATEGORY_CHOICES:
            count = AITool.objects.filter(category=code).count()
            if count > 0:
                categories.append({
                    'code': code,
                    'name': name,
                    'count': count
                })
        categories.sort(key=lambda x: x['count'], reverse=True)
        context['categories'] = categories[:6]
        
        return context


class CatalogView(ListView):
    """
    View for the AI tool catalog.
    """
    model = AITool
    template_name = 'catalog/catalog.html'
    context_object_name = 'tools'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = AITool.objects.all()
        
        # Apply filtering based on category if provided
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', 'popularity')
        if sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('rating__stars')).order_by('-avg_rating')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == '-name':
            queryset = queryset.order_by('-name')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # Default to popularity
            queryset = queryset.order_by('-popularity')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort_by', 'popularity')
        
        return context


class ToolDetailView(DetailView):
    """
    View for the AI tool detail page.
    """
    model = AITool
    template_name = 'catalog/tool_detail.html'
    context_object_name = 'tool'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tool = self.get_object()
        
        # Increment the popularity counter
        tool.popularity += 1
        tool.save()
        
        # Check if the user has favorited this tool
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                tool=tool
            ).exists()
            
            # Check if user has already rated
            context['user_rating'] = Rating.objects.filter(
                user=self.request.user,
                tool=tool
            ).first()
        
        # Get related tools in the same category
        context['related_tools'] = AITool.objects.filter(
            category=tool.category
        ).exclude(id=tool.id).order_by('-popularity')[:4]
        
        # Get all ratings
        context['ratings'] = Rating.objects.filter(tool=tool).select_related('user')
        
        # Rating form
        context['rating_form'] = RatingForm()
        
        return context


class SearchView(ListView):
    """
    View for searching AI tools.
    """
    model = AITool
    template_name = 'catalog/search_results.html'
    context_object_name = 'tools'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = AITool.objects.all()
        form = SearchForm(self.request.GET)
        
        if form.is_valid():
            # Text search
            query = form.cleaned_data.get('q')
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(provider__icontains=query)
                )
            
            # Category filter
            categories = form.cleaned_data.get('category')
            if categories:
                queryset = queryset.filter(category__in=categories)
            
            # Sorting
            sort_by = form.cleaned_data.get('sort_by', 'popularity')
            if sort_by == 'rating':
                queryset = queryset.annotate(avg_rating=Avg('rating__stars')).order_by('-avg_rating')
            elif sort_by == 'name':
                queryset = queryset.order_by('name')
            elif sort_by == '-name':
                queryset = queryset.order_by('-name')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            else:  # Default to popularity
                queryset = queryset.order_by('-popularity')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm(self.request.GET)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class StatisticsView(TemplateView):
    """
    View for displaying statistics about AI tools.
    """
    template_name = 'catalog/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top rated tools
        top_tools = AITool.objects.annotate(
            avg_rating=Avg('rating__stars'),
            num_ratings=Count('rating')
        ).filter(num_ratings__gt=0).order_by('-avg_rating')[:10]
        
        context['top_tools'] = top_tools
        
        # Category distribution
        category_counts = []
        for code, name in CATEGORY_CHOICES:
            count = AITool.objects.filter(category=code).count()
            if count > 0:
                category_counts.append({
                    'name': name,
                    'count': count
                })
        
        context['category_counts'] = category_counts
        
        # Total stats
        context['total_tools'] = AITool.objects.count()
        context['total_ratings'] = Rating.objects.count()
        context['avg_tool_rating'] = Rating.objects.all().aggregate(Avg('stars'))['stars__avg'] or 0
        
        return context


@login_required
def rate_tool(request, slug):
    """
    View for rating an AI tool.
    """
    tool = get_object_or_404(AITool, slug=slug)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            # Check if user has already rated this tool
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                tool=tool,
                defaults={
                    'stars': form.cleaned_data['stars'],
                    'review': form.cleaned_data['review']
                }
            )
            
            # If rating already exists, update it
            if not created:
                rating.stars = form.cleaned_data['stars']
                rating.review = form.cleaned_data['review']
                rating.save()
                messages.success(request, _('Your rating has been updated!'))
            else:
                messages.success(request, _('Your rating has been submitted!'))
            
            return redirect('catalog:tool_detail', slug=slug)
    
    return redirect('catalog:tool_detail', slug=slug)
