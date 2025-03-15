"""
Chat views for the interaction app.

This module contains views related to chatting with AI tools, including direct chat and conversation views.
"""
from typing import Any, Dict, List, Optional, Union
import json
import uuid
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from catalog.models import AITool
from catalog.utils import AIService
from interaction.models import Conversation, Message
from interaction.forms import MessageForm, ConversationForm
from interaction.utils import route_message_to_ai_tool


@login_required
def direct_chat(request: HttpRequest, template: str = 'interaction/unified/direct_chat.html') -> HttpResponse:
    """
    View for the direct chat interface.
    
    This view renders the direct chat interface, where users can chat with AI tools
    without explicitly selecting one.
    
    Args:
        request: The HTTP request object
        template: Optional template path to use for rendering (for variant chat interfaces)
        
    Returns:
        Rendered direct chat page
    """
    # Get the conversation ID from the request, if any
    conversation_id = request.GET.get('conversation_id')
    conversation = None
    messages_list = []
    
    # Debug logging
    logger = logging.getLogger(__name__)
    logger.info(f"Direct chat view called with conversation_id: {conversation_id}")
    
    # Log all available messages in the database for debugging
    all_messages_count = Message.objects.count()
    all_conversations_count = Conversation.objects.count()
    logger.info(f"Total messages in database: {all_messages_count}, Total conversations: {all_conversations_count}")
    
    if conversation_id:
        try:
            # Get the conversation if it exists and belongs to the user
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
            
            # Get the messages for this conversation
            messages_list = Message.objects.filter(
                conversation=conversation
            ).order_by('timestamp')
            
            # Debug logging
            logger.info(f"Found {messages_list.count()} messages for conversation {conversation_id}")
            
            # Force evaluation of the queryset
            messages_list = list(messages_list)
            
            for msg in messages_list:
                logger.info(f"Message: {msg.id}, is_user: {msg.is_user}, content: {msg.content[:50]}...")
        except (Conversation.DoesNotExist, ValueError):
            # If the conversation doesn't exist or ID is invalid, create an empty list
            messages_list = []
            logger.warning(f"Conversation {conversation_id} not found or invalid")
            
    # If we have no messages but have conversations in the database, try to get the most recent conversation
    if not messages_list and Conversation.objects.filter(user=request.user).exists():
        try:
            # Get the most recent conversation for this user
            recent_conversation = Conversation.objects.filter(user=request.user).order_by('-updated_at').first()
            if recent_conversation:
                conversation = recent_conversation
                messages_list = list(Message.objects.filter(conversation=conversation).order_by('timestamp'))
                logger.info(f"Using most recent conversation: {conversation.id} with {len(messages_list)} messages")
        except Exception as e:
            logger.error(f"Error getting recent conversation: {str(e)}")
    
    # Initialize the message form
    form = MessageForm()
    
    # Get all AI tools for the tool selector
    ai_tools = AITool.objects.all().order_by('name')
    
    return render(request, template, {
        'conversation': conversation,
        'conversation_id': conversation_id,  # Pass the original conversation_id as well
        'messages_list': messages_list,
        'chat_messages': messages_list,  # Add an alternative name to avoid potential conflicts
        'ai_tools': ai_tools,
        'form': form,
        'form_action': 'interaction:direct_chat_message'
    })


