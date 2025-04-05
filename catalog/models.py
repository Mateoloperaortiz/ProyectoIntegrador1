from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from catalog.constants import CATEGORY_CHOICES, API_TYPE_CHOICES, RATING_CHOICES
import uuid
from django.db.models import Avg



class AITool(models.Model):
    """
    Model representing an AI tool in the catalog.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True) 
    description = models.TextField()
    provider = models.CharField(max_length=100)
    website_url = models.URLField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='tool_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    popularity = models.FloatField(default=0)     

    # API integration fields
    api_type = models.CharField(max_length=20, choices=API_TYPE_CHOICES, default='NONE')
    api_endpoint = models.CharField(max_length=255, blank=True, null=True)
    api_model = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-popularity', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:tool_detail', kwargs={'slug': self.slug})
    
    def get_average_rating(self):
        """Calculate and update the average rating for this tool."""
        avg = self.ratings.aggregate(Avg('stars'))['stars__avg']
        # Update popularity with the average rating
        self.popularity = round(avg or 0, 2)
        self.save(update_fields=['popularity'])
        return self.popularity



class Rating(models.Model):
    """Model for storing user ratings and reviews."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE, related_name='ratings')
    stars = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tool')

    def __str__(self):
        return (
            f"Rating {self.id} - "
            f"User {self.user.username} - "
            f"Tool {self.tool.name} - "
            f"{self.stars}⭐ - "
            f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tool')

    def __str__(self):
        return f"{self.user.username} ❤️ {self.tool.name}"  
        
 