from django.db import models
from django.conf import settings
from catalog.models import AITool
import uuid

class Conversation(models.Model):
    """
    Model representing a conversation with an AI tool.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} with {self.tool.name} by {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Auto-generate title from first message if not set
        if not self.title and hasattr(self, 'message_set') and self.message_set.exists():
            first_msg = self.message_set.first().content
            self.title = first_msg[:50] + ('...' if len(first_msg) > 50 else '')
        super().save(*args, **kwargs)


class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    is_from_user = models.BooleanField(default=True)  # True if from user, False if from AI
    content = models.TextField()  # May contain HTML content for image understanding features
    image_url = models.TextField(blank=True, null=True)  # Optional image URL or base64
    pdf_url = models.TextField(blank=True, null=True)  # Optional PDF URL or base64
    video_url = models.TextField(blank=True, null=True)  # Optional video URL or base64/YouTube
    audio_url = models.TextField(blank=True, null=True)  # Optional audio URL or base64
    file_type = models.CharField(max_length=20, blank=True, null=True)  # Type of file (image, pdf, video, audio, etc.)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        sender = 'User' if self.is_from_user else 'AI'
        return f"{sender} message in {self.conversation.id}"


class Favorite(models.Model):
    """
    Model representing a user's favorite AI tool.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'tool')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} favorited {self.tool.name}"
