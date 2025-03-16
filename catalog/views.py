from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from .models import AITool, Rating
from .forms import RatingForm, SearchForm
from .constants import CATEGORY_CHOICES
from interaction.models import Favorite
import uuid

class HomeView(TemplateView):
    template_name = 'catalog/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured tools sorted by popularity
        featured_tools = AITool.objects.filter(is_featured=True).order_by('-popularity')[:6]
        
        # Popular tools sorted by popularity
        popular_tools = AITool.objects.all().order_by('-popularity')[:6]
        
        # Latest tools sorted by popularity and date
        latest_tools = AITool.objects.all().order_by('-popularity', '-created_at')[:6]
        
        context.update({
            'featured_tools': featured_tools,
            'popular_tools': popular_tools,
            'latest_tools': latest_tools,
            'total_tools': AITool.objects.count()
        })
        
        # Categories with counting
        categories = []
        for code, name in CATEGORY_CHOICES:
            count = AITool.objects.filter(category=code).count()
            if count > 0:
                categories.append({
                    'code': code,
                    'name': name,
                    'count': count
                })
        context['categories'] = sorted(categories, key=lambda x: x['count'], reverse=True)[:6]
        
        return context

class CatalogView(ListView):
    model = AITool
    template_name = 'catalog/catalog.html'
    context_object_name = 'tools'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = AITool.objects.annotate(avg_rating=Avg('ratings__stars'))
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        sort_by = self.request.GET.get('sort_by', 'popularity')
        if sort_by == 'rating':
            queryset = queryset.order_by('-avg_rating')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == '-name':
            queryset = queryset.order_by('-name')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # Default to popularity (which is now the average rating)
            queryset = queryset.order_by('-avg_rating')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort_by', 'popularity')
        return context

class ToolDetailView(DetailView):
    model = AITool
    template_name = 'catalog/tool_detail.html'
    context_object_name = 'tool'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return ratingAI(request, id=self.object.id)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return ratingAI(request, id=self.object.id)

def ratingAI(request: HttpRequest, id: uuid.UUID) -> HttpResponse:
    tool = get_object_or_404(
        AITool.objects.prefetch_related('ratings'), 
        id=id
    )
    
    related_tools = AITool.objects.filter(category=tool.category).exclude(id=tool.id)[:4]
    
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(
        user=request.user,
        tool=tool
    ).exists()

    if request.method == "POST" and request.user.is_authenticated:
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                user=request.user,
                tool=tool,
                defaults={
                    'stars': form.cleaned_data['stars'],
                    'comment': form.cleaned_data['comment']
                }
            )

            # Update AITool popularity
            avg_rating = tool.ratings.aggregate(Avg('stars'))['stars__avg']
            tool.popularity = round(avg_rating or 0, 1)
            tool.save(update_fields=['popularity'])
            
            messages.success(request, _('Your rating has been submitted!'))
            return redirect('catalog:tool_detail', slug=tool.slug)
        else:
            messages.error(request, _('Error saving rating.'))
    else:
        form = RatingForm()

    return render(request, 'catalog/tool_detail.html', {
        'tool': tool,
        'is_favorite': is_favorite,
        'related_tools': related_tools,
        'ratings': tool.ratings.select_related('user'),
        'average_rating': tool.popularity,
        'form': form
    })

class SearchView(ListView):
    model = AITool
    template_name = 'catalog/search_results.html'
    context_object_name = 'tools'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = AITool.objects.annotate(avg_rating=Avg('ratings__stars'))
        form = SearchForm(self.request.GET)
        
        if form.is_valid():
            query = form.cleaned_data.get('q')
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(provider__icontains=query)
                )
            
            categories = form.cleaned_data.get('category')
            if categories:
                queryset = queryset.filter(category__in=categories)
            
            sort_by = form.cleaned_data.get('sort_by', 'popularity')
            if sort_by == 'rating':
                queryset = queryset.order_by('-avg_rating')
            elif sort_by == 'name':
                queryset = queryset.order_by('name')
            elif sort_by == '-name':
                queryset = queryset.order_by('-name')
            elif sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            else:  # Default to popularity (average rating)
                queryset = queryset.order_by('-avg_rating')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm(self.request.GET)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class StatisticsView(TemplateView):
    template_name = 'catalog/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        top_tools = AITool.objects.annotate(
            avg_rating=Avg('ratings__stars'),
            num_ratings=Count('ratings')
        ).filter(num_ratings__gt=0).order_by('-avg_rating')[:10]
        
        context['top_tools'] = top_tools
        
        category_counts = []
        for code, name in CATEGORY_CHOICES:
            count = AITool.objects.filter(category=code).count()
            if count > 0:
                category_counts.append({
                    'name': name,
                    'count': count
                })
        
        context['category_counts'] = category_counts
        context['total_tools'] = AITool.objects.count()
        context['total_ratings'] = Rating.objects.count()
        context['avg_tool_rating'] = Rating.objects.aggregate(Avg('stars'))['stars__avg'] or 0
        
        return context