import os
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class GeminiIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gemini_integration'
    
    def ready(self):
        """
        Validate that the Gemini API key is present in environment variables.
        """
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ImproperlyConfigured(
                "GEMINI_API_KEY is not set in environment variables. "
                "Please add it to your .env file."
            )
        # Add any other startup validation as needed
