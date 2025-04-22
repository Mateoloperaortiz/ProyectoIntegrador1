from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import json
import random
import os
import requests
import io
import base64
from openai import AzureOpenAI
import google.genai as genai
from google.genai import types
from PIL import Image

from .models import Conversation, Message, Favorite
from .forms import MessageForm, ConversationTitleForm
from catalog.models import AITool

@login_required
def toggle_favorite(request, tool_id):
    """
    Toggle favorite status for an AI tool.
    """
    tool = get_object_or_404(AITool, id=tool_id)
    
    # Check if already favorited
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        tool=tool
    )
    
    # If not created, it already exists, so delete it
    if not created:
        favorite.delete()
        is_favorite = False
        message = _('Removed from favorites')
    else:
        is_favorite = True
        message = _('Added to favorites')
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': is_favorite,
            'message': message
        })
    
    # If regular request, redirect back
    messages.success(request, message)
    return redirect('catalog:tool_detail', slug=tool.slug)


class ConversationListView(LoginRequiredMixin, ListView):
    """
    View for listing user's conversations.
    """
    model = Conversation
    template_name = 'interaction/conversation_list.html'
    context_object_name = 'conversations'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Conversation.objects.filter(user=self.request.user)
        
        # Filter by tool if requested
        tool_id = self.request.GET.get('tool')
        if tool_id:
            queryset = queryset.filter(tool_id=tool_id)
        
        # Filter by date range if requested
        date_range = self.request.GET.get('date_range')
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                queryset = queryset.filter(updated_at__date=today)
            elif date_range == 'week':
                week_ago = today - timezone.timedelta(days=7)
                queryset = queryset.filter(updated_at__date__gte=week_ago)
            elif date_range == 'month':
                month_ago = today - timezone.timedelta(days=30)
                queryset = queryset.filter(updated_at__date__gte=month_ago)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now()
        
        # Get all AI tools the user has conversations with for the filter dropdown
        user_conversation_tools = AITool.objects.filter(
            conversation__user=self.request.user
        ).distinct().order_by('name')
        context['user_tools'] = user_conversation_tools
        
        # Add filter parameters to context
        context['current_tool'] = self.request.GET.get('tool', '')
        context['current_date_range'] = self.request.GET.get('date_range', '')
        
        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a conversation.
    """
    model = Conversation
    template_name = 'interaction/conversation_detail.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the conversation object safely
        conversation = self.get_object()
        context['messages'] = Message.objects.filter(conversation=conversation)
        context['message_form'] = MessageForm()
        context['title_form'] = ConversationTitleForm(instance=conversation)
        return context


@login_required
def start_conversation(request, tool_id):
    """
    Start a new conversation with an AI tool.
    """
    tool = get_object_or_404(AITool, id=tool_id)
    
    conversation = Conversation.objects.create(
        user=request.user,
        tool=tool,
        title=f"Conversation with {tool.name}"
    )
    
    return redirect('interaction:conversation_detail', pk=conversation.id)


@login_required
def send_message(request, conversation_id):
    """
    Send a message in a conversation.
    NOTE: This view is primarily a fallback for non-JS/non-WebSocket scenarios or
          for API types that don't support streaming via the ChatConsumer yet.
          The main interaction for streaming APIs (OpenAI, Gemini) happens via WebSocket.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            user_content = form.cleaned_data['content']
            # Note: Image handling is NOT implemented in this fallback view.
            # It assumes text-only input for simplicity.
            user_message = Message.objects.create(
                conversation=conversation,
                is_from_user=True,
                content=user_content
            )
            
            # Generate AI response using the simulation/fallback function
            # This function handles dispatching to the correct non-streaming API call
            ai_response_content = simulate_ai_response(conversation.tool, user_content)
            
            ai_message = Message.objects.create(
                conversation=conversation,
                is_from_user=False,
                content=ai_response_content
            )
            
            conversation.save() # Update timestamp
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'user_message': {
                        'content': user_message.content,
                        'timestamp': user_message.timestamp.strftime('%b %d, %Y, %I:%M %p')
                    },
                    'ai_message': {
                        'content': ai_message.content,
                        'timestamp': ai_message.timestamp.strftime('%b %d, %Y, %I:%M %p')
                    }
                })
            
    # Redirect back to the conversation for non-AJAX POST or GET requests
    return redirect('interaction:conversation_detail', pk=conversation.id)


