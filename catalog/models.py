import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class AITool(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    endpoint = models.URLField()
    category = models.CharField(max_length=100)
    description = models.TextField()
    popularity = models.IntegerField()
    image = models.ImageField(upload_to='ai_images/', null=True, blank=True)
    # New fields for API integration
    api_type = models.CharField(
        max_length=50, 
        choices=[
            ('openai', 'OpenAI API'),
            ('huggingface', 'Hugging Face API'),
            ('custom', 'Custom Integration'),
            ('none', 'No Integration')
        ],
        default='none'
    )
    api_model = models.CharField(max_length=100, blank=True, null=True)
    api_endpoint = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # New OpenRouter-like fields
    modality = models.CharField(
        max_length=50,
        choices=[
            ('text-to-text', 'Text to Text'),
            ('text-image-to-text', 'Text & Image to Text'),
            ('other', 'Other')
        ],
        default='text-to-text'
    )
    context_length = models.IntegerField(default=4096)
    prompt_pricing = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    completion_pricing = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    series = models.CharField(max_length=100, blank=True, null=True)  # e.g., GPT, Claude, Gemini
    supported_parameters = models.TextField(blank=True, null=True)  # Stored as JSON
    throughput = models.IntegerField(default=1)  # Requests per minute
    latency = models.IntegerField(default=500)  # ms
    release_date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    def get_parameters_list(self):
        """Return supported parameters as a list"""
        if not self.supported_parameters:
            return []
        try:
            return json.loads(self.supported_parameters)
        except:
            return []


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ai_tool = models.ForeignKey(AITool, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'ai_tool')
        
    def __str__(self):
        return f"{self.user.username} - {self.ai_tool.name}"


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ai_tool = models.ForeignKey(AITool, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.ai_tool.name} - {self.title}"
    
    def get_messages(self):
        return self.message_set.all().order_by('timestamp')
    
    def to_json(self):
        """Convert conversation to JSON format for export"""
        data = {
            'id': str(self.id),
            'title': self.title,
            'ai_tool': self.ai_tool.name,
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
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True if from user, False if from AI
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        sender = "User" if self.is_user else "AI"
        return f"{sender} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
