import json
import os
import time
import logging
from typing import Dict, Any, Optional, Union

from dotenv import load_dotenv

# Import core utility functions
from core.utils import call_api
from core.security import get_api_key
from core.logging_utils import log_api_request, log_exception

# Get a logger for this module
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def call_openai_api(prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
    """
    Call the OpenAI API for text generation.
    
    Args:
        prompt (str): The prompt to send to the API
        max_tokens (int): Maximum number of tokens to generate
        
    Returns:
        dict: Response from the API or error message
    """
    # Log the API call attempt
    logger.info(f"Calling OpenAI API with prompt length: {len(prompt)} chars")
    
    # Get API key securely
    api_key = get_api_key('OPENAI_API_KEY')
    
    if not api_key:
        error_msg = 'API key not found. Please set OPENAI_API_KEY in environment variables.'
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
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
    
    # Use the centralized call_api function
    response = call_api(
        url='https://api.openai.com/v1/completions',
        method='POST',
        headers=headers,
        json_data=data,
        timeout=10,
        service_name='OpenAI'
    )
    
    # Log additional details specific to OpenAI
    if response['success']:
        logger.debug("OpenAI API request successful")
    else:
        logger.warning(f"OpenAI API request failed: {response.get('error', 'Unknown error')}")
    
    # Add extra context about the request
    log_api_request(
        logger=logger,
        service_name="OpenAI",
        endpoint="/v1/completions",
        method="POST",
        status_code=response.get('status_code', 0),
        response_time=0.0,  # Not available from call_api but could be added
        request_data={
            'model': data['model'],
            'max_tokens': data['max_tokens'],
            'temperature': data['temperature'],
            'prompt_length': len(prompt)
        }
    )
    
    return response

def call_huggingface_api(prompt: str, model: str = "google/flan-t5-small") -> Dict[str, Any]:
    """
    Call the Hugging Face Inference API.
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use for inference
        
    Returns:
        dict: Response from the API or error message
    """
    # Log the API call attempt
    logger.info(f"Calling Hugging Face API with model: {model}")
    
    # Get API key securely
    api_key = get_api_key('HUGGINGFACE_API_KEY')
    
    if not api_key:
        error_msg = 'API key not found. Please set HUGGINGFACE_API_KEY in environment variables.'
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
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
    
    endpoint = f'/models/{model}'
    
    # Use the centralized call_api function
    response = call_api(
        url=f'https://api-inference.huggingface.co/models/{model}',
        method='POST',
        headers=headers,
        json_data=data,
        timeout=10,
        service_name='HuggingFace'
    )
    
    # Log additional details specific to HuggingFace
    if response['success']:
        logger.debug(f"Hugging Face API request successful for model: {model}")
    else:
        logger.warning(f"Hugging Face API request failed: {response.get('error', 'Unknown error')}")
    
    # Add extra context about the request
    log_api_request(
        logger=logger,
        service_name="HuggingFace",
        endpoint=endpoint,
        method="POST",
        status_code=response.get('status_code', 0),
        response_time=0.0,  # Not available from call_api but could be added
        request_data={
            'model': model,
            'wait_for_model': True,
            'prompt_length': len(prompt)
        }
    )
    
    return response