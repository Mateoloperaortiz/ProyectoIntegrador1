import json
import os
import io
import base64
import httpx
import pathlib
import time
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
        pdf_url = data.get('pdf_url')  # Can be base64 data URL or file URL
        is_pdf_upload = data.get('is_pdf_upload', False)  # Flag for PDF upload
        user = self.scope["user"]

        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id, user=user)
        
        @database_sync_to_async
        def get_tool(conversation):
            return conversation.tool
        tool = await get_tool(conversation)

        file_type = None
        if image_url:
            file_type = 'image'
        elif pdf_url:
            file_type = 'pdf'

        await database_sync_to_async(Message.objects.create)(
            conversation=conversation, 
            is_from_user=True, 
            content=user_message, 
            image_url=image_url,
            pdf_url=pdf_url,
            file_type=file_type
        )

        if tool.api_type == 'OPENAI':
            await self.stream_openai_response(tool, user_message, conversation, user, image_url)
        elif tool.api_type == 'GEMINI':
            await self.stream_gemini_response(tool, user_message, conversation, user, image_url, pdf_url, is_pdf_upload)
        else:
            from .views import simulate_ai_response
            ai_response = await database_sync_to_async(simulate_ai_response)(tool, user_message)
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

    async def stream_gemini_response(self, tool, user_message, conversation, user, image_url=None, pdf_url=None, is_pdf_upload=False):
        api_key = os.environ.get('GEMINI_API_KEY')
        model_name = tool.api_model or "gemini-2.0-flash-live-001"

        if not api_key:
            await self.send(text_data=json.dumps({'type': 'error', 'content': "Gemini API key not found."}))
            return

        try:
            client = genai.Client(api_key=api_key)
            contents = []
            pil_image = None
            pdf_data = None
            file_obj = None

            if image_url and image_url.startswith('data:image'):
                try:
                    header, encoded = image_url.split(',', 1)
                    decoded_bytes = base64.b64decode(encoded)
                    pil_image = Image.open(io.BytesIO(decoded_bytes))
                    contents.append(pil_image)
                except Exception as img_err:
                    await self.send(text_data=json.dumps({'type': 'error', 'content': f"Error processing image: {str(img_err)}"}))
                    return

            if pdf_url:
                try:
                    await self.send(text_data=json.dumps({
                        'type': 'ai_message', 
                        'content': "Processing PDF document...", 
                        'done': False
                    }))

                    if pdf_url.startswith('data:application/pdf'):
                        header, encoded = pdf_url.split(',', 1)
                        pdf_bytes = base64.b64decode(encoded)
                        
                        if len(pdf_bytes) < 20 * 1024 * 1024:  # 20MB
                            pdf_data = types.Part.from_bytes(
                                data=pdf_bytes,
                                mime_type='application/pdf'
                            )
                            contents.append(pdf_data)
                        else:
                            pdf_io = io.BytesIO(pdf_bytes)
                            file_obj = await database_sync_to_async(client.files.upload)(
                                file=pdf_io,
                                config=dict(mime_type='application/pdf')
                            )
                            contents.append(file_obj)
                    elif pdf_url.startswith('http'):
                        await self.send(text_data=json.dumps({
                            'type': 'ai_message', 
                            'content': "Downloading PDF from URL...", 
                            'done': False
                        }))
                        
                        response = await database_sync_to_async(httpx.get)(pdf_url)
                        pdf_bytes = response.content
                        
                        if len(pdf_bytes) < 20 * 1024 * 1024:  # 20MB
                            pdf_data = types.Part.from_bytes(
                                data=pdf_bytes,
                                mime_type='application/pdf'
                            )
                            contents.append(pdf_data)
                        else:
                            pdf_io = io.BytesIO(pdf_bytes)
                            file_obj = await database_sync_to_async(client.files.upload)(
                                file=pdf_io,
                                config=dict(mime_type='application/pdf')
                            )
                            contents.append(file_obj)
                except Exception as pdf_err:
                    await self.send(text_data=json.dumps({'type': 'error', 'content': f"Error processing PDF: {str(pdf_err)}"}))
                    return

            contents.append(user_message)

            response_stream = await database_sync_to_async(client.models.generate_content_stream)(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            ai_content = ""

            async for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    ai_content += chunk.text
                    await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': False}))

            if file_obj:
                try:
                    await database_sync_to_async(client.files.delete)(file_obj.name)
                except Exception as del_err:
                    print(f"Warning: Could not delete temporary file: {str(del_err)}")

            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, 
                is_from_user=False, 
                content=ai_content, 
                image_url=None,
                pdf_url=pdf_url if is_pdf_upload else None,
                file_type='pdf' if is_pdf_upload else None
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
