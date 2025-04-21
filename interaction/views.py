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
import os
import requests
import io
import base64
from openai import OpenAI
import google.genai as genai
from PIL import Image

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
    NOTE: This view is primarily a fallback for non-JS/non-WebSocket scenarios or
          for API types that don't support streaming via the ChatConsumer yet.
          The main interaction for streaming APIs (OpenAI, Gemini) happens via WebSocket.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_content = form.cleaned_data['content']
            # Note: Image handling is NOT implemented in this fallback view.
            # It assumes text-only input for simplicity.
            user_message = Message.objects.create(
                conversation=conversation,
                is_from_user=True,
                content=user_content
            )
            
            # Generate AI response using the simulation/fallback function
            # This function handles dispatching to the correct non-streaming API call
            ai_response_content = simulate_ai_response(conversation.tool, user_content)
            
            ai_message = Message.objects.create(
                conversation=conversation,
                is_from_user=False,
                content=ai_response_content
            )
            
            conversation.save() # Update timestamp
            
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
            
    # Redirect back to the conversation for non-AJAX POST or GET requests
    return redirect('interaction:conversation_detail', pk=conversation.id)


def simulate_ai_response(tool, user_message):
    """
    Dispatch to the appropriate non-streaming API generation function based on tool type.
    Handles text input only in this fallback implementation.
    """
    try:
        if tool.api_type == 'OPENAI':
            # Note: generate_openai_response might need adjustment if it expects multimodal input here
            return generate_openai_response(tool, user_message)
        elif tool.api_type == 'GEMINI':
            return generate_gemini_response(tool, user_message)
        elif tool.api_type == 'HUGGINGFACE':
            return generate_huggingface_response(tool, user_message)
        elif tool.api_type == 'ANTHROPIC':
            return fallback_response(tool, user_message, "Anthropic API integration is not yet available for non-streaming.")
        elif tool.api_type == 'GOOGLE': # Consider renaming or removing if GEMINI covers all Google AI
            return fallback_response(tool, user_message, "Google AI API integration is not yet available for non-streaming.")
        else:
            return fallback_response(tool, user_message)
    except Exception as e:
        print(f"Error in simulate_ai_response dispatcher: {str(e)}")
        # Provide a generic error message via fallback
        return fallback_response(tool, user_message, f"An error occurred while processing the request: {str(e)}")


def generate_openai_response(tool, user_message):
    """
    Non-streaming OpenAI response generation (Text only for fallback).
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return fallback_response(tool, user_message, "OpenAI API key not found.")

    try:
        client = OpenAI(api_key=api_key)
        model = tool.api_model or "gpt-4o" # Default model

        # Using chat completions endpoint for consistency, text-only
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are {tool.name}, an AI assistant by {tool.provider}. Respond concisely."}, # Simplified prompt for fallback
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return fallback_response(tool, user_message, f"OpenAI API error (non-streaming): {str(e)}")


def generate_gemini_response(tool, user_message):
    """
    Non-streaming Gemini response generation (Text only for fallback).
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return fallback_response(tool, user_message, "Gemini API key not found.")

    try:
        genai.configure(api_key=api_key)
        model_name = tool.api_model or "gemini-2.0-flash-live-001"
        model = genai.GenerativeModel(model_name)

        # Generate content with text only for this fallback
        response = model.generate_content(user_message)
        # Handle potential lack of text in response
        if response.parts:
             return response.text
        else:
             # Handle cases where the response might be blocked or empty
             # Log the full response for debugging
             print(f"Gemini Warning: Received response with no parts. Full response: {response}")
             # Check for prompt feedback indicating blocking
             if response.prompt_feedback and response.prompt_feedback.block_reason:
                 return f"My response was blocked due to: {response.prompt_feedback.block_reason.name}. Please modify your prompt."
             return fallback_response(tool, user_message, "Received an empty or blocked response from Gemini.")

    except Exception as e:
        return fallback_response(tool, user_message, f"Gemini API error (non-streaming): {str(e)}")


def generate_huggingface_response(tool, user_message):
    """
    Generate a response using Hugging Face API (placeholder/example).
    Requires tool.api_endpoint to be set correctly.
    """
    api_key = os.environ.get('HUGGINGFACE_API_KEY') # Assumes HF key is needed
    if not api_key:
        return fallback_response(tool, user_message, "Hugging Face API key not found.")
    if not tool.api_endpoint:
         return fallback_response(tool, user_message, "Hugging Face model endpoint not configured for this tool.")

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": user_message}
        response = requests.post(tool.api_endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raise an exception for bad status codes
        result = response.json()
        # The actual response structure depends heavily on the specific HF model/API
        # This is a common structure for text generation models
        return result[0].get('generated_text', "Sorry, I couldn't process that.")
    except requests.exceptions.RequestException as e:
         return fallback_response(tool, user_message, f"Hugging Face API request error: {str(e)}")
    except Exception as e:
        return fallback_response(tool, user_message, f"Hugging Face API error: {str(e)}")


def fallback_response(tool, user_message, error_message=None):
    """
    Provides a generic fallback response or formats an error message.
    """
    if error_message:
        print(f"Fallback triggered for {tool.name}: {error_message}")
        return f"I encountered an issue processing your request with {tool.name}. Error: {error_message}"
    else:
        responses = [
            f"Sorry, I can't fully process that request with {tool.name} right now.",
            f"Hmm, I'm having trouble connecting to the {tool.name} service.",
            f"Let me try that again later. I couldn't get a response from {tool.name}."
        ]
        return random.choice(responses)


@login_required
def update_conversation_title(request, conversation_id):
    """
    Update the title of a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        form = ConversationTitleForm(request.POST, instance=conversation)
        if form.is_valid():
            form.save()
            # Return JSON for AJAX request or redirect
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'new_title': conversation.title})
            else:
                messages.success(request, _('Conversation title updated.'))
                return redirect('interaction:conversation_detail', pk=conversation.id)
        else:
            # Handle errors if needed, perhaps return JSON error
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            else:
                 messages.error(request, _('Error updating title.'))
    # If not POST, or if form invalid in non-AJAX, redirect back
    return redirect('interaction:conversation_detail', pk=conversation.id)


@login_required
def delete_conversation(request, conversation_id):
    """
    Delete a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        conversation_title = conversation.title # Get title before deleting
        conversation.delete()
        messages.success(request, _(f'Conversation "{conversation_title}" deleted.'))
        return redirect('interaction:conversation_list')
    
    # If GET, render confirmation page (though usually handled by modal)
    # You might want to redirect to list if accessed via GET directly
    # return render(request, 'interaction/delete_confirmation.html', {'conversation': conversation})
    return redirect('interaction:conversation_list')