@login_required
def conversation_view(request: HttpRequest, conversation_id: uuid.UUID, template: str = 'interaction/unified/direct_chat.html') -> HttpResponse:
    """
    View for a specific conversation.
    
    This view renders a specific conversation, showing the message history
    and allowing the user to send new messages.
    
    Args:
        request: The HTTP request object
        conversation_id: The UUID of the conversation
        template: Optional template path to use for rendering (for variant chat interfaces)
        
    Returns:
        Rendered conversation page
    """
    # Get the conversation
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )
    
    # Handle form submission for sending a new message
    if request.method == 'POST':
        # Create a new message instance but don't save it yet
        new_message = Message(conversation=conversation, is_from_user=True)
        form = MessageForm(request.POST, instance=new_message)
        
        if form.is_valid():
            # Save the user message
            user_message = form.save()
            
            # Get the AI tool for this conversation
            ai_tool = conversation.ai_tool
            
            # Get the AI service for this tool
            ai_service = AIService(ai_tool)
            
            # Get the AI response
            ai_response = ai_service.get_response(user_message.content)
            
            # Save the AI response
            Message.objects.create(
                conversation=conversation,
                content=ai_response,
                is_from_user=False
            )
            
            # Update the conversation's last activity time
            conversation.updated_at = timezone.now()
            conversation.save(update_fields=['updated_at'])
            
            # Redirect to avoid form resubmission
            return redirect('interaction:conversation', conversation_id=conversation_id)
    else:
        # Initialize an empty form for GET requests
        form = MessageForm()
    
    # Get the messages for this conversation
    messages_list = Message.objects.filter(
        conversation=conversation
    ).order_by('timestamp')
    
    # Get all AI tools for the tool selector
    ai_tools = AITool.objects.all().order_by('name')
    
    return render(request, template, {
        'conversation': conversation,
        'messages_list': messages_list,
        'chat_messages': messages_list,  # For backward compatibility
        'messages': messages_list,       # For backward compatibility
        'ai_tools': ai_tools,
        'form': form,
        'form_action': 'interaction:send_message',
        'conversation_id': conversation_id,
        'chat_header_title': f"Conversation with {conversation.ai_tool.name}" if conversation.ai_tool else "Conversation"
    })


@login_required
@require_http_methods(["POST"])
def message_view(request: HttpRequest, conversation_id: Optional[uuid.UUID] = None) -> JsonResponse:
    """
    View for sending and receiving messages via AJAX.
    
    This view handles sending messages to AI tools and receiving responses with validation.
    
    Args:
        request: The HTTP request object
        conversation_id: The UUID of the conversation, if any
        
    Returns:
        JSON response with the AI's reply or validation errors
    """
    user = request.user
    
    # Log request details
    logger.info(f"Message view called with conversation_id: {conversation_id}")
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"POST data present: {bool(request.POST)}")
    if request.POST:
        logger.info(f"POST keys: {list(request.POST.keys())}")
    
    # Get the message content from the request
    # Try to get data from POST first (form data)
    if request.POST:
        user_message = request.POST.get('message', '').strip()
        ai_tool_id = request.POST.get('ai_tool_id')
        logger.info(f"Got message from POST: '{user_message[:50]}...' (truncated)")
    else:
        # If not in POST, try to parse JSON data
        try:
            logger.info("No POST data, trying to parse request body as JSON")
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            ai_tool_id = data.get('ai_tool_id')
            logger.info(f"Got message from JSON: '{user_message[:50]}...' (truncated)")
        except json.JSONDecodeError:
            logger.error("Failed to parse request body as JSON")
            return JsonResponse({
                'error': 'Invalid request data'
            }, status=400)
    
    # Validate the message
    errors = {}
    if not user_message:
        errors['message'] = ['Message cannot be empty.']
    elif len(user_message) < 2:
        errors['message'] = ['Message must be at least 2 characters long.']
    elif len(user_message) > 5000:
        errors['message'] = ['Message must be less than 5000 characters.']
    
    # If there are validation errors, return them
    if errors:
        return JsonResponse({
            'errors': errors
        }, status=400)
    
    # Get or create the conversation
    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        except (Conversation.DoesNotExist, ValueError):
            # If the conversation doesn't exist or ID is invalid, create a new one
            conversation = None
    
    # If no conversation exists, create a new one
    if not conversation:
        # If an AI tool ID is provided, use that tool
        ai_tool = None
        if ai_tool_id:
            try:
                ai_tool = AITool.objects.get(id=ai_tool_id)
            except AITool.DoesNotExist:
                # If the AI tool doesn't exist, use smart routing
                ai_tool = None
        
        # If no AI tool is specified, use smart routing
        if not ai_tool:
            ai_tool = route_message_to_ai_tool(user_message)
            # Log the selected AI tool for debugging
            logger.info(f"Smart routing selected AI tool: {ai_tool.name if ai_tool else 'None'}")
        
        # Create a new conversation with the selected AI tool
        conversation = Conversation.objects.create(
            user=user,
            ai_tool=ai_tool,
            title=user_message[:50] + ('...' if len(user_message) > 50 else '')
        )
    
    # Create a new message instance
    new_message = Message(
        conversation=conversation,
        content=user_message,
        is_user=True  # Using the correct field name from the model
    )
    
    # Validate the message with our form
    form = MessageForm(instance=new_message, data={'content': user_message})
    if not form.is_valid():
        return JsonResponse({
            'errors': form.errors
        }, status=400)
    
    # Save the user message
    user_message_obj = form.save()
    
    # Get the AI tool for this conversation
    ai_tool = conversation.ai_tool
    
    # Get the AI tool configuration
    service_config = {
        'api_type': ai_tool.api_type,
        'api_model': ai_tool.api_model
    }
    
    # Get the AI response using the static method
    response = AIService.send_to_ai_service(user_message, service_config)
    
    # Extract the response content
    if response.get('success', False):
        ai_response = response.get('data', 'Sorry, I could not process your request.')
    else:
        ai_response = response.get('error', 'Sorry, an error occurred while processing your request.')
    
    # Save the AI response
    ai_message = Message.objects.create(
        conversation=conversation,
        content=ai_response,
        is_user=False  # Using the correct field name from the model
    )
    
    # Update the conversation's last activity time
    conversation.updated_at = timezone.now()
    conversation.save(update_fields=['updated_at'])
    
    # Check if the request is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return JSON as before
        return JsonResponse({
            'message': ai_response,
            'conversation_id': str(conversation.id),
            'ai_tool_name': ai_tool.name,
            'timestamp': ai_message.timestamp.isoformat()
        })
    else:
        # If it's a regular form submission, redirect to the chat interface
        return redirect(f'/interaction/direct-chat/?conversation_id={conversation.id}')


