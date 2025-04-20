from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import json
import random

from .models import Conversation, Message, Favorite
from .forms import MessageForm, ConversationTitleForm
from catalog.models import AITool

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


class ConversationListView(LoginRequiredMixin, ListView):
    """
    View for listing user's conversations.
    """
    model = Conversation
    template_name = 'interaction/conversation_list.html'
    context_object_name = 'conversations'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Conversation.objects.filter(user=self.request.user)
        
        # Filter by tool if requested
        tool_id = self.request.GET.get('tool')
        if tool_id:
            queryset = queryset.filter(tool_id=tool_id)
        
        # Filter by date range if requested
        date_range = self.request.GET.get('date_range')
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                queryset = queryset.filter(updated_at__date=today)
            elif date_range == 'week':
                week_ago = today - timezone.timedelta(days=7)
                queryset = queryset.filter(updated_at__date__gte=week_ago)
            elif date_range == 'month':
                month_ago = today - timezone.timedelta(days=30)
                queryset = queryset.filter(updated_at__date__gte=month_ago)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now()
        
        # Get all AI tools the user has conversations with for the filter dropdown
        user_conversation_tools = AITool.objects.filter(
            conversation__user=self.request.user
        ).distinct().order_by('name')
        context['user_tools'] = user_conversation_tools
        
        # Add filter parameters to context
        context['current_tool'] = self.request.GET.get('tool', '')
        context['current_date_range'] = self.request.GET.get('date_range', '')
        
        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a conversation.
    """
    model = Conversation
    template_name = 'interaction/conversation_detail.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the conversation object safely
        conversation = self.get_object()
        context['messages'] = Message.objects.filter(conversation=conversation)
        context['message_form'] = MessageForm()
        context['title_form'] = ConversationTitleForm(instance=conversation)
        return context


@login_required
def start_conversation(request, tool_id):
    """
    Start a new conversation with an AI tool.
    """
    tool = get_object_or_404(AITool, id=tool_id)
    
    conversation = Conversation.objects.create(
        user=request.user,
        tool=tool,
        title=f"Conversation with {tool.name}"
    )
    
    return redirect('interaction:conversation_detail', pk=conversation.id)


@login_required
def send_message(request, conversation_id):
    """
    Send a message in a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                is_from_user=True,
                content=form.cleaned_data['content']
            )
            
            # Generate AI response
            ai_response = simulate_ai_response(conversation.tool, form.cleaned_data['content'])
            
            # Save AI response
            ai_message = Message.objects.create(
                conversation=conversation,
                is_from_user=False,
                content=ai_response
            )
            
            # Update conversation timestamp
            conversation.save()
            
            # If AJAX request, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'user_message': {
                        'content': user_message.content,
                        'timestamp': user_message.timestamp.strftime('%b %d, %Y, %I:%M %p')
                    },
                    'ai_message': {
                        'content': ai_message.content,
                        'timestamp': ai_message.timestamp.strftime('%b %d, %Y, %I:%M %p')
                    }
                })
            
            # No need for a success message for each chat message
            # Prevent empty messages from appearing
    
    return redirect('interaction:conversation_detail', pk=conversation.id)


def simulate_ai_response(tool, user_message):
    """
    Generate an AI response using the appropriate API based on the tool's configuration.
    Falls back to simulated responses if API calls fail.
    """
    import os
    import requests
    from openai import OpenAI
    
    try:
        if tool.api_type == 'OPENAI':
            return generate_openai_response(tool, user_message)
        elif tool.api_type == 'HUGGINGFACE':
            return generate_huggingface_response(tool, user_message)
        elif tool.api_type == 'ANTHROPIC':
            return fallback_response(tool, user_message, "Anthropic API integration is coming soon.")
        elif tool.api_type == 'GOOGLE':
            return fallback_response(tool, user_message, "Google AI API integration is coming soon.")
        else:
            return fallback_response(tool, user_message)
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return fallback_response(tool, user_message, f"API Error: {str(e)}")


