import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class AITool(models.Model):
    class Category(models.TextChoices):
        TRANSCRIPTION = 'Transcription', _('Transcription')
        IMAGE_GENERATOR = 'Image Generator', _('Image Generator')
        WORD_PROCESSOR = 'Word Processor', _('Word Processor')
        OTHER = 'Other', _('Other')
    
    # Fields
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_("Unique identifier for the AI tool")
    )
    
    name = models.CharField(
        max_length=255,
        help_text=_("Name of the AI tool"),
        db_index=True  # Add index for better query performance
    )
    
    provider = models.CharField(
        max_length=255,
        help_text=_("Provider or company that created the AI tool"),
        db_index=True  # Add index for better query performance
    )
    
    endpoint = models.URLField(
        validators=[URLValidator()],
        help_text=_("URL of the AI service")
    )
    
    category = models.CharField(
        max_length=100,
        choices=Category.choices,
        default=Category.OTHER,
        help_text=_("Category of the AI tool"),
        db_index=True  # Add index for better filtering
    )
    
    description = models.TextField(
        help_text=_("Detailed description of the AI tool")
    )
    
    popularity = models.IntegerField(
        validators=[
            MinValueValidator(0, message=_("Popularity must be at least 0")),
            MaxValueValidator(100, message=_("Popularity cannot exceed 100"))
        ],
        help_text=_("Popularity rating from 0 to 100")
    )
    
    image = models.ImageField(
        upload_to='ai_images/', 
        null=True, 
        blank=True,
        help_text=_("Image representing the AI tool")
    )
    
    # Meta information
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text=_("Date and time when this record was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Date and time when this record was last updated")
    )
    
    # Methods
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of the model."""
        from django.urls import reverse
        return reverse('presentationAI', args=[str(self.id)])
    
    class Meta:
        ordering = ['-popularity', 'name']  # Default ordering by popularity (desc) then name
        verbose_name = _("AI Tool")
        verbose_name_plural = _("AI Tools")