import logging
logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
def direct_chat_message(request: HttpRequest) -> JsonResponse:
    """
    View for handling direct chat messages.
    
    This view processes messages sent from the direct chat interface,
    routes them to the appropriate AI tool, and returns the AI's response.
    
    Args:
        request: The HTTP request object
        
    Returns:
        JSON response with the AI's reply
    """
    # Log request details
    logger.info(f"Received direct chat message request: POST={bool(request.POST)}, FILES={bool(request.FILES)}")
    logger.info(f"Content type: {request.content_type}")
    
    # Log POST data
    if request.POST:
        logger.info(f"POST data keys: {list(request.POST.keys())}")
    
    # Get the conversation ID from the request, if any
    conversation_id = request.POST.get('conversation_id')
    logger.info(f"Conversation ID from POST: {conversation_id}")
    
    # Log all request headers for debugging
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.info(f"Is AJAX request: {is_ajax}")
    
    # Log all form data for debugging
    logger.info(f"POST data: {dict(request.POST)}")
    
    if conversation_id:
        try:
            # Convert the conversation ID to a UUID
            conversation_uuid = uuid.UUID(conversation_id)
            logger.info(f"Valid conversation UUID: {conversation_uuid}")
            # Call the message view with the conversation ID
            return message_view(request, conversation_uuid)
        except (ValueError, TypeError):
            # If the conversation ID is invalid, log it and continue without it
            logger.warning(f"Invalid conversation ID format: {conversation_id}")
            conversation_id = None
    else:
        logger.info("No conversation ID provided")
    
    # If no conversation ID is provided or it's invalid, call the message view without it
    return message_view(request)


@login_required
def chat_selection(request: HttpRequest) -> HttpResponse:
    """
    View for selecting an AI tool to chat with.
    
    This view renders the chat selection interface, where users can choose
    which AI tool they want to chat with.
    
    Args:
        request: The HTTP request object
        
    Returns:
        Rendered chat selection page
    """
    # Get all AI tools
    ai_tools = AITool.objects.all().order_by('name')
    
    # Get recent conversations
    recent_conversations = Conversation.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:5]
    
    return render(request, 'interaction/chat_selection.html', {
        'ai_tools': ai_tools,
        'recent_conversations': recent_conversations
    })


