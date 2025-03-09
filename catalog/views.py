from .models import AITool, UserFavorite, Conversation, Message
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import time
from . import utils

User = get_user_model()


def home(request):
    """Render the home page with a showcase of top AI tools."""
    # Get 3 most popular AIs to showcase
    popular_ais = AITool.objects.all().order_by('-popularity')[:3]
    return render(request, 'catalog/home.html', {
        'popular_ais': popular_ais
    })


def presentationAI(request, id):
    """Display detailed information about a specific AI tool."""
    ai_tool = get_object_or_404(AITool, id=id)
    
    # Get related AIs in the same category (limited to 3)
    related_ais = AITool.objects.filter(
        category=ai_tool.category
    ).exclude(id=id).order_by('-popularity')[:3]
    
    return render(request, 'catalog/presentationAI.html', {
        'ai_tool': ai_tool,
        'related_ais': related_ais
    })


# Available categories for AI tools
CATEGORIES = ["Transcription", "Image Generator", "Word Processor"]

def catalog_view(request):
    """
    Display the catalog of AI tools with filtering, sorting, and search capabilities.
    
    Filters:
    - searchAITool: Search by name, provider, or description
    - category: Filter by specific category
    - sort: Sort results by popularity or name
    """
    # Get filter parameters from request
    searchTerm = request.GET.get('searchAITool', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')
    
    # Start with all AI tools
    ai_tools = AITool.objects.all()

    # Apply category filter if provided and valid
    if category in CATEGORIES:
        ai_tools = ai_tools.filter(category=category)
    
    # Apply search filter if provided (search in name, provider, and description)
    if searchTerm:
        ai_tools = ai_tools.filter(
            Q(name__icontains=searchTerm) | 
            Q(provider__icontains=searchTerm) | 
            Q(description__icontains=searchTerm)
        )
    
    # Apply sorting if provided
    if sort:
        if sort == 'popularity_desc':
            ai_tools = ai_tools.order_by('-popularity')
        elif sort == 'popularity_asc':
            ai_tools = ai_tools.order_by('popularity')
        elif sort == 'name_asc':
            ai_tools = ai_tools.order_by('name')
        elif sort == 'name_desc':
            ai_tools = ai_tools.order_by('-name')
    else:
        # Default sorting by popularity (highest first)
        ai_tools = ai_tools.order_by('-popularity')
    
    # Get the featured AI (highest popularity)
    featured_ai = AITool.objects.all().order_by('-popularity').first()

    return render(request, 'catalog/catalog.html', {
        'ai_tools': ai_tools,
        'categories': CATEGORIES,
        'searchTerm': searchTerm,
        'current_category': category,
        'sort': sort,
        'featured_ai': featured_ai,
    })


def register_view(request):
    """Handle user registration."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Basic validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'catalog/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return render(request, 'catalog/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'catalog/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'catalog/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # Log in the user
        login(request, user)
        messages.success(request, 'Registration successful! Welcome to InspireAI.')
        
        return redirect('home')
    
    return render(request, 'catalog/register.html')


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not remember:
                # Session expires when browser closes
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {username}!')
            
            # Redirect to the page the user was trying to access, or home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'catalog/login.html')


def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """Display user profile with favorite AI tools and activity."""
    # Get user's favorite AI tools
    favorites = UserFavorite.objects.filter(user=request.user).select_related('ai_tool')
    
    # Get user's recent conversations
    recent_conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')[:5]
    
    return render(request, 'catalog/profile.html', {
        'user': request.user,
        'favorites': favorites,
        'recent_conversations': recent_conversations
    })


def chat_view(request, ai_id):
    """Display the chat interface for a specific AI tool."""
    ai_tool = get_object_or_404(AITool, id=ai_id)
    
    # Check if this AI has API integration
    has_api = ai_tool.api_type != 'none'
    
    # Get or create a conversation
    conversation_id = request.GET.get('conversation_id')
    if conversation_id:
        # Load existing conversation if ID provided
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user.is_authenticated and conversation.user != request.user:
            # Prevent access to other users' conversations
            messages.error(request, "You don't have permission to access this conversation.")
            return redirect('presentationAI', id=ai_id)
    else:
        # Create a new conversation
        conversation = Conversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            ai_tool=ai_tool,
            title=f"Chat with {ai_tool.name}"
        )
    
    # Get messages for this conversation
    chat_messages = conversation.get_messages()
    
    return render(request, 'catalog/chat.html', {
        'ai_tool': ai_tool,
        'conversation': conversation,
        'messages': chat_messages,
        'has_api': has_api
    })


@csrf_exempt
@require_POST
def send_message(request, conversation_id):
    """Handle sending messages in the chat."""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '')
        model_override = data.get('model', None)  # Get model from request if provided
        
        if not message_text.strip():
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Get the conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)
        ai_tool = conversation.ai_tool
        
        # Create user message
        user_message = Message.objects.create(
            conversation=conversation,
            content=message_text,
            is_user=True
        )
        
        # Process with AI based on tool's API type
        ai_response_text = "I'm sorry, this AI tool doesn't have active API integration."
        
        if ai_tool.api_type == 'openai':
            # Use model override if provided, otherwise use the one from the AI tool
            model = model_override or ai_tool.api_model or "gpt-3.5-turbo"
            response = utils.call_openai_api(message_text, model)
            if response['success']:
                try:
                    # For newer OpenAI API format
                    if 'choices' in response['data'] and 'message' in response['data']['choices'][0]:
                        ai_response_text = response['data']['choices'][0]['message']['content'].strip()
                    # For older OpenAI API format
                    elif 'choices' in response['data'] and 'text' in response['data']['choices'][0]:
                        ai_response_text = response['data']['choices'][0]['text'].strip()
                    else:
                        ai_response_text = "Received an unexpected response format from the AI."
                except (KeyError, IndexError):
                    ai_response_text = "Received an unexpected response format from the AI."
            else:
                ai_response_text = f"Error calling API: {response.get('error', 'Unknown error')}"
                
        elif ai_tool.api_type == 'huggingface':
            # Use model override if provided, otherwise use the one from the AI tool
            model = model_override or ai_tool.api_model or "google/flan-t5-base"
            response = utils.call_huggingface_api(message_text, model)
            if response['success']:
                try:
                    if isinstance(response['data'], list):
                        ai_response_text = response['data'][0]['generated_text']
                    else:
                        ai_response_text = response['data']['generated_text']
                except (KeyError, IndexError):
                    ai_response_text = "Received an unexpected response format from the AI."
            else:
                ai_response_text = f"Error calling API: {response.get('error', 'Unknown error')}"
        else:
            # For demo mode, create a simulated response
            service_config = {
                'api_type': 'none'
            }
            ai_response_text = utils.send_to_ai_service(message_text, service_config)
        
        # Create AI response message
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response_text,
            is_user=False
        )
        
        # Update conversation timestamp
        conversation.save()  # This updates the updated_at field
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat()
            },
            'ai_message': {
                'id': str(ai_message.id),
                'content': ai_message.content,
                'timestamp': ai_message.timestamp.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def download_conversation(request, conversation_id, format='json'):
    """Download conversation history in the specified format."""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user has access to this conversation
    if conversation.user and conversation.user != request.user:
        messages.error(request, "You don't have permission to access this conversation.")
        return redirect('profile')
    
    ai_name = conversation.ai_tool.name
    timestamp = conversation.updated_at.strftime('%Y%m%d_%H%M%S')
    filename = f"conversation_{ai_name}_{timestamp}"
    
    if format == 'json':
        # Return JSON format
        response = HttpResponse(conversation.to_json(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        return response
    
    elif format == 'txt':
        # Return plain text format
        lines = [f"Conversation with {ai_name} - {conversation.created_at.strftime('%Y-%m-%d %H:%M')}"]
        lines.append("-" * 50)
        
        for msg in conversation.get_messages():
            sender = "You" if msg.is_user else ai_name
            time_str = msg.timestamp.strftime('%H:%M:%S')
            lines.append(f"[{time_str}] {sender}: {msg.content}")
            
        response = HttpResponse("\n".join(lines), content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{filename}.txt"'
        return response
    
    else:
        messages.error(request, f"Unsupported format: {format}")
        return redirect('chat', ai_id=conversation.ai_tool.id)


@login_required
@require_POST
def toggle_favorite(request, ai_id):
    """Toggle favorite status for an AI tool."""
    ai_tool = get_object_or_404(AITool, id=ai_id)
    
    # Check if already favorited
    favorite, created = UserFavorite.objects.get_or_create(user=request.user, ai_tool=ai_tool)
    
    if not created:
        # If it existed, delete it (unfavorite)
        favorite.delete()
        status = 'removed'
    else:
        # If it was created, it's now favorited
        status = 'added'
    
    # Return JSON response
    return JsonResponse({
        'success': True,
        'status': status,
        'message': f"AI tool {status} {'to' if status == 'added' else 'from'} favorites"
    })


def chat_selection(request):
    """Display a page to select an AI model to chat with."""
    # Get filter parameters from request
    searchTerm = request.GET.get('searchAITool', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')
    
    # Start with all AI tools
    ai_tools = AITool.objects.all()

    # Apply category filter if provided and valid
    if category in CATEGORIES:
        ai_tools = ai_tools.filter(category=category)
    
    # Apply search filter if provided (search in name, provider, and description)
    if searchTerm:
        ai_tools = ai_tools.filter(
            Q(name__icontains=searchTerm) | 
            Q(provider__icontains=searchTerm) | 
            Q(description__icontains=searchTerm)
        )
    
    # Apply sorting if provided
    if sort:
        if sort == 'popularity_desc':
            ai_tools = ai_tools.order_by('-popularity')
        elif sort == 'popularity_asc':
            ai_tools = ai_tools.order_by('popularity')
        elif sort == 'name_asc':
            ai_tools = ai_tools.order_by('name')
        elif sort == 'name_desc':
            ai_tools = ai_tools.order_by('-name')
    else:
        # Default sorting by popularity (highest first)
        ai_tools = ai_tools.order_by('-popularity')
    
    # Get the featured AI (highest popularity)
    featured_ai = AITool.objects.all().order_by('-popularity').first()

    # Get user's recent conversations
    recent_conversations = []
    if request.user.is_authenticated:
        recent_conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')[:5]

    return render(request, 'catalog/chat_selection.html', {
        'ai_tools': ai_tools,
        'categories': CATEGORIES,
        'searchTerm': searchTerm,
        'current_category': category,
        'sort': sort,
        'featured_ai': featured_ai,
        'recent_conversations': recent_conversations,
    })


def compare_tools(request):
    """Compare two AI tools side by side."""
    tool1_id = request.GET.get('tool1')
    tool2_id = request.GET.get('tool2')
    
    tool1 = None
    tool2 = None
    
    if tool1_id:
        try:
            tool1 = AITool.objects.get(id=tool1_id)
        except AITool.DoesNotExist:
            pass
    
    if tool2_id:
        try:
            tool2 = AITool.objects.get(id=tool2_id)
        except AITool.DoesNotExist:
            pass
    
    # Get all AI tools for the dropdowns
    all_tools = AITool.objects.all().order_by('name')
    
    return render(request, 'catalog/compare.html', {
        'tool1': tool1,
        'tool2': tool2,
        'all_tools': all_tools
    })