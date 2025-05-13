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
        The 'field_type' parameter is less relevant now if we use original filenames.
        """
        try:
            # Path to the source images in your static directory
            logo_path = os.path.join('static', 'images', logo_name)
            
            if not os.path.exists(logo_path):
                self.stdout.write(self.style.WARNING(f"Source logo file not found: {logo_path}"))
                return None
                
            # Read the original file content
            with open(logo_path, 'rb') as f_original:
                file_content = f_original.read()

            # Create a temporary file to hold the content for Django's File object
            img_temp = tempfile.NamedTemporaryFile(delete=True)
            img_temp.write(file_content)
            img_temp.flush() # Ensure all data is written
            img_temp.seek(0) # Rewind to the beginning of the temporary file
                
            # Return a Django File object using the original filename (logo_name)
            # This name will be used when saving to DigitalOcean Spaces.
            return File(img_temp, name=logo_name) 
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading SVG file {logo_name}: {e}"))
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
                'api_type': 'GEMINI',
                'api_model': 'gemini-1.5-flash',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent',
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
                        self.stdout.write(f"Processing logo {logo_filename} for {tool_data['name']}...")
                        
                        # Get the Django File object for the logo
                        # We'll use the original logo_filename as the name for storage
                        logo_file_obj = self.get_svg_file(logo_filename, tool_data['name'], "logo")
                        
                        if logo_file_obj:
                            tool.logo = logo_file_obj # Assign to the logo field
                            # tool.image = logo_file_obj # If you want the same image for the 'image' field
                                                     # Otherwise, handle tool.image separately if it's for a different image.
                            tool.save() # This will trigger the upload to Spaces via django-storages
                            self.stdout.write(self.style.SUCCESS(f"Successfully processed and assigned logo for {tool_data['name']}."))
                        else:
                            self.stdout.write(self.style.WARNING(f"Could not load logo file for {tool_data['name']}. Skipping logo assignment."))
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created AI tool: {tool_data['name']}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating {tool_data['name']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} AI tools'))