def generate_openai_response(tool, user_message):
    """
    Generate a response using OpenAI API (using the new responses endpoint as per official docs).
    """
    import os
    from openai import OpenAI

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return fallback_response(tool, user_message, "OpenAI API key not found in environment.")

    client = OpenAI(api_key=api_key)
    model = tool.api_model if tool.api_model else "o4-mini-2025-04-16"

    # Use the new responses endpoint for text and image (vision) models
    try:
        # If the tool is for images, check if user_message is a dict/list for vision input
        if tool.category == 'IMAGE' and isinstance(user_message, (list, dict)):
            response = client.responses.create(
                model=model,
                input=user_message
            )
        else:
            response = client.responses.create(
                model=model,
                input=user_message
            )
        return getattr(response, 'output_text', str(response))
    except Exception as e:
        return fallback_response(tool, user_message, f"OpenAI API error: {str(e)}")


def generate_huggingface_response(tool, user_message):
    """
    Generate a response using Hugging Face API.
    """
    import os
    import requests
    import json
    
    api_key = os.environ.get('HUGGINGFACE_API_KEY')
    if not api_key:
        return fallback_response(tool, user_message, "Hugging Face API key not found in environment.")
    
    api_endpoint = tool.api_endpoint if tool.api_endpoint else "https://api-inference.huggingface.co/models/gpt2"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": user_message,
        "parameters": {
            "max_length": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            if tool.category == 'IMAGE':
                return "I've created an image based on your description. (Image data would be displayed here)"
            elif 'generated_text' in result[0]:
                return result[0]['generated_text']
            else:
                return json.dumps(result)
        else:
            return fallback_response(tool, user_message, "Unexpected response format from Hugging Face API.")
    except Exception as e:
        return fallback_response(tool, user_message, f"Hugging Face API error: {str(e)}")


def fallback_response(tool, user_message, error_message=None):
    """
    Generate a fallback response when API calls fail.
    """
    # Simple responses based on AI tool category
    responses = {
        'TEXT': [
            "I've generated a text passage based on your input.",
            "Here's a creative text I've written for you.",
            "I hope you find this text helpful for your needs."
        ],
        'IMAGE': [
            "I've created an image based on your description.",
            "Your image has been generated. I hope it matches what you had in mind.",
            "Here's the visualization I created from your prompt."
        ],
        'CHAT': [
            "That's an interesting question! Let me share my thoughts.",
            "I understand what you're asking. Here's my response.",
            "Great conversation! Here's what I think about that."
        ]
    }
    
    # Get responses for the tool's category or use generic responses
    category_responses = responses.get(tool.category, [
        "Thank you for your input. Here's my response.",
        "I've processed your request and here are the results.",
        "I hope this answer helps with what you were looking for."
    ])
    
    # Random response from category
    response = random.choice(category_responses)
    
    # Add some context from the user message to make it seem more responsive
    words = user_message.split()
    if len(words) > 3:
        keywords = words[:3]
        response += f" I noticed you mentioned {', '.join(keywords)}."
    
    if error_message:
        response += f"\n\n(Note: {error_message})"
    
    return response


@login_required
def update_conversation_title(request, conversation_id):
    """
    Update the title of a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    if request.method == 'POST':
        form = ConversationTitleForm(request.POST, instance=conversation)
        if form.is_valid():
            # Get the old title for comparison
            old_title = conversation.title
            form.save()
            
            # Only display a success message if the title actually changed
            if old_title != form.cleaned_data['title']:
                messages.success(request, _('Conversation title updated!'))
    
    return redirect('interaction:conversation_detail', pk=conversation.id)


@login_required
def delete_conversation(request, conversation_id):
    """
    Delete a conversation and all its messages.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    if request.method == 'POST':
        # Store the conversation title for the success message
        title = conversation.title
        
        # Delete the conversation (cascade will delete all related messages)
        conversation.delete()
        
        # Show success message
        messages.success(request, _(f'Conversation "{title}" has been deleted.'))
        
        # Redirect to conversation list
        return redirect('interaction:conversation_list')
    
    # If not POST, show confirmation page
    return render(request, 'interaction/delete_confirmation.html', {
        'conversation': conversation
    })
