"""
Core utility functions shared across the entire project.

This module contains utility functions that are used by multiple apps
throughout the project.
"""
from typing import Any, Dict, List, Optional, TypeVar, Union, cast, Tuple
import os
import json
import csv
import time
import logging
import requests
from io import StringIO
from django.conf import settings
from django.http import HttpRequest
from django.utils.text import slugify

# Get a logger for this module
logger = logging.getLogger(__name__)

#
# General utilities
#

# This function has been moved to core.logging_utils
# Kept here for backward compatibility
from core.logging_utils import get_client_ip


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string, returning default value on error.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def format_file_size(size_in_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_in_bytes: File size in bytes
        
    Returns:
        Human-readable file size string
    """
    # Convert bytes to appropriate unit
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024 or unit == 'TB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024


def is_valid_image_extension(filename: str) -> bool:
    """
    Check if a filename has a valid image extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        True if the file has a valid image extension, False otherwise
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    _, extension = os.path.splitext(filename.lower())
    return extension in valid_extensions


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the truncated text
        suffix: Suffix to add if the text is truncated
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


#
# Slug generation utilities
#

def create_unique_slug(model_instance: Any, slugable_field_name: str, 
                      slug_field_name: str = 'slug') -> str:
    """
    Create a unique slug for a model instance.
    
    Args:
        model_instance: The model instance to create a slug for
        slugable_field_name: The name of the field to base the slug on
        slug_field_name: The name of the slug field
        
    Returns:
        A unique slug string
    """
    slug = slugify(getattr(model_instance, slugable_field_name))
    unique_slug = slug
    model_class = model_instance.__class__
    extension = 1
    
    # Check if the slug already exists and make it unique if needed
    while model_class.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{slug}-{extension}"
        extension += 1
        
    return unique_slug


#
# API utilities
#

def call_api(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    service_name: str = "External API"
) -> Dict[str, Any]:
    """
    Generic API call function with logging and error handling.
    
    Args:
        url: The API endpoint URL
        method: HTTP method (GET, POST, etc.)
        headers: Optional request headers
        params: Optional URL parameters
        data: Optional form data
        json_data: Optional JSON data (for POST/PUT)
        timeout: Request timeout in seconds
        service_name: Name of the service for logging
        
    Returns:
        dict: Response with success status and data/error
    """
    method = method.upper()
    headers = headers or {}
    start_time = time.time()
    status_code = None
    error_message = None
    
    try:
        # Prepare request arguments
        request_kwargs = {
            'headers': headers,
            'timeout': timeout,
        }
        
        if params:
            request_kwargs['params'] = params
            
        if data:
            request_kwargs['data'] = data
            
        if json_data:
            request_kwargs['json'] = json_data
        
        # Make the request
        logger.info(f"Calling {service_name} ({method} {url})")
        
        response = requests.request(method, url, **request_kwargs)
        status_code = response.status_code
        response_time = time.time() - start_time
        
        # Log the API request details
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            logger.debug(
                f"{service_name} request: {method} {url} - "
                f"Status: {status_code} - "
                f"Time: {response_time:.3f}s"
            )
        
        # Handle the response
        if 200 <= status_code < 300:
            # Try to parse JSON response
            try:
                result_data = response.json()
                return {
                    "success": True,
                    "data": result_data,
                    "status_code": status_code
                }
            except ValueError:
                # Not JSON, return text
                return {
                    "success": True,
                    "data": response.text,
                    "status_code": status_code
                }
        else:
            error_message = f"{service_name} Error: Status {status_code}"
            logger.warning(f"{error_message} - Response: {response.text[:200]}")
            return {
                "success": False,
                "error": error_message,
                "status_code": status_code,
                "response": response.text
            }
    except requests.exceptions.Timeout:
        error_message = f"{service_name} request timed out after {timeout}s"
        logger.error(error_message)
        return {
            "success": False,
            "error": error_message
        }
    except requests.exceptions.ConnectionError:
        error_message = f"Cannot connect to {service_name}"
        logger.error(error_message)
        return {
            "success": False,
            "error": error_message
        }
    except Exception as e:
        error_message = f"{service_name} request failed: {str(e)}"
        logger.exception(error_message)
        return {
            "success": False,
            "error": error_message
        }


#
# Content formatting utilities
#

def format_conversation_for_download(conversation: Any, format_type: str = 'json') -> Tuple[str, str, str]:
    """
    Format a conversation for download in the specified format.
    
    This function converts a conversation and its messages into one of several downloadable formats.
    Supported formats include JSON, plain text, and CSV.
    
    Args:
        conversation: The Conversation object to format with its associated messages
        format_type: The format type to convert to ('json', 'txt', or 'csv')
        
    Returns:
        Tuple[str, str, str]: A tuple containing:
            - formatted_content: The conversation content in the requested format
            - content_type: The MIME type for the content (e.g., 'application/json')
            - file_extension: The appropriate file extension (e.g., 'json')
            
    Raises:
        ValueError: If an invalid format_type is provided
    """
    messages = conversation.get_messages()
    
    if format_type == 'json':
        # Use the built-in to_json method
        content = conversation.to_json()
        content_type = 'application/json'
        file_ext = 'json'
        
    elif format_type == 'txt':
        # Simple text format
        lines = [f"Conversation: {conversation.title}"]
        lines.append(f"AI Tool: {conversation.ai_tool.name if conversation.ai_tool else 'Unknown'}")
        lines.append(f"Date: {conversation.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append("-" * 40)
        
        for msg in messages:
            sender = "You" if msg.is_user else (conversation.ai_tool.name if conversation.ai_tool else "AI")
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M')
            lines.append(f"{sender} ({timestamp}):")
            lines.append(msg.content)
            lines.append("")
            
        content = "\n".join(lines)
        content_type = 'text/plain'
        file_ext = 'txt'
        
    elif format_type == 'csv':
        # CSV format
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Sender', 'Message'])
        
        for msg in messages:
            sender = "User" if msg.is_user else (conversation.ai_tool.name if conversation.ai_tool else "AI")
            writer.writerow([
                msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                sender,
                msg.content
            ])
            
        content = output.getvalue()
        content_type = 'text/csv'
        file_ext = 'csv'
        
    else:
        # Default to JSON if format not recognized
        content = conversation.to_json()
        content_type = 'application/json'
        file_ext = 'json'
        
    return content, content_type, file_ext
