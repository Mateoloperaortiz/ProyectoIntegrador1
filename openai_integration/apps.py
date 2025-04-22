from django.apps import AppConfig


class OpenaiIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'openai_integration'
    
    def ready(self):
        # Validate OpenAI environment variables on startup
        import os
        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_VERSION',
            'AZURE_OPENAI_DEPLOYMENT'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            import warnings
            warnings.warn(f"Missing required Azure OpenAI environment variables: {', '.join(missing_vars)}")
