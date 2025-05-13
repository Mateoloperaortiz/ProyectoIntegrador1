from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Users')

    def ready(self):
        # Import posthog and settings here to avoid circular imports
        # and ensure settings are loaded.
        from django.conf import settings
        import posthog

        if settings.POSTHOG_API_KEY:
            posthog.api_key = settings.POSTHOG_API_KEY
            posthog.host = settings.POSTHOG_HOST
            if hasattr(settings, 'POSTHOG_DEBUG'):
                posthog.debug = settings.POSTHOG_DEBUG
            
            # Optional: Disable PostHog during tests
            # if getattr(settings, 'TESTING', False): # Assuming you have a TESTING setting
            #     posthog.disabled = True
            
            print(f"PostHog initialized in UsersConfig. API Key: {posthog.api_key[:7]}..., Host: {posthog.host}")
        else:
            print("PostHog API Key not found in settings. PostHog not initialized.")