def simulate_ai_response(tool, user_message, image_url=None, is_image_generation=False, is_video_generation=False):
    """
    Dispatch to the appropriate non-streaming API generation function based on tool type.
    Handles text input, image input, image generation, and video generation requests.
    
    Args:
        tool: The AITool object
        user_message: Text message from the user
        image_url: Optional base64 encoded image data
        is_image_generation: Whether this is an image generation request
        is_video_generation: Whether this is a video generation request
        
    Returns:
        Text response, image data, video data, or error message
    """
    try:
        if is_video_generation:
            if tool.api_type == 'GEMINI':
                params = {}
                prompt = user_message
                
                if ":" in user_message:
                    prompt_parts = user_message.split("\n")
                    prompt_lines = []
                    for part in prompt_parts:
                        if ":" in part and not part.startswith("http"):
                            key, value = part.split(":", 1)
                            key = key.strip().lower()
                            value = value.strip()
                            if key == "number_of_videos":
                                try:
                                    params[key] = int(value)
                                except ValueError:
                                    params[key] = 1
                            elif key == "aspect_ratio":
                                params[key] = value
                            elif key == "person_generation":
                                params[key] = value
                            elif key == "duration_seconds":
                                try:
                                    params[key] = int(value)
                                except ValueError:
                                    params[key] = 5
                            elif key == "enhance_prompt":
                                params[key] = value.lower() == "true"
                            else:
                                prompt_lines.append(part)
                        else:
                            prompt_lines.append(part)
                    prompt = "\n".join(prompt_lines)
                
                # Generate videos using Veo
                result = generate_veo_video(tool, prompt, image_url, **params)
                if isinstance(result, dict) and "error" in result:
                    return f"Video generation error: {result['error']}"
                
                response = "Generated videos based on your prompt:\n\n"
                for i, video in enumerate(result):
                    if isinstance(video, dict) and "video_data" in video:
                        video_data = video.get("video_data", "")
                        response += f"Video {i+1}: {video_data}\n\n"
                return response
            else:
                return fallback_response(tool, user_message, "Video generation is only available with Gemini API.")
        
        elif is_image_generation:
            if tool.api_type == 'GEMINI':
                params = {}
                if ":" in user_message:
                    prompt_parts = user_message.split("\n")
                    prompt = []
                    for part in prompt_parts:
                        if ":" in part and not part.startswith("http"):
                            key, value = part.split(":", 1)
                            key = key.strip().lower()
                            value = value.strip()
                            if key == "number_of_images":
                                try:
                                    params[key] = int(value)
                                except ValueError:
                                    params[key] = 1
                            elif key == "aspect_ratio":
                                params[key] = value
                            elif key == "person_generation":
                                params[key] = value
                            else:
                                prompt.append(part)
                        else:
                            prompt.append(part)
                    prompt = "\n".join(prompt)
                else:
                    prompt = user_message
                
                # Generate images using Imagen 3
                result = generate_imagen_image(tool, prompt, **params)
                if isinstance(result, dict) and "error" in result:
                    return f"Image generation error: {result['error']}"
                
                response = "Generated images based on your prompt:\n\n"
                for i, img in enumerate(result):
                    if isinstance(img, dict) and "image_data" in img:
                        image_data = img.get("image_data", "")
                        response += f"Image {i+1}: {image_data}\n\n"
                return response
            else:
                return fallback_response(tool, user_message, "Image generation is only available with Gemini API.")
        
        elif image_url and tool.api_type == 'GEMINI':
            result = generate_gemini_image_edit(tool, user_message, image_url)
            if "error" in result:
                return f"Image editing error: {result['error']}"
            
            response = result["text"] + "\n\n"
            for i, img_url in enumerate(result["images"]):
                response += f"Edited image {i+1}: {img_url}\n\n"
            return response
        
        # Handle regular text generation
        elif tool.api_type == 'OPENAI':
            return generate_openai_response(tool, user_message)
        elif tool.api_type == 'GEMINI':
            return generate_gemini_response(tool, user_message)
        elif tool.api_type == 'HUGGINGFACE':
            return generate_huggingface_response(tool, user_message)
        elif tool.api_type == 'ANTHROPIC':
            return fallback_response(tool, user_message, "Anthropic API integration is not yet available for non-streaming.")
        elif tool.api_type == 'GOOGLE': # Consider renaming or removing if GEMINI covers all Google AI
            return fallback_response(tool, user_message, "Google AI API integration is not yet available for non-streaming.")
        else:
            return fallback_response(tool, user_message)
    except Exception as e:
        print(f"Error in simulate_ai_response dispatcher: {str(e)}")
        # Provide a generic error message via fallback
        return fallback_response(tool, user_message, f"An error occurred while processing the request: {str(e)}")


