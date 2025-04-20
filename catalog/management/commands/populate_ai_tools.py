import random
import requests
import os
import tempfile
from io import BytesIO
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from catalog.models import AITool
from catalog.constants import CATEGORY_CHOICES, API_TYPE_CHOICES
from PIL import Image


class Command(BaseCommand):
    help = 'Populates the database with sample AI tools from OpenAI, Hugging Face, and Google'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of AI tools to create (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing AI tools before creating new ones'
        )
        
    def fetch_and_save_image(self, url, tool_name, is_logo=False):
        """
        Fetch image from URL, process it, and return a File object.
        Falls back to a default image if fetching fails.
        """
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            if response.status_code == 200:
                img_temp = tempfile.NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                
                try:
                    img = Image.open(BytesIO(response.content))
                    
                    if is_logo:
                        if max(img.size) > 400:
                            img.thumbnail((400, 400))
                    else:
                        if max(img.size) > 800:
                            img.thumbnail((800, 800))
                    
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                        img = background
                    
                    img.save(img_temp, format='JPEG')
                    img_temp.seek(0)
                    
                    return File(img_temp, name=f"{slugify(tool_name)}.jpg")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing image for {tool_name}: {e}"))
                    return self.get_default_image(is_logo)
            else:
                self.stdout.write(self.style.WARNING(f"Failed to fetch image for {tool_name}: HTTP {response.status_code}"))
                return self.get_default_image(is_logo)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error fetching image for {tool_name}: {e}"))
            return self.get_default_image(is_logo)
            
    def get_default_image(self, is_logo=False):
        """
        Return a default image file when fetching fails
        """
        try:
            default_path = os.path.join('static', 'images', 'default-logo.png' if is_logo else 'default-tool.png')
            
            if not os.path.exists(default_path):
                default_path = os.path.join('static', 'images', 'icon.png')
                
            with open(default_path, 'rb') as f:
                img_temp = tempfile.NamedTemporaryFile(delete=True)
                img_temp.write(f.read())
                img_temp.flush()
                img_temp.seek(0)
                
                return File(img_temp, name=os.path.basename(default_path))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading default image: {e}"))
            return None

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing AI tools...')
            AITool.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared all AI tools'))

        count = options['count']
        self.stdout.write(f'Creating AI tools from OpenAI, Hugging Face, and Google...')

        # List of sample AI tools with realistic data - only OpenAI, Hugging Face, and Google
        ai_tools_data = [
            {
                'name': 'ChatGPT',
                'description': 'ChatGPT is an AI-powered chatbot developed by OpenAI, based on the GPT (Generative Pre-trained Transformer) family of large language models. It is designed to understand and generate human-like text based on the input it receives.',
                'provider': 'OpenAI',
                'website_url': 'https://chat.openai.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'OPENAI',
                'api_model': 'gpt-4',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/1200px-ChatGPT_logo.svg.png',
                'image_url': 'https://cdn.vox-cdn.com/thumbor/K_8RrfZgm8wAKQIjTX_5arDMJ98=/0x0:2040x1360/1400x1400/filters:focal(1020x680:1021x681)/cdn.vox-cdn.com/uploads/chorus_asset/file/24247717/STK_AI_Verge_005.jpg',
            },
            {
                'name': 'DALL-E 3',
                'description': 'DALL-E 3 is an AI system that can create realistic images and art from a description in natural language. The third iteration of DALL-E features significantly improved image quality, better text rendering, and more accurate responses to prompts.',
                'provider': 'OpenAI',
                'website_url': 'https://openai.com/dall-e-3',
                'category': 'IMAGE',
                'is_featured': True,
                'api_type': 'OPENAI',
                'api_model': 'dall-e-3',
                'api_endpoint': 'https://api.openai.com/v1/images/generations',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/OpenAI_Logo.svg/1200px-OpenAI_Logo.svg.png',
                'image_url': 'https://cdn.openai.com/dall-e-3/prompt-examples/v2/astronaut_riding_a_horse.webp',
            },
            {
                'name': 'GPT-4',
                'description': 'GPT-4 is OpenAI\'s most advanced system, producing safer and more useful responses. GPT-4 can solve difficult problems with greater accuracy, thanks to its broader general knowledge and problem solving abilities.',
                'provider': 'OpenAI',
                'website_url': 'https://openai.com/gpt-4',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'OPENAI',
                'api_model': 'gpt-4',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/OpenAI_Logo.svg/1200px-OpenAI_Logo.svg.png',
                'image_url': 'https://cdn.openai.com/research-covers/gpt-4/GPT-4-still.jpg',
            },
            {
                'name': 'Whisper',
                'description': 'Whisper is an automatic speech recognition (ASR) system trained on 680,000 hours of multilingual and multitask supervised data. It can transcribe speech in multiple languages and translate it to English.',
                'provider': 'OpenAI',
                'website_url': 'https://openai.com/research/whisper',
                'category': 'AUDIO',
                'is_featured': True,
                'api_type': 'OPENAI',
                'api_model': 'whisper-1',
                'api_endpoint': 'https://api.openai.com/v1/audio/transcriptions',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/OpenAI_Logo.svg/1200px-OpenAI_Logo.svg.png',
                'image_url': 'https://cdn.openai.com/research-covers/whisper/3.jpg',
            },
            {
                'name': 'Hugging Face Transformers',
                'description': 'Hugging Face Transformers provides thousands of pre-trained models for natural language understanding (NLU) and generation (NLG), computer vision, and audio processing tasks. It\'s an open-source library that democratizes access to state-of-the-art AI models.',
                'provider': 'Hugging Face',
                'website_url': 'https://huggingface.co/transformers/',
                'category': 'OTHER',
                'is_featured': True,
                'api_type': 'HUGGINGFACE',
                'api_model': None,
                'api_endpoint': 'https://api-inference.huggingface.co/models/',
                'logo_url': 'https://huggingface.co/front/assets/huggingface_logo.svg',
                'image_url': 'https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/transformers-logo.png',
            },
            {
                'name': 'Stable Diffusion XL',
                'description': 'Stable Diffusion XL is a deep learning, text-to-image model released by Stability AI. It is primarily used to generate detailed images conditioned on text descriptions, with significantly improved quality over previous versions.',
                'provider': 'Stability AI via Hugging Face',
                'website_url': 'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0',
                'category': 'IMAGE',
                'is_featured': True,
                'api_type': 'HUGGINGFACE',
                'api_model': 'stabilityai/stable-diffusion-xl-base-1.0',
                'api_endpoint': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0',
                'logo_url': 'https://huggingface.co/front/assets/huggingface_logo.svg',
                'image_url': 'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/example_1.png',
            },
            {
                'name': 'BERT',
                'description': 'BERT (Bidirectional Encoder Representations from Transformers) is a transformer-based machine learning technique for natural language processing pre-training developed by Google and hosted on Hugging Face.',
                'provider': 'Google via Hugging Face',
                'website_url': 'https://huggingface.co/bert-base-uncased',
                'category': 'TEXT',
                'is_featured': False,
                'api_type': 'HUGGINGFACE',
                'api_model': 'bert-base-uncased',
                'api_endpoint': 'https://api-inference.huggingface.co/models/bert-base-uncased',
                'logo_url': 'https://huggingface.co/front/assets/huggingface_logo.svg',
                'image_url': 'https://miro.medium.com/v2/resize:fit:1400/1*wBhpIfrVCgPFcJj-lZKqMQ.png',
            },
            {
                'name': 'Gemini Pro',
                'description': 'Gemini Pro is Google\'s largest and most capable AI model, designed to be multimodal from the ground up. It can understand virtually any input, from text and code to audio and images, and generate high-quality outputs.',
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-pro',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
                'logo_url': 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/gemini_1.max-1000x1000.png',
                'image_url': 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Gemini_Inline_1.max-1300x1300.jpg',
            },
            {
                'name': 'Gemini Vision',
                'description': 'Gemini Vision is Google\'s multimodal AI model that can analyze and understand images along with text. It can process visual information and provide detailed descriptions, analysis, and answers to questions about images.',
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'IMAGE',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-pro-vision',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent',
                'logo_url': 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/gemini_1.max-1000x1000.png',
                'image_url': 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Gemini_Inline_2.max-1300x1300.jpg',
            },
            {
                'name': 'Gemini Code',
                'description': 'Gemini Code is specialized for code generation, understanding, and explanation. It can help developers write code, debug issues, and understand complex codebases across multiple programming languages.',
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'CODE',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-pro',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
                'logo_url': 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/gemini_1.max-1000x1000.png',
                'image_url': 'https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Gemini_Inline_3.max-1300x1300.jpg',
            },
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
                
                logo_url = tool_data.pop('logo_url', None)
                image_url = tool_data.pop('image_url', None)
                
                try:
                    # Create the AI tool without images first
                    tool = AITool.objects.create(**tool_data)
                    
                    if logo_url:
                        self.stdout.write(f"Fetching logo for {tool_data['name']}...")
                        logo_file = self.fetch_and_save_image(logo_url, f"{tool_data['name']}_logo", is_logo=True)
                        if logo_file:
                            tool.logo = logo_file
                            tool.save(update_fields=['logo'])
                    
                    if image_url:
                        self.stdout.write(f"Fetching image for {tool_data['name']}...")
                        image_file = self.fetch_and_save_image(image_url, f"{tool_data['name']}_image", is_logo=False)
                        if image_file:
                            tool.image = image_file
                            tool.save(update_fields=['image'])
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created AI tool: {tool_data['name']}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating {tool_data['name']}: {e}"))
        
        # If we need more tools to reach the requested count, create random ones
        categories = [c[0] for c in CATEGORY_CHOICES]
        api_types = [c[0] for c in API_TYPE_CHOICES]
        
        while created_count < count:
            # Generate a random tool name
            random_name = f"AI Tool {created_count + 1}"
            
            # Skip if a tool with this name already exists
            if AITool.objects.filter(name=random_name).exists():
                continue
                
            # Create random tool data
            random_category = random.choice(categories)
            random_api_type = random.choice(api_types)
            
            # Get category display name safely
            category_dict = dict(CATEGORY_CHOICES)
            category_display = category_dict.get(random_category, "Unknown Category")
            
            random_tool = {
                'name': random_name,
                'slug': slugify(random_name),  # Ensure slug is set
                'description': f"This is a sample AI tool for {category_display}.",
                'provider': f"Provider {created_count + 1}",
                'website_url': f"https://example.com/tool{created_count + 1}",
                'category': random_category,
                'is_featured': random.choice([True, False]),
                'api_type': random_api_type,
                'api_model': f"model-{created_count + 1}" if random_api_type != 'NONE' else None,
                'api_endpoint': f"https://api.example.com/v1/{random_name.lower().replace(' ', '-')}" if random_api_type != 'NONE' else None,
            }
            
            try:
                # Create the AI tool
                AITool.objects.create(**random_tool)
                created_count += 1
                self.stdout.write(f"Created random AI tool: {random_tool['name']}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating random tool {random_tool['name']}: {e}"))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} AI tools'))
