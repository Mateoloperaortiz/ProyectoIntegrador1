from django.db import models
from django.conf import settings
from django.utils import timezone
import json
from typing import List, Dict, Any, Optional, Union
from django.db.models.query import QuerySet
from catalog.models import AITool
from core.models import UUIDModel, TimeStampedModel

class Conversation(UUIDModel, TimeStampedModel):
    """
    Model representing a conversation between a user and an AI tool.
    
    This model stores the metadata for a conversation, including references to the user,
    the AI tool being used, and timestamps for creation and updates.
    
    This model inherits from UUIDModel for UUID primary key and 
    TimeStampedModel for created_at and updated_at fields.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Changed from 'users.CustomUser' to settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interaction_conversations'
    )
    ai_tool = models.ForeignKey(
        'catalog.AITool',  
        on_delete=models.CASCADE,
        related_name='interaction_conversations'
    )
    title = models.CharField(max_length=255, default="New Conversation")
    
    def __str__(self) -> str:
        # Type checking: ensure user has username attribute
        user_str = self.user.username if self.user and hasattr(self.user, 'username') else "Anonymous"
        # Type checking: ensure ai_tool has name attribute
        tool_name = self.ai_tool.name if hasattr(self.ai_tool, 'name') else "Unknown Tool"
        return f"{user_str} - {tool_name} - {self.title}"
    
    def get_messages(self) -> 'QuerySet[Message]':
        """
        Get all messages in this conversation ordered by timestamp.
        
        Returns:
            QuerySet[Message]: QuerySet of Message objects ordered by timestamp
        """
        # Django automatically creates a message_set attribute for the reverse relation
        # Type ignore is needed because mypy doesn't understand Django's dynamic attributes
        return self.message_set.all().order_by('timestamp')  # type: ignore
    
    def to_json(self) -> str:
        """
        Convert conversation to JSON format for export.
        
        This method serializes the conversation and its messages into a JSON string
        suitable for export or API responses.
        
        Returns:
            str: JSON string representation of the conversation
        """
        data: Dict[str, Any] = {
            'id': str(self.id),
            'title': self.title,
            'ai_tool': self.ai_tool.name if hasattr(self.ai_tool, 'name') else "Unknown Tool",
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'messages': [
                {
                    'content': msg.content,
                    'is_user': msg.is_user,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in self.get_messages()
            ]
        }
        return json.dumps(data, indent=2)


class Message(models.Model):
    """
    Model representing a single message in a conversation.
    
    This model stores the content of a message, whether it was sent by the user or the AI,
    and when it was sent.
    
    Attributes:
        conversation (ForeignKey): Reference to the conversation this message belongs to
        content (TextField): The text content of the message
        is_user (BooleanField): Whether the message was sent by the user (True) or the AI (False)
        timestamp (DateTimeField): When the message was sent
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True if from user, False if from AI
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self) -> str:
        sender = "User" if self.is_user else "AI"
        return f"{sender} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class FavoritePrompt(UUIDModel, TimeStampedModel):
    """
    Model for storing user's favorite prompts.
    
    This model allows users to save prompts they frequently use with multiple AI tools.
    
    This model inherits from UUIDModel for UUID primary key and 
    TimeStampedModel for created_at and updated_at fields.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ai_tools = models.ManyToManyField(
        AITool, 
        related_name='favorite_prompts',
        blank=True,
        help_text="AI tools this prompt can be used with"
    )
    prompt_text = models.TextField()
    title = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        username = self.user.username if hasattr(self.user, 'username') else "Unknown User"
        return f"{username} - {self.title}"


class SharedChat(UUIDModel, TimeStampedModel):
    """
    Model for sharing conversations with other users or publicly.
    
    This model enables users to share their conversations either with specific users
    or publicly via an access token, with optional expiration.
    
    This model inherits from UUIDModel for UUID primary key and 
    TimeStampedModel for created_at and updated_at fields.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_chats')
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='received_chats'
    )
    is_public = models.BooleanField(default=False)
    access_token = models.CharField(max_length=64, unique=True)
    expiration_days = models.PositiveIntegerField(default=7, help_text="Number of days until the shared chat expires")
    
    def __str__(self) -> str:
        created_by_name = self.created_by.username if hasattr(self.created_by, 'username') else "Unknown User"
        if self.is_public:
            return f"Public share by {created_by_name}"
        elif self.recipient:
            recipient_name = self.recipient.username if hasattr(self.recipient, 'username') else "Unknown User"
            return f"Shared by {created_by_name} with {recipient_name}"
        else:
            return f"Private share by {created_by_name}"
    
    def is_expired(self) -> bool:
        """
        Check if the shared chat has expired.
        
        Returns:
            bool: True if the shared chat has expired, False otherwise
        """
        if self.expiration_days <= 0:
            # If expiration_days is 0 or negative, the shared chat never expires
            return False
            
        # Calculate the expiration date
        expiration_date = self.created_at + timezone.timedelta(days=self.expiration_days)
        
        # Check if the current time is past the expiration date
        return timezone.now() > expiration_date


# UserFavorite model has been removed in favor of using the ManyToManyField in CustomUser model
# This ensures a single source of truth for user favorites