def generate_openai_response(tool, user_message):
    """
    Non-streaming Azure OpenAI response generation (Text only for fallback).
    """
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
    api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
    deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT')
    if not all([api_key, endpoint, api_version, deployment]):
        return fallback_response(tool, user_message, "Azure OpenAI configuration is missing in environment variables.")

    try:
        client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        # Use deployment as the model name
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": f"You are {tool.name}, an AI assistant by {tool.provider}. Respond concisely."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return fallback_response(tool, user_message, f"Azure OpenAI API error (non-streaming): {str(e)}")


def generate_gemini_response(tool, user_message):
    """
    Non-streaming Gemini response generation (Text only for fallback).
    Uses the new client-based approach for the Gemini API.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return fallback_response(tool, user_message, "Gemini API key not found.")

    try:
        client = genai.Client(api_key=api_key)
        model_name = tool.api_model or "gemini-2.0-flash"
        
        # Generate content with text only for this fallback
        response = client.models.generate_content(
            model=model_name,
            contents=[user_message],
            config=genai.types.GenerateContentConfig(
                max_output_tokens=1024,
                temperature=0.7,
                top_p=0.95,
                top_k=40
            )
        )
        
        # Handle potential lack of text in response
        if hasattr(response, 'text') and response.text:
            return response.text
        else:
            # Handle cases where the response might be blocked or empty
            # Log the full response for debugging
            print(f"Gemini Warning: Received response with no text. Full response: {response}")
            # Check for prompt feedback indicating blocking
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason'):
                return f"My response was blocked due to: {response.prompt_feedback.block_reason.name}. Please modify your prompt."
            return fallback_response(tool, user_message, "Received an empty or blocked response from Gemini.")

    except Exception as e:
        return fallback_response(tool, user_message, f"Gemini API error (non-streaming): {str(e)}")


# (Removed generate_huggingface_response and all  API code as requested)
    """
    Generate a response using  API (placeholder/example).
    Requires tool.api_endpoint to be set correctly.
    """
    api_key = os.environ.get('') # Assumes HF key is needed
    if not api_key:
        return fallback_response(tool, user_message, " API key not found.")
    if not tool.api_endpoint:
         return fallback_response(tool, user_message, " model endpoint not configured for this tool.")

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"inputs": user_message}
        response = requests.post(tool.api_endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raise an exception for bad status codes
        result = response.json()
        # The actual response structure depends heavily on the specific HF model/API
        # This is a common structure for text generation models
        return result[0].get('generated_text', "Sorry, I couldn't process that.")
    except requests.exceptions.RequestException as e:
         return fallback_response(tool, user_message, f" API request error: {str(e)}")
    except Exception as e:
        return fallback_response(tool, user_message, f" API error: {str(e)}")


def generate_imagen_image(tool, prompt, number_of_images=1, aspect_ratio="1:1", person_generation="ALLOW_ADULT"):
    """
    Generate images using Imagen 3 model.
    
    Args:
        tool: The AITool object
        prompt: Text prompt for image generation
        number_of_images: Number of images to generate (1-4)
        aspect_ratio: Aspect ratio of generated images ("1:1", "3:4", "4:3", "9:16", "16:9")
        person_generation: Person generation policy ("DONT_ALLOW" or "ALLOW_ADULT")
        
    Returns:
        List of base64 encoded image data or error message
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return {"error": "Gemini API key not found."}
    
    try:
        client = genai.Client(api_key=api_key)
        model = 'imagen-3.0-generate-002'  # Imagen 3 model
        
        number_of_images = max(1, min(4, number_of_images))
        
        valid_aspect_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
        if aspect_ratio not in valid_aspect_ratios:
            aspect_ratio = "1:1"  # Default to 1:1 if invalid
        
        valid_person_generation = ["DONT_ALLOW", "ALLOW_ADULT"]
        if person_generation not in valid_person_generation:
            person_generation = "ALLOW_ADULT"  # Default
        
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
                person_generation=person_generation
            )
        )
        
        result = []
        for generated_image in response.generated_images:
            image_bytes = generated_image.image.image_bytes
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            result.append({
                "image_data": f"data:image/png;base64,{base64_image}",
                "prompt": prompt
            })
        
        return result
    
    except Exception as e:
        print(f"Imagen API error: {str(e)}")
        return {"error": f"Error generating image: {str(e)}"}


