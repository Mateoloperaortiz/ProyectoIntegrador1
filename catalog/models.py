from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from catalog.constants import CATEGORY_CHOICES, API_TYPE_CHOICES, RATING_CHOICES
import uuid

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
    popularity = models.IntegerField(default=0)  # Number of views/interactions
    
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
        ratings = self.rating_set.all()
        if ratings:
            return sum(r.stars for r in ratings) / len(ratings)
        return 0


class Rating(models.Model):
    """
    Model representing user ratings for AI tools.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=RATING_CHOICES)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'tool')  # One rating per user per tool
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.stars} stars for {self.tool.name}"
