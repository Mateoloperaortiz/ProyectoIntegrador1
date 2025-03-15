"""
Profile services for the profile app.

This module contains service functions for retrieving and manipulating user profile data.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta

from django.db.models import Count, QuerySet, Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model
from django.utils import timezone

from catalog.models import AITool
from interaction.models import Conversation, Message, FavoritePrompt
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
    
    # Get favorite prompts
    favorite_prompts = FavoritePrompt.objects.filter(user=user).order_by('-updated_at')[:5]
    
    # Get most used AI tool
    most_used_tool = None
    most_used_ai_tool = None
    
    if total_conversations > 0:
        tool_usage = Conversation.objects.filter(
            user=user
        ).values('ai_tool').annotate(count=Count('id')).order_by('-count')
        
        if tool_usage and tool_usage[0]['ai_tool'] is not None:
            most_used_tool_id = tool_usage[0]['ai_tool']
            most_used_ai_tool = AITool.objects.filter(id=most_used_tool_id).first()
            if most_used_ai_tool:
                most_used_tool = most_used_ai_tool.name
    
    # Get additional stats
    stats = get_user_stats(user_id)
    
    # Get activity timeline
    activity_timeline = get_user_activity_timeline(user_id)
    
    return {
        'user': user,
        'favorites': favorites,
        'favorite_prompts': favorite_prompts,
        'recent_conversations': recent_conversations,
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'most_used_tool': most_used_tool,
        'most_used_ai_tool': most_used_ai_tool,
        'stats': stats,
        'activity_timeline': activity_timeline
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
    prompts_count = FavoritePrompt.objects.filter(user=user).count()
    
    # Calculate average messages per conversation
    avg_messages_per_conversation = 0
    if total_conversations > 0:
        avg_messages_per_conversation = total_messages / total_conversations
    
    # Get conversation count by month (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    conversations_by_month = Conversation.objects.filter(
        user=user, 
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Format for template
    formatted_conversations_by_month = []
    for item in conversations_by_month:
        formatted_conversations_by_month.append({
            'month': item['month'].strftime('%b'),
            'count': item['count']
        })
    
    # Get most active day of week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    conversations_by_day = Conversation.objects.filter(
        user=user
    ).annotate(
        day=Count('created_at__week_day')
    ).values('created_at__week_day').annotate(
        count=Count('id')
    ).order_by('-count')
    
    most_active_day = None
    if conversations_by_day:
        # Django's week_day is 1-7 where 1 is Sunday
        day_index = conversations_by_day[0]['created_at__week_day'] - 1
        day_index = (day_index + 1) % 7  # Convert to Monday=0 format
        most_active_day = days[day_index]
    
    return {
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'favorites_count': favorites_count,
        'prompts_count': prompts_count,
        'avg_messages_per_conversation': round(avg_messages_per_conversation, 1),
        'conversations_by_month': formatted_conversations_by_month,
        'most_active_day': most_active_day
    }


def get_user_activity_timeline(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get a timeline of user activity.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of events to return
        
    Returns:
        List of activity events
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return []
    
    # Get recent conversations
    conversations = Conversation.objects.filter(
        user=user
    ).order_by('-created_at')[:limit]
    
    # Create timeline events
    timeline = []
    for conv in conversations:
        timeline.append({
            'type': 'conversation',
            'object': conv,
            'timestamp': conv.created_at,
            'title': f'Started conversation with {conv.ai_tool.name if conv.ai_tool else "AI"}',
            'icon': 'comment'
        })
    
    # Future: Add other event types like favorite additions, prompt creations, etc.
    
    # Sort by timestamp descending and limit
    timeline.sort(key=lambda x: x['timestamp'], reverse=True)
    return timeline[:limit]