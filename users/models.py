from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom user model for InspireAI.
    
    Extends the default Django user model to add additional fields.
    """
    
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Use email instead of username for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
