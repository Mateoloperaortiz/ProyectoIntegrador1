import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import AITool
from catalog.constants import CATEGORY_CHOICES, API_TYPE_CHOICES


class Command(BaseCommand):
    help = 'Populates the database with sample AI tools'

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

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing AI tools...')
            AITool.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleared all AI tools'))

        count = options['count']
        self.stdout.write(f'Creating {count} AI tools...')

        # List of sample AI tools with realistic data
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
            },
            {
                'name': 'Midjourney',
                'description': 'Midjourney is an AI program that generates images from textual descriptions, similar to OpenAI\'s DALL-E and Stable Diffusion. The tool is currently in open beta and is known for its artistic style and high-quality outputs.',
                'provider': 'Midjourney, Inc.',
                'website_url': 'https://www.midjourney.com/',
                'category': 'IMAGE',
                'is_featured': True,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Claude',
                'description': 'Claude is an AI assistant created by Anthropic to be helpful, harmless, and honest. It excels at thoughtful dialogue and creative content generation with a focus on safety and ethical considerations.',
                'provider': 'Anthropic',
                'website_url': 'https://www.anthropic.com/claude',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'ANTHROPIC',
                'api_model': 'claude-3-opus',
                'api_endpoint': 'https://api.anthropic.com/v1/messages',
            },
            {
                'name': 'GitHub Copilot',
                'description': 'GitHub Copilot is an AI pair programmer that offers autocomplete-style suggestions as you code. It helps developers write code faster and with less work by suggesting whole lines or blocks of code as you type.',
                'provider': 'GitHub & OpenAI',
                'website_url': 'https://github.com/features/copilot',
                'category': 'CODE',
                'is_featured': True,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Gemini',
                'description': 'Gemini is Google\'s largest and most capable AI model, designed to be multimodal from the ground up. It can understand virtually any input, from text and code to audio and images, and generate high-quality outputs.',
                'provider': 'Google',
                'website_url': 'https://gemini.google.com/',
                'category': 'CHAT',
                'is_featured': True,
                'api_type': 'GOOGLE',
                'api_model': 'gemini-pro',
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            },
            {
                'name': 'Stable Diffusion',
                'description': 'Stable Diffusion is a deep learning, text-to-image model released in 2022. It is primarily used to generate detailed images conditioned on text descriptions, though it can also be applied to other tasks such as inpainting and outpainting.',
                'provider': 'Stability AI',
                'website_url': 'https://stability.ai/',
                'category': 'IMAGE',
                'is_featured': True,
                'api_type': 'HUGGINGFACE',
                'api_model': 'stabilityai/stable-diffusion-xl-base-1.0',
                'api_endpoint': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0',
            },
            {
                'name': 'Perplexity AI',
                'description': 'Perplexity AI is an AI-powered search engine and answer engine that provides direct responses to questions by searching the web and citing sources. It combines the capabilities of large language models with real-time web search.',
                'provider': 'Perplexity Labs',
                'website_url': 'https://www.perplexity.ai/',
                'category': 'SEARCH',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Whisper',
                'description': 'Whisper is an automatic speech recognition (ASR) system trained on 680,000 hours of multilingual and multitask supervised data. It can transcribe speech in multiple languages and translate it to English.',
                'provider': 'OpenAI',
                'website_url': 'https://openai.com/research/whisper',
                'category': 'AUDIO',
                'is_featured': False,
                'api_type': 'OPENAI',
                'api_model': 'whisper-1',
                'api_endpoint': 'https://api.openai.com/v1/audio/transcriptions',
            },
            {
                'name': 'Runway Gen-2',
                'description': 'Runway Gen-2 is a text-to-video AI model that can generate novel video content from text descriptions, existing images, or even other videos. It\'s designed for creative professionals in film, advertising, and digital media.',
                'provider': 'Runway AI',
                'website_url': 'https://runwayml.com/',
                'category': 'VIDEO',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'DeepL',
                'description': 'DeepL is a neural machine translation service that translates between different languages. It\'s known for producing more natural-sounding translations compared to other services, especially for European languages.',
                'provider': 'DeepL GmbH',
                'website_url': 'https://www.deepl.com/',
                'category': 'TRANS',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': 'https://api.deepl.com/v2/translate',
            },
            {
                'name': 'Hugging Face Transformers',
                'description': 'Hugging Face Transformers provides thousands of pre-trained models for natural language understanding (NLU) and generation (NLG), computer vision, and audio processing tasks. It\'s an open-source library that democratizes access to state-of-the-art AI models.',
                'provider': 'Hugging Face',
                'website_url': 'https://huggingface.co/transformers/',
                'category': 'OTHER',
                'is_featured': False,
                'api_type': 'HUGGINGFACE',
                'api_model': None,
                'api_endpoint': 'https://api-inference.huggingface.co/models/',
            },
            {
                'name': 'Suno AI',
                'description': 'Suno AI is a music generation platform that can create original songs from text prompts. It can generate vocals, instruments, and full compositions in various styles and genres.',
                'provider': 'Suno',
                'website_url': 'https://suno.ai/',
                'category': 'AUDIO',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Otter.ai',
                'description': 'Otter.ai is an AI-powered transcription and note-taking app that records audio, transcribes it in real-time, and makes it searchable. It\'s designed for meetings, interviews, lectures, and other spoken content.',
                'provider': 'Otter.ai',
                'website_url': 'https://otter.ai/',
                'category': 'AUDIO',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Codeium',
                'description': 'Codeium is an AI-powered coding assistant that provides code completions, explanations, and refactoring suggestions. It supports over 70 programming languages and integrates with popular IDEs and text editors.',
                'provider': 'Codeium',
                'website_url': 'https://codeium.com/',
                'category': 'CODE',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Elicit',
                'description': 'Elicit is an AI research assistant that helps researchers find and understand scientific papers. It can search for papers, extract key information, summarize findings, and answer questions about research.',
                'provider': 'Ought',
                'website_url': 'https://elicit.org/',
                'category': 'SEARCH',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Synthesia',
                'description': 'Synthesia is an AI video generation platform that creates videos with virtual presenters. Users can select from a variety of AI avatars and have them speak any script in over 120 languages.',
                'provider': 'Synthesia',
                'website_url': 'https://www.synthesia.io/',
                'category': 'VIDEO',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Notion AI',
                'description': 'Notion AI is an AI writing assistant integrated into the Notion workspace. It can draft content, summarize text, improve writing, translate languages, and answer questions based on your workspace content.',
                'provider': 'Notion Labs',
                'website_url': 'https://www.notion.so/product/ai',
                'category': 'TEXT',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Jasper',
                'description': 'Jasper is an AI content platform designed for marketing teams. It can generate blog posts, social media content, emails, and other marketing copy based on brief descriptions or templates.',
                'provider': 'Jasper',
                'website_url': 'https://www.jasper.ai/',
                'category': 'TEXT',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
            },
            {
                'name': 'Descript',
                'description': 'Descript is an all-in-one audio and video editing platform with AI-powered features like automatic transcription, text-based editing, and voice cloning. It allows users to edit audio and video as easily as editing a text document.',
                'provider': 'Descript',
                'website_url': 'https://www.descript.com/',
                'category': 'AUDIO',
                'is_featured': False,
                'api_type': 'CUSTOM',
                'api_model': None,
                'api_endpoint': None,
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
                    
                # Create the AI tool
                AITool.objects.create(**tool_data)
                created_count += 1
                self.stdout.write(f"Created AI tool: {tool_data['name']}")
        
        # If we need more tools to reach the requested count, create random ones
        categories = [choice[0] for choice in CATEGORY_CHOICES]
        api_types = [choice[0] for choice in API_TYPE_CHOICES]
        
        while created_count < count:
            # Generate a random tool name
            random_name = f"AI Tool {created_count + 1}"
            
            # Skip if a tool with this name already exists
            if AITool.objects.filter(name=random_name).exists():
                continue
                
            # Create random tool data
            random_category = random.choice(categories)
            random_api_type = random.choice(api_types)
            
            random_tool = {
                'name': random_name,
                'description': f"This is a sample AI tool for {dict(CATEGORY_CHOICES).get(random_category)}.",
                'provider': f"Provider {created_count + 1}",
                'website_url': f"https://example.com/tool{created_count + 1}",
                'category': random_category,
                'is_featured': random.choice([True, False]),
                'api_type': random_api_type,
                'api_model': f"model-{created_count + 1}" if random_api_type != 'NONE' else None,
                'api_endpoint': f"https://api.example.com/v1/{random_name.lower().replace(' ', '-')}" if random_api_type != 'NONE' else None,
            }
            
            # Create the AI tool
            AITool.objects.create(**random_tool)
            created_count += 1
            self.stdout.write(f"Created random AI tool: {random_tool['name']}")
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} AI tools'))
