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
import posthog # Import PostHog
from django.conf import settings # Import Django settings


@login_required
def toggle_favorite(request, tool_id):
    """
    Toggle favorite status for an AI tool.
    """
    tool = get_object_or_404(AITool, id=tool_id)
    
    # Check if already favorited
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        tool=tool
    )
    
    # If not created, it already exists, so delete it
    if not created:
        favorite.delete()
        is_favorite = False
        message = _('Removed from favorites')
    else:
        is_favorite = True
        message = _('Added to favorites')
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': is_favorite,
            'message': message
        })
    
    # If regular request, redirect back
    messages.success(request, message)
    return redirect('catalog:tool_detail', slug=tool.slug)


def get_recommended_tools(user, current_tool=None, limit=4):
    if not user.is_authenticated:
        return AITool.objects.none()

    # Obtener categorías de herramientas favoritas del usuario
    favorite_tools = Favorite.objects.filter(user=user).values_list('tool__category', flat=True)
    if not favorite_tools:
        return AITool.objects.none()

    # Seleccionar herramientas relacionadas por categoría
    recommended = AITool.objects.annotate(avg_rating=Avg('ratings__stars')).filter(
        category__in=favorite_tools
    ).exclude(
        id__in=Favorite.objects.filter(user=user).values_list('tool__id', flat=True)
    )

    if current_tool:
        recommended = recommended.exclude(id=current_tool.id)

    # Ordenar por calificación promedio y retornar solo `limit`
    return recommended.order_by('-avg_rating')[:limit]


class HomeView(TemplateView):
    template_name = 'catalog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        featured_tools = AITool.objects.filter(is_featured=True).order_by('-popularity')[:6]
        popular_tools = AITool.objects.all().order_by('-popularity')[:6]
        latest_tools = AITool.objects.all().order_by('-popularity', '-created_at')[:6]

        context.update({
            'featured_tools': featured_tools,
            'popular_tools': popular_tools,
            'latest_tools': latest_tools,
            'total_tools': AITool.objects.count()
        })

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
        else:
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
        tool_id = getattr(self.object, 'id', None)
        if tool_id is not None:
            return ratingAI(request, id=tool_id)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        tool_id = getattr(self.object, 'id', None)
        if tool_id is not None:
            return ratingAI(request, id=tool_id)
        slug = getattr(self.object, 'slug', None)
        if slug is not None:
            return redirect('catalog:tool_detail', slug=slug)
        return redirect('catalog:catalog')


def ratingAI(request: HttpRequest, id: uuid.UUID) -> HttpResponse:
    tool = get_object_or_404(
        AITool.objects.prefetch_related('ratings'),
        id=id
    )

    # PostHog: Capture ai_tool_viewed event
    if settings.POSTHOG_API_KEY and request.method == "GET": # Capture only on initial GET request
        distinct_id = None
        if request.user.is_authenticated:
            distinct_id = request.user.email # Or request.user.id, ensure consistency
        # else:
            # For anonymous users, you might use a session ID or let the frontend snippet handle it.
            # For simplicity, we'll only capture for authenticated users here, or if you have
            # a robust way to get a distinct_id for anonymous users.
            # distinct_id = request.session.session_key # Example for anonymous

        if distinct_id: # Only capture if we have a distinct_id
            posthog.capture(
                distinct_id,
                'ai_tool_viewed',
                properties={
                    'tool_id': str(tool.id), # Ensure ID is a string if it's UUID
                    'tool_name': tool.name,
                    'tool_slug': tool.slug,
                    'category': tool.category, # Assuming category is a simple field or has a __str__
                    '$current_url': request.build_absolute_uri()
                }
            )

    is_favorite = request.user.is_authenticated and Favorite.objects.filter(
        user=request.user,
        tool=tool
    ).exists()

    recommended_tools = get_recommended_tools(request.user, current_tool=tool)

    if request.method == "POST" and request.user.is_authenticated:
        form = RatingForm(request.POST)
        if form.is_valid():
            try:
                rating, created = Rating.objects.update_or_create(
                    user=request.user,
                    tool=tool,
                    defaults={
                        'stars': form.cleaned_data['stars'],
                        'comment': form.cleaned_data['comment']
                    }
                )
                avg_rating = Rating.objects.filter(tool=tool).aggregate(Avg('stars'))['stars__avg']
                tool.popularity = round(avg_rating or 0, 1)
                tool.save(update_fields=['popularity'])

                # PostHog: Capture ai_tool_rated event
                if settings.POSTHOG_API_KEY:
                    posthog.capture(
                        request.user.email, # Distinct ID
                        'ai_tool_rated',
                        properties={
                            'tool_id': str(tool.id),
                            'tool_name': tool.name,
                            'rating_score': rating.stars, # Or form.cleaned_data['stars']
                            'comment_length': len(rating.comment) if rating.comment else 0,
                            'was_new_rating': created # Boolean: True if new, False if updated
                        }
                    )

                messages.success(request, _('Your rating has been saved successfully!'))
                return redirect('catalog:tool_detail', slug=tool.slug)
            except Exception as e:
                messages.error(request, _('An error occurred while saving your rating.'))
                print(f"Error saving rating: {str(e)}")  # Para debugging
        else:
            messages.error(request, _('Please check your rating form.'))
            print(f"Form errors: {form.errors}")  # Para debugging
    else:
        # Obtener la calificación existente del usuario si existe
        if request.user.is_authenticated:
            existing_rating = Rating.objects.filter(user=request.user, tool=tool).first()
            form = RatingForm(instance=existing_rating) if existing_rating else RatingForm()
        else:
            form = RatingForm()

    ratings = Rating.objects.filter(tool=tool).select_related('user').order_by('-created_at')
    
    context = {
        'tool': tool,
        'is_favorite': is_favorite,
        'recommended_tools': recommended_tools,
        'ratings': ratings,
        'average_rating': tool.popularity,
        'form': form
    }

    return render(request, 'catalog/tool_detail.html', context)


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
            else:
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
            tools_in_category = AITool.objects.filter(category=code)
            count = tools_in_category.count()
            if count > 0:
                # Get total ratings for tools in this category
                total_ratings = Rating.objects.filter(
                    tool__category=code
                ).aggregate(
                    total_count=Count('id'),
                    avg_rating=Avg('stars')
                )
                
                category_counts.append({
                    'name': name,
                    'count': count,
                    'total_ratings': total_ratings['total_count'] or 0,
                    'avg_rating': round(total_ratings['avg_rating'] or 0, 1)
                })

        context['category_counts'] = category_counts
        context['total_tools'] = AITool.objects.count()
        context['total_ratings'] = Rating.objects.count()
        context['avg_tool_rating'] = Rating.objects.aggregate(Avg('stars'))['stars__avg'] or 0

        return context
