"""
Utility functions for the catalog app.
"""
import json
import requests
import os
import time
from django.http import HttpResponse
from django.conf import settings
import random

# Get API keys from environment variables (or set defaults for demo)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

def call_openai_api(prompt, model="gpt-3.5-turbo"):
    """
    Call OpenAI API with the provided prompt.
    
    Args:
        prompt (str): The message to send to the API
        model (str): The OpenAI model name to use
        
    Returns:
        dict: Response with success status and data/error
    """
    # If no API key set, return a simulated response
    if not OPENAI_API_KEY:
        return simulate_ai_response("openai", prompt)
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        response_data = response.json()
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response_data
            }
        else:
            return {
                "success": False,
                "error": response_data.get("error", {}).get("message", "Unknown error")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def call_huggingface_api(prompt, model="google/flan-t5-base"):
    """
    Call Hugging Face Inference API with the provided prompt.
    
    Args:
        prompt (str): The message to send to the API
        model (str): The Hugging Face model to use
        
    Returns:
        dict: Response with success status and data/error
    """
    # If no API key set, return a simulated response
    if not HUGGINGFACE_API_KEY:
        return simulate_ai_response("huggingface", prompt)
    
    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }
        
        data = {
            "inputs": prompt,
            "parameters": {
                "max_length": 512,
                "temperature": 0.7
            }
        }
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json()
            }
        else:
            return {
                "success": False,
                "error": f"Error {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def simulate_ai_response(service_type, prompt):
    """
    Simulate an AI response for demo purposes.
    
    Args:
        service_type (str): The type of service (openai, huggingface, etc.)
        prompt (str): The user's input
        
    Returns:
        dict: Simulated response object
    """
    # Add a slight delay to simulate network latency
    time.sleep(1.5)
    
    # List of possible responses based on common queries
    responses = [
        f"I'm a simulated AI assistant. You asked: '{prompt}'",
        f"This is a demo response to: '{prompt}'",
        "I'd be happy to help with that! However, this is currently running in demo mode.",
        "That's an interesting question. In a full implementation, I would connect to the appropriate API.",
        "I understand your request. In demo mode, I can only provide simulated responses.",
        f"I processed your input: '{prompt}' and would normally generate a thoughtful response.",
        "Thanks for your message. This is a placeholder response since we're in demo mode.",
        "I'm designed to simulate AI responses for demonstration purposes.",
        "I noticed your question and would typically analyze it in detail. This is a demo response.",
        "Interesting prompt! In a full implementation, I would generate a more tailored response."
    ]
    
    # Format based on service type
    if service_type == "openai":
        return {
            "success": True,
            "data": {
                "choices": [
                    {
                        "text": random.choice(responses)
                    }
                ]
            }
        }
    elif service_type == "huggingface":
        return {
            "success": True,
            "data": [
                {
                    "generated_text": random.choice(responses)
                }
            ]
        }
    else:
        return {
            "success": True,
            "data": {
                "response": random.choice(responses)
            }
        }

def send_to_ai_service(prompt, service_config):
    """
    Send a prompt to an AI service and get a response.
    
    Args:
        prompt (str): The user's message to send to the AI
        service_config (dict): Configuration for the AI service (API type, endpoint, model, etc)
        
    Returns:
        str: The AI's response
    """
    api_type = service_config.get('api_type', 'none')
    
    if api_type == 'openai':
        model = service_config.get('api_model', 'gpt-3.5-turbo')
        response = call_openai_api(prompt, model)
        if response['success']:
            try:
                return response['data']['choices'][0]['message']['content']
            except (KeyError, IndexError):
                return "Received an unexpected response format from the AI."
        else:
            return f"Error calling OpenAI API: {response.get('error', 'Unknown error')}"
            
    elif api_type == 'huggingface':
        model = service_config.get('api_model', 'google/flan-t5-base')
        response = call_huggingface_api(prompt, model)
        if response['success']:
            try:
                if isinstance(response['data'], list):
                    return response['data'][0]['generated_text']
                else:
                    return response['data']['generated_text']
            except (KeyError, IndexError):
                return "Received an unexpected response format from the AI."
        else:
            return f"Error calling Hugging Face API: {response.get('error', 'Unknown error')}"
    
    # Default response for demo purposes
    return f"This is a simulated response from the AI service for: '{prompt}'"

def format_conversation_for_download(conversation, format_type='json'):
    """
    Format a conversation for download in the specified format.
    
    Args:
        conversation: The Conversation object to format
        format_type (str): The format to convert to ('json', 'txt', etc)
        
    Returns:
        HttpResponse: A downloadable response with the conversation data
    """
    if format_type == 'json':
        # Convert to JSON format
        content = conversation.to_json()
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="conversation_{conversation.id}.json"'
        return response
    elif format_type == 'txt':
        # Convert to plain text format
        lines = [
            f"Conversation: {conversation.title}",
            f"AI Tool: {conversation.ai_tool.name}",
            f"Date: {conversation.created_at.strftime('%Y-%m-%d %H:%M')}",
            "-----------------------------------",
        ]
        
        for msg in conversation.get_messages():
            sender = "User" if msg.is_user else "AI"
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            lines.append(f"[{timestamp}] {sender}: {msg.content}")
            
        content = "\n".join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="conversation_{conversation.id}.txt"'
        return response
    else:
        # Unsupported format
        return HttpResponse(f"Format '{format_type}' not supported", status=400)