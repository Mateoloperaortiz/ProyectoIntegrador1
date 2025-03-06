import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_openai_api(prompt, max_tokens=100):
    """
    Call the OpenAI API for text generation.
    
    Args:
        prompt (str): The prompt to send to the API
        max_tokens (int): Maximum number of tokens to generate
        
    Returns:
        dict: Response from the API or error message
    """
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        return {
            'success': False,
            'error': 'API key not found. Please set OPENAI_API_KEY in .env file.'
        }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        'model': 'gpt-3.5-turbo-instruct',
        'prompt': prompt,
        'max_tokens': max_tokens,
        'temperature': 0.7
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/completions',
            headers=headers,
            data=json.dumps(data),
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        else:
            return {
                'success': False,
                'error': f'API Error: {response.status_code}',
                'message': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }

def call_huggingface_api(prompt, model="google/flan-t5-small"):
    """
    Call the Hugging Face Inference API.
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use for inference
        
    Returns:
        dict: Response from the API or error message
    """
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    if not api_key:
        return {
            'success': False,
            'error': 'API key not found. Please set HUGGINGFACE_API_KEY in .env file.'
        }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'inputs': prompt,
        'options': {
            'wait_for_model': True
        }
    }
    
    try:
        response = requests.post(
            f'https://api-inference.huggingface.co/models/{model}',
            headers=headers,
            data=json.dumps(data),
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'data': response.json()
            }
        else:
            return {
                'success': False,
                'error': f'API Error: {response.status_code}',
                'message': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Request failed: {str(e)}'
        }