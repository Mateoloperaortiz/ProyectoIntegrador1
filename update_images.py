#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inspireai.settings')
django.setup()

from catalog.models import AITool
from django.core.files import File
from users.models import CustomUser

# Update AI tools with images
tools = AITool.objects.all()
for tool in tools:
    print(f'Processing tool: {tool.name}')
    
    if 'chatgpt' in tool.name.lower():
        image_path = 'media/tool_images/chatgpt.png'
        if os.path.exists(image_path):
            tool.image.save('chatgpt.png', File(open(image_path, 'rb')))
    
    elif 'dall-e' in tool.name.lower() or 'dalle' in tool.name.lower():
        image_path = 'media/tool_images/dalle.png'
        if os.path.exists(image_path):
            tool.image.save('dalle.png', File(open(image_path, 'rb')))
    
    elif 'claude' in tool.name.lower():
        image_path = 'media/tool_images/claude.png'
        if os.path.exists(image_path):
            tool.image.save('claude.png', File(open(image_path, 'rb')))
    
    else:
        # Use placeholder for other tools
        image_path = 'static/images/placeholder.png'
        if os.path.exists(image_path):
            tool.image.save(f'{tool.slug}.png', File(open(image_path, 'rb')))
    
    tool.save()

# Update users with profile pictures
users = CustomUser.objects.all()
for user in users:
    print(f'Processing user: {user.username}')
    if not user.profile_picture:
        image_path = 'static/images/default-avatar.png'
        if os.path.exists(image_path):
            user.profile_picture.save('default-avatar.png', File(open(image_path, 'rb')))
            user.save()

print("Image update completed!")