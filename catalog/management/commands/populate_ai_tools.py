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

        # List of AI tools with realistic data - only OpenAI, Hugging Face, and Google
        ai_tools_data = [
            # OpenAI Tools
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
                'logo_filename': 'openai-svgrepo-com.svg',
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
                'logo_filename': 'openai-svgrepo-com.svg',
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
                'logo_filename': 'openai-svgrepo-com.svg',
            },
            {
                'name': 'GPT-4o',
                'description': 'GPT-4o ("o" for "omni") is OpenAI\'s most advanced, fastest, and most affordable model offering human-level performance on a wide variety of tasks. It brings similar capabilities as GPT-4 Turbo but runs significantly faster.',
                'provider': 'OpenAI',
                'website_url': 'https://openai.com/index/gpt-4o/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'OPENAI',
                'api_model': 'gpt-4o',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                'logo_filename': 'openai-svgrepo-com.svg',
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
                'logo_filename': 'openai-svgrepo-com.svg',
            },
            
            # Hugging Face Tools
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
                'logo_filename': 'hf-logo-with-title.svg',
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
                'logo_filename': 'hf-logo-with-title.svg',
            },
            {
                'name': 'Llama 3',
                'description': 'Llama 3 is an open source large language model developed by Meta and available via Hugging Face. It performs well across benchmarks, excels at coding, and supports multilingual capabilities.',
                'provider': 'Meta via Hugging Face',
                'website_url': 'https://huggingface.co/meta-llama/Meta-Llama-3-8B',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'HUGGINGFACE',
                'api_model': 'meta-llama/Meta-Llama-3-8B',
                'api_endpoint': 'https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B',
                'logo_filename': 'hf-logo-with-title.svg',
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
                'logo_filename': 'hf-logo-with-title.svg',
            },
            {
                'name': 'Mistral',
                'description': 'Mistral is a family of state-of-the-art language models that deliver excellent performance while being efficient to deploy. It performs particularly well in reasoning and coding tasks.',
                'provider': 'Mistral AI via Hugging Face',
                'website_url': 'https://huggingface.co/mistralai/Mistral-7B-v0.1',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'HUGGINGFACE',
                'api_model': 'mistralai/Mistral-7B-v0.1',
                'api_endpoint': 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-v0.1',
                'logo_filename': 'hf-logo-with-title.svg',
            },
            
            # Google Gemini Tools
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
                'logo_filename': 'Google_Gemini_logo.svg',
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
                'logo_filename': 'Google_Gemini_logo.svg',
            },
            {
                'name': 'Gemini 1.5 Pro',
                'description': 'Gemini 1.5 Pro is the latest version of Google\'s Gemini model offering a massive 1 million token context window, advanced multimodal capabilities, and improved performance across a wide range of tasks.',
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-1.5-pro',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent',
                'logo_filename': 'Google_Gemini_logo.svg',
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
                'logo_filename': 'Google_Gemini_logo.svg',
            },
            {
                'name': 'Gemini Ultra',
                'description': 'Gemini Ultra is Google\'s most capable AI model, surpassing human experts on MMLU and showing superior performance on text, image, audio, and video understanding tasks. It represents Google\'s most advanced multimodal AI.',
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-ultra',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-ultra:generateContent',
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
