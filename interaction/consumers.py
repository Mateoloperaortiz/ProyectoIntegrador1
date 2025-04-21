import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from openai import AsyncOpenAI
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
        image_url = data.get('image_url')  # Accept image_url (can be URL or base64)
        user = self.scope["user"]

        conversation = await database_sync_to_async(Conversation.objects.get)(id=self.conversation_id, user=user)
        
        @database_sync_to_async
        def get_tool(conversation):
            return conversation.tool
        tool = await get_tool(conversation)

        await database_sync_to_async(Message.objects.create)(
            conversation=conversation, is_from_user=True, content=user_message, image_url=image_url
        )

        if tool.api_type == 'OPENAI':
            await self.stream_openai_response(tool, user_message, conversation, user, image_url)
        else:
            from .views import simulate_ai_response
            ai_response = await database_sync_to_async(simulate_ai_response)(tool, user_message)
            await database_sync_to_async(Message.objects.create)(
                conversation=conversation, is_from_user=False, content=ai_response
            )
            await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_response, 'done': True}))

    async def stream_openai_response(self, tool, user_message, conversation, user, image_url=None):
        import os
        api_key = os.environ.get('OPENAI_API_KEY')
        model = tool.api_model or "gpt-4o"
        client = AsyncOpenAI(api_key=api_key)
        ai_content = ""
        try:
            # Build multimodal input if image is present
            if image_url:
                input_content = [
                    {"type": "input_text", "text": user_message},
                    {"type": "input_image", "image_url": image_url, "detail": "auto"}
                ]
                input_payload = [
                    {"role": "user", "content": input_content}
                ]
                stream = await client.responses.create(
                    model=model,
                    input=input_payload,
                    stream=True
                )
                async for event in stream:
                    if hasattr(event, "output_text") and event.output_text:
                        ai_content = event.output_text
                        await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': False}))
                await database_sync_to_async(Message.objects.create)(
                    conversation=conversation, is_from_user=False, content=ai_content, image_url=None
                )
                await self.send(text_data=json.dumps({'type': 'ai_message', 'content': ai_content, 'done': True}))
            else:
                # ...existing code for text-only...
                stream = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": f"You are {tool.name}, an AI assistant by {tool.provider}."},
                        {"role": "user", "content": user_message}
                    ],
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
            await self.send(text_data=json.dumps({'type': 'error', 'content': str(e)}))