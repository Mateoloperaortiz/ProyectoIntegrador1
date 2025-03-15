from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InteractionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interaction'
    verbose_name = _('AI Interactions')
