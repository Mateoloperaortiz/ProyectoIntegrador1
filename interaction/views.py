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
    paginate_by = 10
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now()
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
        context['messages'] = Message.objects.filter(conversation=self.object)
        context['message_form'] = MessageForm()
        context['title_form'] = ConversationTitleForm(instance=self.object)
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
    
    return redirect('interaction:conversation_detail', pk=conversation.id)


def simulate_ai_response(tool, user_message):
    """
    Simulate an AI response when the API is not available.
    This is a fallback function when the real API integration is not working.
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
            form.save()
            messages.success(request, _('Conversation title updated!'))
    
    return redirect('interaction:conversation_detail', pk=conversation.id)