@login_required
def chat_view(request: HttpRequest, ai_id=None, 
               conversation_id=None, template: str = 'interaction/unified/direct_chat.html') -> HttpResponse:
    """
    View for the chat interface.
    
    This view renders the chat interface for a specific AI tool or conversation.
    
    Args:
        request: The HTTP request object
        ai_id: The UUID of the AI tool, if starting a new conversation
        conversation_id: The UUID of the conversation, if continuing an existing one
        template: Optional template path to use for rendering (for variant chat interfaces)
        
    Returns:
        Rendered chat page
    """
    # Initialize variables
    ai_tool = None
    conversation = None
    messages_list = []
    
    # If a conversation ID is provided, load that conversation
    if conversation_id:
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        ai_tool = conversation.ai_tool
        messages_list = Message.objects.filter(
            conversation=conversation
        ).order_by('timestamp')
        
        # Handle form submission for sending a new message
        if request.method == 'POST':
            # Create a new message instance but don't save it yet
            new_message = Message(conversation=conversation, is_from_user=True)
            form = MessageForm(request.POST, instance=new_message)
            
            if form.is_valid():
                # Save the user message
                user_message = form.save()
                
                # Get the AI service for this tool
                ai_service = AIService(ai_tool)
                
                # Get the AI response
                ai_response = ai_service.get_response(user_message.content)
                
                # Save the AI response
                Message.objects.create(
                    conversation=conversation,
                    content=ai_response,
                    is_from_user=False
                )
                
                # Update the conversation's last activity time
                conversation.updated_at = timezone.now()
                conversation.save(update_fields=['updated_at'])
                
                # Redirect to avoid form resubmission
                return redirect('interaction:chat', conversation_id=conversation_id)
            else:
                # If the form is invalid, add error messages
                for field, errors in form.errors.items():
                    for error in errors:
                        django_messages.error(request, f"{field.capitalize()}: {error}")
        else:
            # Initialize an empty form for GET requests
            form = MessageForm()
    # If an AI tool ID is provided, load that tool and create a form for a new conversation
    elif ai_id:
        try:
            # Try to get the AI tool by ID (handles both UUID and integer IDs)
            ai_tool = get_object_or_404(AITool, id=ai_id)
        except (ValueError, ValidationError):
            # If there's a validation error (invalid UUID), redirect to chat selection
            django_messages.error(request, f"Invalid AI tool ID: {ai_id}")
            return redirect('interaction:chat_selection')
        form = MessageForm()
        
        # Handle form submission for creating a new conversation and sending the first message
        if request.method == 'POST':
            # Create a new conversation
            conversation = Conversation.objects.create(
                user=request.user,
                ai_tool=ai_tool,
                title=request.POST.get('content', '')[:50] + ('...' if len(request.POST.get('content', '')) > 50 else '')
            )
            
            # Create a new message instance but don't save it yet
            new_message = Message(conversation=conversation, is_from_user=True)
            form = MessageForm(request.POST, instance=new_message)
            
            if form.is_valid():
                # Save the user message
                user_message = form.save()
                
                # Get the AI service for this tool
                ai_service = AIService(ai_tool)
                
                # Get the AI response
                ai_response = ai_service.get_response(user_message.content)
                
                # Save the AI response
                Message.objects.create(
                    conversation=conversation,
                    content=ai_response,
                    is_from_user=False
                )
                
                # Redirect to the new conversation
                return redirect('interaction:chat', conversation_id=conversation.id)
            else:
                # If the form is invalid, add error messages
                for field, errors in form.errors.items():
                    for error in errors:
                        django_messages.error(request, f"{field.capitalize()}: {error}")
    # If neither is provided, redirect to the chat selection page
    else:
        return redirect('interaction:chat_selection')
    
    # Get all AI tools for the tool selector
    ai_tools = AITool.objects.all().order_by('name')
    
    return render(request, template, {
        'ai_tool': ai_tool,
        'conversation': conversation,
        'messages_list': messages_list, 
        'messages': messages_list,      # For backward compatibility
        'chat_messages': messages_list, # For backward compatibility
        'ai_tools': ai_tools,
        'form': form,
        'form_action': 'interaction:send_message' if conversation else 'interaction:message_view',
        'conversation_id': conversation.id if conversation else None,
        'chat_header_title': f"Chat with {ai_tool.name}" if ai_tool else "Chat with AI Assistant",
        'show_debug': request.GET.get('debug', 'false').lower() == 'true'
    })


@login_required
@require_http_methods(["POST"])
def send_message(request: HttpRequest, conversation_id: uuid.UUID) -> JsonResponse:
    """
    View for sending a message in an existing conversation.
    
    This view handles sending a message in an existing conversation and returns the AI's response.
    
    Args:
        request: The HTTP request object
        conversation_id: The UUID of the conversation
        
    Returns:
        JSON response with the AI's reply
    """
    # Call the message view with the conversation ID
    return message_view(request, conversation_id)
