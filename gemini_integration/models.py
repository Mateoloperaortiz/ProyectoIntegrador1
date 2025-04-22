from django.db import models
from django.conf import settings
from interaction.models import Conversation, Message

class GeminiFile(models.Model):
    """
    Model to track Gemini file uploads and their metadata.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gemini_file_id = models.CharField(max_length=255, unique=True)
    filename = models.CharField(max_length=255)
    purpose = models.CharField(max_length=50, choices=[
        ('general', 'General Use'),
        ('vision', 'Vision'),
        ('document', 'Document Analysis'),
        ('audio', 'Audio Analysis'),
        ('video', 'Video Analysis')
    ], default='general')
    mime_type = models.CharField(max_length=100, default='application/octet-stream')
    bytes_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.filename} ({self.gemini_file_id})"


class MessageGeminiFile(models.Model):
    """
    Model to associate Messages with Gemini files.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='gemini_files')
    gemini_file = models.ForeignKey(GeminiFile, on_delete=models.CASCADE, related_name='message_links')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'gemini_file')
    
    def __str__(self):
        return f"Link between {self.message} and {self.gemini_file}"
