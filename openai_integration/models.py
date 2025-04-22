from django.db import models
from django.conf import settings
from interaction.models import Conversation, Message

class OpenAIFile(models.Model):
    """
    Model to track OpenAI file uploads and their metadata.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    openai_file_id = models.CharField(max_length=255, unique=True)
    filename = models.CharField(max_length=255)
    purpose = models.CharField(max_length=50, choices=[
        ('assistants', 'Assistants'),
        ('fine-tune', 'Fine-Tuning'),
        ('vision', 'Vision'),
        ('user_data', 'User Data')
    ], default='assistants')
    bytes_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} ({self.openai_file_id})"


class OpenAIThread(models.Model):
    """
    Model to track OpenAI threads related to conversations.
    """
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='openai_thread')
    thread_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Thread {self.thread_id} for {self.conversation}"


class MessageOpenAIFile(models.Model):
    """
    Model to associate Messages with OpenAI files.
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='openai_files')
    openai_file = models.ForeignKey(OpenAIFile, on_delete=models.CASCADE, related_name='message_links')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'openai_file')
    
    def __str__(self):
        return f"Link between {self.message} and {self.openai_file}"
