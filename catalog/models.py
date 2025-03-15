from django.db import models
from django.conf import settings
from django.db.models import Avg
from core.models import UUIDModel, TimeStampedModel

class AITool(UUIDModel, TimeStampedModel):
    """
    Model representing an AI tool available in the catalog.
    
    This model inherits from UUIDModel for UUID primary key and 
    TimeStampedModel for created_at and updated_at fields.
    """
    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    endpoint = models.URLField()
    category = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='ai_images/', null=True, blank=True)
    popularity = models.FloatField(default=0)
    
    # API integration fields
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

    def __str__(self):
        return self.name

class Rating(UUIDModel, TimeStampedModel):
    """
    Model for storing user ratings and reviews.
    
    This model inherits from UUIDModel for UUID primary key and 
    TimeStampedModel for created_at and updated_at fields.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        related_name='ai_ratings'
    )
    ai_tool = models.ForeignKey(
        'catalog.AITool',  
        on_delete=models.CASCADE,
        related_name="ratings"
    )
    stars = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    comment = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Save rating and update AI tool popularity"""
        super().save(*args, **kwargs)
        # Update popularity directly
        avg = self.ai_tool.ratings.aggregate(Avg('stars'))['stars__avg']
        self.ai_tool.popularity = round(avg, 2) if avg else 0
        self.ai_tool.save(update_fields=['popularity'])

    class Meta:
        unique_together = ('user', 'ai_tool')

    def __str__(self):
        return (
            f"Rating {self.id} - "
            f"User: {self.user.id} ({self.user.email}) - "
            f"Tool: {self.ai_tool.id} ({self.ai_tool.name}) - "
            f"{self.stars}⭐ - "
            f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )