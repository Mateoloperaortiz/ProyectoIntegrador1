from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom user model for InspireAI.
    """
    
    email = models.EmailField(_('email address'), unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Cambiar el campo de autenticación a email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
