import json
import os
import io
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from openai import AsyncOpenAI
import google.genai as genai
from google.genai import types
from PIL import Image
from .models import Conversation, Message
from catalog.models import AITool

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get('message')
        image_url = data.get('image_url')  # Can be base64 data URL
        is_image_generation = data.get('is_image_generation', False)  # Flag for image generation requests
        is_image_editing = data.get('is_image_editing', False)  # Flag for image editing requests
        is_video_generation = data.get('is_video_generation', False)  # Flag for video generation requests
        user = self.scope["user"]

        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id, user=user)
        
        @database_sync_to_async
        def get_tool(conversation):
            return conversation.tool
        tool = await get_tool(conversation)

        await database_sync_to_async(Message.objects.create)(
            conversation=conversation, is_from_user=True, content=user_message, image_url=image_url
        )

        if is_video_generation and tool.api_type == 'GEMINI':
            await self.stream_veo_response(tool, user_message, conversation, user, image_url)
        elif is_image_generation and tool.api_type == 'GEMINI':
            await self.stream_imagen_response(tool, user_message, conversation, user)
        elif is_image_editing and image_url and tool.api_type == 'GEMINI':
            await self.stream_gemini_image_edit(tool, user_message, conversation, user, image_url)
        elif tool.api_type == 'OPENAI':
            await self.stream_openai_response(tool, user_message, conversation, user, image_url)
        elif tool.api_type == 'GEMINI':
            await self.stream_gemini_response(tool, user_message, conversation, user, image_url)
        else:
            from .views import simulate_ai_response
            ai_response = await database_sync_to_async(simulate_ai_response)(tool, user_message, image_url)
            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=ai_response
            )
            await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_response, 'done': True}))

    async def stream_openai_response(self, tool, user_message, conversation, user, image_url=None):
        api_key = os.environ.get('OPENAI_API_KEY')
        model = tool.api_model or "gpt-4o"
        if not api_key:
            await self.send(text_data=json.dumps({'type': 'error', 'content': "OpenAI API key not found."}))
            return
        client = AsyncOpenAI(api_key=api_key)
        ai_content = ""
        try:
            if image_url and image_url.startswith('data:image'):
                input_content = [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "auto"}
                    }
                ]
                messages = [
                    {"role": "user", "content": input_content}
                ]
                stream = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
            else:
                messages=[
                    {"role": "system", "content": f"You are {tool.name}, an AI assistant by {tool.provider}."},
                    {"role": "user", "content": user_message}
                ]
                stream = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )

            async for event in stream:
                if hasattr(event, "choices") and event.choices:
                    delta = event.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        ai_content += delta.content
                        await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': False}))

            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=ai_content, image_url=None
            )
            await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': True}))

        except Exception as e:
            error_message = f"Error interacting with OpenAI API: {str(e)}"
            print(error_message)
            await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))

    async def stream_imagen_response(self, tool, user_message, conversation, user):
        """
        Generate images using Imagen 3 and stream the results back to the client.
        """
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            await self.send(text_data=json.dumps({'type': 'error', 'content': "Gemini API key not found."}))
            return

        try:
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
                            prompt_lines.append(part)
                    else:
                        prompt_lines.append(part)
                prompt = "\n".join(prompt_lines)
            
            await self.send(text_data=json.dumps({
                'type': 'ai_message', 
                'content': "Generating images based on your prompt...", 
                'done': False
            }))
            
            from .views import generate_imagen_image
            result = await database_sync_to_async(generate_imagen_image)(tool, prompt, **params)
            
            if isinstance(result, dict) and "error" in result:
                error_message = f"Image generation error: {result['error']}"
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=error_message
                )
                await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))
                return
            
            response_content = "Generated images based on your prompt:\n\n"
            image_urls = []
            
            for i, img in enumerate(result):
                if isinstance(img, dict) and "image_data" in img:
                    image_data = img.get("image_data", "")
                    image_urls.append(image_data)
                    response_content += f"Image {i+1}: {image_data}\n\n"
            
            first_image_url = image_urls[0] if image_urls else None
            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=response_content, image_url=first_image_url
            )
            
            await self.send(text_data=json.dumps({
                'type': 'ai_message', 
                'content': response_content, 
                'done': True
            }))
            
        except Exception as e:
            error_message = f"Error generating images with Imagen: {str(e)}"
            print(error_message)
            try:
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=f"Error: {error_message}"
                )
            except Exception as db_err:
                print(f"Error saving error message to DB: {db_err}")
            await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))
    
    async def stream_gemini_image_edit(self, tool, user_message, conversation, user, image_url):
        """
        Edit images using Gemini and stream the results back to the client.
        """
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            await self.send(text_data=json.dumps({'type': 'error', 'content': "Gemini API key not found."}))
            return

        try:
            if not image_url or not image_url.startswith('data:image'):
                await self.send(text_data=json.dumps({'type': 'error', 'content': "Invalid image data for editing."}))
                return
            
            await self.send(text_data=json.dumps({
                'type': 'ai_message', 
                'content': "Editing image based on your prompt...", 
                'done': False
            }))
            
            from .views import generate_gemini_image_edit
            result = await database_sync_to_async(generate_gemini_image_edit)(tool, user_message, image_url)
            
            if isinstance(result, dict) and "error" in result:
                error_message = f"Image editing error: {result['error']}"
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=error_message
                )
                await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))
                return
            
            response_text = result.get("text", "")
            image_urls = result.get("images", [])
            
            response_content = response_text + "\n\n"
            for i, img_url in enumerate(image_urls):
                response_content += f"Edited image {i+1}: {img_url}\n\n"
            
            first_image_url = image_urls[0] if image_urls else None
            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=response_content, image_url=first_image_url
            )
            
            await self.send(text_data=json.dumps({
                'type': 'ai_message', 
                'content': response_content, 
                'done': True
            }))
            
        except Exception as e:
            error_message = f"Error editing image with Gemini: {str(e)}"
            print(error_message)
            try:
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=f"Error: {error_message}"
                )
            except Exception as db_err:
                print(f"Error saving error message to DB: {db_err}")
            await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))
    
    async def stream_veo_response(self, tool, user_message, conversation, user, image_url=None):
        """
        Generate videos using Veo and stream the results back to the client.
        """
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            await self.send(text_data=json.dumps({'type': 'error', 'content': "Gemini API key not found."}))
            return

        try:
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
            
            await self.send(text_data=json.dumps({
                'type': 'ai_message', 
                'content': "Generating videos based on your prompt... This may take 2-3 minutes.", 
                'done': False
            }))
            
            from .views import generate_veo_video
            result = await database_sync_to_async(generate_veo_video)(tool, prompt, image_url, **params)
            
            if isinstance(result, dict) and "error" in result:
                error_message = f"Video generation error: {result['error']}"
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=error_message
                )
                await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))
                return
            
            response_content = "Generated videos based on your prompt:\n\n"
            video_urls = []
            
            for i, video in enumerate(result):
                if isinstance(video, dict) and "video_data" in video:
                    video_data = video.get("video_data", "")
                    video_urls.append(video_data)
                    response_content += f"Video {i+1}: {video_data}\n\n"
            
            first_video_url = video_urls[0] if video_urls else None
            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=response_content, image_url=first_video_url
            )
            
            await self.send(text_data=json.dumps({
                'type': 'ai_message', 
                'content': response_content, 
                'done': True
            }))
            
        except Exception as e:
            error_message = f"Error generating videos with Veo: {str(e)}"
            print(error_message)
            try:
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=f"Error: {error_message}"
                )
            except Exception as db_err:
                print(f"Error saving error message to DB: {db_err}")
            await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))

    async def stream_gemini_response(self, tool, user_message, conversation, user, image_url=None):
        api_key = os.environ.get('GEMINI_API_KEY')
        model_name = tool.api_model or "gemini-2.0-flash-live-001"

        if not api_key:
            await self.send(text_data=json.dumps({'type': 'error', 'content': "Gemini API key not found."}))
            return

        try:
            client = genai.Client(api_key=api_key)
            contents = []
            pil_image = None

            if image_url and image_url.startswith('data:image'):
                try:
                    header, encoded = image_url.split(',', 1)
                    decoded_bytes = base64.b64decode(encoded)
                    pil_image = Image.open(io.BytesIO(decoded_bytes))
                    contents.append(pil_image)
                except Exception as img_err:
                    await self.send(text_data=json.dumps({'type': 'error', 'content': f"Error processing image: {str(img_err)}"}))
                    return

            contents.append(user_message)

            response_stream = await database_sync_to_async(client.models.generate_content_stream)(
                model=model_name,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    max_output_tokens=1024,
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            ai_content = ""

            async for chunk in response_stream:
                if hasattr(chunk, 'text'):
                    ai_content += chunk.text
                    await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': False}))

            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=ai_content, image_url=None
            )
            await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': True}))

        except Exception as e:
            error_message = f"Error interacting with Gemini API: {str(e)}"
            print(error_message)
            try:
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=f"Error: {error_message}"
                )
            except Exception as db_err:
                 print(f"Error saving error message to DB: {db_err}")
            await self.send(text_data=json.dumps({'type': 'error', 'content': error_message}))
