import os
import io
import google.genai as genai
from google.genai import types
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings

from .models import GeminiFile, MessageGeminiFile
from interaction.models import Message

# Initialize the Gemini client
def get_gemini_client():
    """
    Get an initialized Gemini client using the API key from environment variables.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    
    return genai.Client(api_key=api_key)


@login_required
@require_http_methods(["GET"])
def file_list(request):
    """
    List all Gemini files for the current user.
    """
    user_files = GeminiFile.objects.filter(user=request.user).order_by('-created_at')
    
    # Clean up expired files
    now = timezone.now()
    expired_files = user_files.filter(expiration_time__lt=now)
    for expired_file in expired_files:
        try:
            # Attempt to delete from Gemini API
            client = get_gemini_client()
            client.files.delete(name=expired_file.gemini_file_id)
        except Exception as e:
            # Log error but continue with DB deletion
            print(f"Error deleting expired file from Gemini API: {str(e)}")
        
        # Delete from database
        expired_file.delete()
    
    # Re-query to get updated list
    user_files = GeminiFile.objects.filter(user=request.user).order_by('-created_at')
    
    # Optionally fetch the latest file metadata from Gemini
    fresh_data = request.GET.get('refresh') == 'true'
    if fresh_data:
        client = get_gemini_client()
        for file in user_files:
            try:
                gemini_file = client.files.get(name=file.gemini_file_id)
                # Update metadata if needed
                if gemini_file:
                    # No updates needed for now
                    pass
            except Exception as e:
                # Log but continue
                print(f"Error refreshing file metadata from Gemini API: {str(e)}")
    
    # Return as JSON for API calls or render template for web interface
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        files_data = [
            {
                'id': file.id,
                'gemini_file_id': file.gemini_file_id,
                'filename': file.filename,
                'purpose': file.purpose,
                'mime_type': file.mime_type,
                'bytes_size': file.bytes_size,
                'created_at': file.created_at.isoformat(),
                'expiration_time': file.expiration_time.isoformat() if file.expiration_time else None
            }
            for file in user_files
        ]
        return JsonResponse({'files': files_data})
    
    return render(request, 'gemini_integration/file_list.html', {'files': user_files})


@login_required
@require_http_methods(["POST"])
def file_upload(request):
    """
    Upload a file to the Gemini API and store its metadata.
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    uploaded_file = request.FILES['file']
    purpose = request.POST.get('purpose', 'general')
    message_id = request.POST.get('message_id', None)
    
    # Check file size (2GB limit for Gemini API)
    if uploaded_file.size > 2 * 1024 * 1024 * 1024:  # 2GB in bytes
        return JsonResponse({'error': 'File size exceeds 2GB limit'}, status=400)
    
    # Determine mime type based on file extension or content
    mime_type = uploaded_file.content_type or 'application/octet-stream'
    
    try:
        # Initialize Gemini client
        client = get_gemini_client()
        
        # Read file into memory
        file_content = io.BytesIO(uploaded_file.read())
        
        # Upload file to Gemini API
        gemini_file = client.files.upload(
            file=file_content,
            config=dict(mime_type=mime_type)
        )
        
        # Calculate expiration time (48 hours from now as per Gemini docs)
        expiration_time = timezone.now() + timedelta(hours=48)
        
        # Store file metadata in our database
        file_record = GeminiFile.objects.create(
            user=request.user,
            gemini_file_id=gemini_file.name,  # The Gemini API returns the full file name/path
            filename=uploaded_file.name,
            purpose=purpose,
            mime_type=mime_type,
            bytes_size=uploaded_file.size,
            expiration_time=expiration_time
        )
        
        # If a message ID was provided, associate the file with that message
        if message_id:
            try:
                message = Message.objects.get(id=message_id, conversation__user=request.user)
                MessageGeminiFile.objects.create(
                    message=message,
                    gemini_file=file_record
                )
            except Message.DoesNotExist:
                # Log error but continue
                print(f"Could not associate file with message ID {message_id}: Message not found or not owned by user")
        
        # Return success response
        response_data = {
            'success': True,
            'file_id': file_record.id,
            'gemini_file_id': file_record.gemini_file_id,
            'filename': file_record.filename,
            'purpose': file_record.purpose,
            'mime_type': file_record.mime_type,
            'bytes_size': file_record.bytes_size,
            'created_at': file_record.created_at.isoformat(),
            'expiration_time': file_record.expiration_time.isoformat() if file_record.expiration_time else None
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        # Log the error and return a JSON response
        print(f"Error uploading file to Gemini API: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def file_detail(request, file_id):
    """
    Get details for a specific Gemini file.
    """
    file_record = get_object_or_404(GeminiFile, id=file_id)
    
    # Check ownership
    if file_record.user != request.user:
        return HttpResponseForbidden("You don't have permission to access this file.")
    
    # Fetch fresh metadata from Gemini API
    client = get_gemini_client()
    try:
        gemini_file = client.files.get(name=file_record.gemini_file_id)
        
        # Return as JSON
        file_data = {
            'id': file_record.id,
            'gemini_file_id': file_record.gemini_file_id,
            'filename': file_record.filename,
            'purpose': file_record.purpose,
            'mime_type': file_record.mime_type,
            'bytes_size': file_record.bytes_size,
            'created_at': file_record.created_at.isoformat(),
            'expiration_time': file_record.expiration_time.isoformat() if file_record.expiration_time else None
        }
        
        return JsonResponse(file_data)
    
    except Exception as e:
        # Log the error and return a JSON response
        print(f"Error fetching file details from Gemini API: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST", "DELETE"])
def file_delete(request, file_id):
    """
    Delete a Gemini file.
    """
    file_record = get_object_or_404(GeminiFile, id=file_id)
    
    # Check ownership
    if file_record.user != request.user:
        return HttpResponseForbidden("You don't have permission to delete this file.")
    
    try:
        # Initialize Gemini client
        client = get_gemini_client()
        
        # Delete file from Gemini API
        client.files.delete(name=file_record.gemini_file_id)
        
        # Delete file record from our database
        file_record.delete()
        
        # Return success response
        return JsonResponse({'success': True, 'message': 'File deleted successfully'})
    
    except Exception as e:
        # Log the error and return a JSON response
        print(f"Error deleting file from Gemini API: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def file_manager(request):
    """
    Render the file manager interface.
    """
    return render(request, 'gemini_integration/file_manager.html')
