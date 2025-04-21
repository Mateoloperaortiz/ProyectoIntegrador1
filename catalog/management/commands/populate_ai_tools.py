import os
import tempfile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from catalog.models import AITool
from catalog.constants import CATEGORY_CHOICES, API_TYPE_CHOICES


class Command(BaseCommand):
    help = 'Populates the database with AI tools from OpenAI, Hugging Face, and Google Gemini'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Number of AI tools to create (default: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing AI tools before creating new ones'
        )
    
    def get_svg_file(self, logo_name, tool_name, field_type="logo"):
        """
        Loads an SVG logo file and returns a File object
        """
        try:
            logo_path = os.path.join('static', 'images', logo_name)
            
            if not os.path.exists(logo_path):
                self.stdout.write(self.style.WARNING(f"Logo file not found: {logo_path}"))
                return None
                
            with open(logo_path, 'rb') as f:
                img_temp = tempfile.NamedTemporaryFile(delete=True)
                img_temp.write(f.read())
                img_temp.flush()
                img_temp.seek(0)
                
                return File(img_temp, name=f"{slugify(tool_name)}_{field_type}.svg")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading SVG file: {e}"))
            return None

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing AI tools...')
            AITool.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared all AI tools'))

        count = options['count']
        self.stdout.write(f'Creating AI tools from OpenAI, Hugging Face, and Google Gemini...')

        # Only ChatGPT and Gemini tools, both multimodal
        ai_tools_data = [
            {
                'name': 'ChatGPT',
                'description': 'ChatGPT is an AI-powered chatbot developed by OpenAI, based on the GPT family. It supports multimodal input and output, including text and images.',
                'provider': 'OpenAI',
                'website_url': 'https://chat.openai.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'OPENAI',
                'api_model': 'gpt-4o',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                'logo_filename': 'openai-svgrepo-com.svg',
            },
            {
                'name': 'Gemini',
                'description': "Gemini is Google's most advanced multimodal AI model, supporting chat, image, and code understanding.",
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-pro-vision',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent',
                'logo_filename': 'Google_Gemini_logo.svg',
            }
        ]

        # Create AI tools from the sample data
        created_count = 0
        for tool_data in ai_tools_data:
            if created_count >= count:
                break
                
            # Check if tool already exists by name
            if not AITool.objects.filter(name=tool_data['name']).exists():
                # Create slug from name if not provided
                if 'slug' not in tool_data:
                    tool_data['slug'] = slugify(tool_data['name'])
                
                # Get the SVG file
                logo_filename = tool_data.pop('logo_filename', None)
                
                try:
                    # Create the AI tool without images first
                    tool = AITool.objects.create(**tool_data)
                    
                    if logo_filename:
                        self.stdout.write(f"Loading SVG for {tool_data['name']}...")
                        
                        # Use same SVG file for both logo and image
                        logo_file = self.get_svg_file(logo_filename, tool_data['name'], "logo")
                        if logo_file:
                            tool.logo = logo_file
                            
                        image_file = self.get_svg_file(logo_filename, tool_data['name'], "image")
                        if image_file:
                            tool.image = image_file
                            
                        tool.save()
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created AI tool: {tool_data['name']}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating {tool_data['name']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} AI tools'))