def generate_gemini_image_edit(tool, prompt, image_data, response_modalities=None):
    """
    Edit images using Gemini's image generation capabilities.
    
    Args:
        tool: The AITool object
        prompt: Text prompt describing the edit
        image_data: Base64 encoded image data or PIL Image object
        response_modalities: List of modalities to include in response (default: ['TEXT', 'IMAGE'])
        
    Returns:
        Dictionary with text and image data or error message
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return {"error": "Gemini API key not found."}
    
    try:
        client = genai.Client(api_key=api_key)
        model = "gemini-1.5-flash"
        
        if response_modalities is None:
            response_modalities = ['TEXT', 'IMAGE']
        
        pil_image = None
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            header, encoded = image_data.split(',', 1)
            decoded_bytes = base64.b64decode(encoded)
            pil_image = Image.open(io.BytesIO(decoded_bytes))
        elif isinstance(image_data, Image.Image):
            pil_image = image_data
        else:
            return {"error": "Invalid image data format"}
        
        # Generate content with image editing
        response = client.models.generate_content(
            model=model,
            contents=[prompt, pil_image],
            config=types.GenerateContentConfig(
                response_modalities=response_modalities
            )
        )
        
        result = {"text": "", "images": []}
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                result["text"] += part.text
            elif part.inline_data is not None:
                image_bytes = part.inline_data.data
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                mime_type = part.inline_data.mime_type
                result["images"].append(f"data:{mime_type};base64,{base64_image}")
        
        return result
    
    except Exception as e:
        print(f"Gemini image editing error: {str(e)}")
        return {"error": f"Error editing image: {str(e)}"}


def generate_veo_video(tool, prompt, image_data=None, aspect_ratio="16:9", person_generation="ALLOW_ADULT", 
                      number_of_videos=1, duration_seconds=5, enhance_prompt=True):
    """
    Generate videos using Veo model.
    
    Args:
        tool: The AITool object
        prompt: Text prompt for video generation
        image_data: Optional base64 encoded image data or PIL Image object for image-to-video generation
        aspect_ratio: Aspect ratio of generated videos ("16:9" or "9:16")
        person_generation: Person generation policy ("DONT_ALLOW" or "ALLOW_ADULT") - only for text-to-video
        number_of_videos: Number of videos to generate (1 or 2)
        duration_seconds: Length of each output video in seconds (5-8)
        enhance_prompt: Enable or disable the prompt rewriter
        
    Returns:
        List of dictionaries with video data or error message
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return {"error": "Gemini API key not found."}
    
    try:
        client = genai.Client(api_key=api_key)
        model = 'veo-2.0-generate-001'  # Veo model
        
        valid_aspect_ratios = ["16:9", "9:16"]
        if aspect_ratio not in valid_aspect_ratios:
            aspect_ratio = "16:9"  # Default to 16:9 if invalid
        
        valid_person_generation = ["DONT_ALLOW", "ALLOW_ADULT"]
        if person_generation not in valid_person_generation:
            person_generation = "ALLOW_ADULT"  # Default
        
        number_of_videos = max(1, min(2, number_of_videos))
        duration_seconds = max(5, min(8, duration_seconds))
        
        config_params = {
            "aspect_ratio": aspect_ratio,
            "number_of_videos": number_of_videos,
            "duration_seconds": duration_seconds,
            "enhance_prompt": enhance_prompt
        }
        
        # For text-to-video, we can specify person_generation
        if image_data is None:
            config_params["person_generation"] = person_generation
        
        pil_image = None
        if image_data:
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                header, encoded = image_data.split(',', 1)
                decoded_bytes = base64.b64decode(encoded)
                pil_image = Image.open(io.BytesIO(decoded_bytes))
            elif isinstance(image_data, Image.Image):
                pil_image = image_data
            else:
                return {"error": "Invalid image data format"}
        
        if pil_image:
            # Image-to-video generation
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                image=pil_image,
                config=types.GenerateVideosConfig(**config_params)
            )
        else:
            # Text-to-video generation
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                config=types.GenerateVideosConfig(**config_params)
            )
        
        import time
        while not operation.done:
            time.sleep(20)
            operation = client.operations.get(operation)
        
        result = []
        for i, video in enumerate(operation.response.generated_videos):
            video_filename = f"video_{int(time.time())}_{i}.mp4"
            video_path = os.path.join("/tmp", video_filename)
            
            client.files.download(file=video.video)
            video.video.save(video_path)
            
            with open(video_path, "rb") as video_file:
                video_bytes = video_file.read()
                base64_video = base64.b64encode(video_bytes).decode('utf-8')
            
            result.append({
                "video_data": f"data:video/mp4;base64,{base64_video}",
                "prompt": prompt
            })
            
            os.remove(video_path)
        
        return result
    
    except Exception as e:
        print(f"Veo API error: {str(e)}")
        return {"error": f"Error generating video: {str(e)}"}


