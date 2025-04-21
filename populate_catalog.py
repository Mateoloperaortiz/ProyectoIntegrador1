import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inspireai.settings')
django.setup()

from catalog.models import AITool
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def create_ai_tools():
    """Create sample AI tools for testing."""
    
    try:
        gemini_tool = AITool.objects.create(
            name="Gemini Image Generator",
            description="Generate images using Google's Gemini API with Imagen 3 model.",
            provider="Google",
            website_url="https://ai.google.dev/",
            category="IMAGE",
            is_featured=True,
            api_type="GEMINI",
            api_model="gemini-2.0-flash-exp-image-generation",
            api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent"
        )
        print(f"Created Gemini Image Generator tool: {gemini_tool}")
    except IntegrityError:
        print("Gemini Image Generator tool already exists")
    
    try:
        gemini_chat = AITool.objects.create(
            name="Gemini Chat",
            description="Chat with Google's Gemini AI model.",
            provider="Google",
            website_url="https://ai.google.dev/",
            category="CHAT",
            is_featured=True,
            api_type="GEMINI",
            api_model="gemini-2.0-flash",
            api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        )
        print(f"Created Gemini Chat tool: {gemini_chat}")
    except IntegrityError:
        print("Gemini Chat tool already exists")
    
    try:
        openai_tool = AITool.objects.create(
            name="GPT-4 Chat",
            description="Chat with OpenAI's GPT-4 model.",
            provider="OpenAI",
            website_url="https://openai.com/",
            category="CHAT",
            is_featured=True,
            api_type="OPENAI",
            api_model="gpt-4",
            api_endpoint="https://api.openai.com/v1/chat/completions"
        )
        print(f"Created OpenAI GPT-4 tool: {openai_tool}")
    except IntegrityError:
        print("OpenAI GPT-4 tool already exists")

if __name__ == "__main__":
    print("Populating catalog with AI tools...")
    create_ai_tools()
    print("Done!")
