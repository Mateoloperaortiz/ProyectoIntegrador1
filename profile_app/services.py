"""
Profile services for the profile app.

This module contains service functions for retrieving and manipulating user profile data.
"""
from typing import Dict, Any, List, Optional, Union, Tuple

from django.db.models import Count, QuerySet
from django.contrib.auth import get_user_model

from catalog.models import AITool
from interaction.models import Conversation, Message
from users.models import CustomUser

User = get_user_model()


def get_user_profile_data(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive profile data for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dictionary with profile data including favorites, conversations, and statistics
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {'error': 'User not found'}
    
    # Get user's favorites
    favorites = user.favorites.all()
    
    # Get user's recent conversations
    recent_conversations = Conversation.objects.filter(
        user=user
    ).order_by('-updated_at')[:10]
    
    # Get conversation statistics
    total_conversations = Conversation.objects.filter(user=user).count()
    total_messages = Message.objects.filter(conversation__user=user).count()
    
    # Get most used AI tool
    most_used_tool = None
    most_used_ai_tool = None
    
    if total_conversations > 0:
        tool_usage = Conversation.objects.filter(
            user=user
        ).values('ai_tool').annotate(count=Count('id')).order_by('-count')
        
        if tool_usage:
            most_used_tool_id = tool_usage[0]['ai_tool']
            if most_used_tool_id:
                most_used_ai_tool = AITool.objects.filter(id=most_used_tool_id).first()
                if most_used_ai_tool:
                    most_used_tool = most_used_ai_tool.name
    
    # Create profile form
    from users.forms import UserProfileForm
    profile_form = UserProfileForm(instance=user)
    
    # Create password form (we don't initialize it with data as it will be handled by the view)
    from django.contrib.auth.forms import PasswordChangeForm
    password_form = None
    
    return {
        'user': user,
        'favorites': favorites,
        'recent_conversations': recent_conversations,
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'most_used_tool': most_used_tool,
        'most_used_ai_tool': most_used_ai_tool,
        'profile_form': profile_form,
        'password_form': password_form
    }


def get_user_stats(user_id: str) -> Dict[str, Any]:
    """
    Get user statistics for the profile.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dictionary with user statistics
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {'error': 'User not found'}
    
    total_conversations = Conversation.objects.filter(user=user).count()
    total_messages = Message.objects.filter(conversation__user=user).count()
    favorites_count = user.favorites.count()
    
    # Calculate average messages per conversation
    avg_messages_per_conversation = 0
    if total_conversations > 0:
        avg_messages_per_conversation = total_messages / total_conversations
    
    # Get conversation count by month (last 6 months)
    # This is a placeholder - in a real implementation you would query by month
    conversations_by_month = [
        {'month': 'Jan', 'count': Conversation.objects.filter(user=user).count()},
        {'month': 'Feb', 'count': 0},
        {'month': 'Mar', 'count': 0},
        {'month': 'Apr', 'count': 0},
        {'month': 'May', 'count': 0},
        {'month': 'Jun', 'count': 0},
    ]
    
    return {
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'favorites_count': favorites_count,
        'avg_messages_per_conversation': round(avg_messages_per_conversation, 1),
        'conversations_by_month': conversations_by_month
    }