def fallback_response(tool, user_message, error_message=None):
    """
    Provides a generic fallback response or formats an error message.
    """
    if error_message:
        print(f"Fallback triggered for {tool.name}: {error_message}")
        return f"I encountered an issue processing your request with {tool.name}. Error: {error_message}"
    else:
        responses = [
            f"Sorry, I can't fully process that request with {tool.name} right now.",
            f"Hmm, I'm having trouble connecting to the {tool.name} service.",
            f"Let me try that again later. I couldn't get a response from {tool.name}."
        ]
        return random.choice(responses)


@login_required
def update_conversation_title(request, conversation_id):
    """
    Update the title of a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        form = ConversationTitleForm(request.POST, instance=conversation)
        if form.is_valid():
            form.save()
            # Return JSON for AJAX request or redirect
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'new_title': conversation.title})
            else:
                messages.success(request, _('Conversation title updated.'))
                return redirect('interaction:conversation_detail', pk=conversation.id)
        else:
            # Handle errors if needed, perhaps return JSON error
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            else:
                 messages.error(request, _('Error updating title.'))
    # If not POST, or if form invalid in non-AJAX, redirect back
    return redirect('interaction:conversation_detail', pk=conversation.id)


@login_required
def delete_conversation(request, conversation_id):
    """
    Delete a conversation.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    if request.method == 'POST':
        conversation_title = conversation.title # Get title before deleting
        conversation.delete()
        messages.success(request, _(f'Conversation "{conversation_title}" deleted.'))
        return redirect('interaction:conversation_list')
    
    # If GET, render confirmation page (though usually handled by modal)
    # You might want to redirect to list if accessed via GET directly
    # return render(request, 'interaction/delete_confirmation.html', {'conversation': conversation})
    return redirect('interaction:conversation_list')
