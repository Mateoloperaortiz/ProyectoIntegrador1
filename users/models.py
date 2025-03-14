import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import List, Union, Optional

class CustomUser(AbstractUser):
    # Use CharField instead of UUIDField to support both UUID and integer IDs
    # This allows existing users with integer IDs to continue working
    # while new users will get UUID IDs
    id = models.CharField(primary_key=True, max_length=36, editable=False)
    email = models.EmailField(unique=True, help_text="User email")
    first_name = models.CharField(max_length=255, help_text="User first name")
    bio = models.TextField(blank=True, max_length=500, help_text="User biography")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )

    favorites = models.ManyToManyField(
        'catalog.AITool',
        related_name='favorited_by',
        blank=True,  # Allows the field to be empty
        help_text="User's favorite AI tools"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    def __str__(self) -> str:
        return self.email
        
    def save(self, *args, **kwargs):
        # Generate a UUID for new users (if ID is not set)
        if not self.id:
            self.id = str(uuid.uuid4())
        super().save(*args, **kwargs)