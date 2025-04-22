import os
import json
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import FileUploadForm, TextToSpeechForm, SpeechToTextForm, StructuredOutputForm
from .models import OpenAIFile, OpenAIThread, MessageOpenAIFile
from .services import (
    upload_file, retrieve_file, retrieve_file_content, delete_file, list_files,
    get_or_create_thread, add_message_to_thread, list_thread_messages,
    generate_tts, transcribe_audio
)
from interaction.models import Conversation, Message


@login_required
def file_upload_view(request):
    """
    View for uploading files to OpenAI.
    """
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                openai_file = upload_file(
                    file_obj=request.FILES['file'],
                    purpose=form.cleaned_data['purpose'],
                    user=request.user
                )
                
                messages.success(request, _(f"File '{openai_file.filename}' uploaded successfully."))
                
                # If AJAX request, return JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'file_id': openai_file.openai_file_id,
                        'filename': openai_file.filename,
                        'size': openai_file.bytes_size
                    })
                
                # Otherwise redirect to file list view
                return redirect('openai_integration:file_list')
                
            except Exception as e:
                messages.error(request, _(f"Error uploading file: {str(e)}"))
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=400)
    else:
        form = FileUploadForm()
    
    return render(request, 'openai_integration/file_upload.html', {
        'form': form
    })


@login_required
def file_list_view(request):
    """
    View for listing files uploaded to OpenAI.
    """
    # Get purpose filter from request parameters
    purpose = request.GET.get('purpose')
    
    # Get files from OpenAI
    try:
        if purpose:
            files_response = list_files(purpose=purpose)
        else:
            files_response = list_files()
        
        openai_files = files_response.data
    except Exception as e:
        openai_files = []
        messages.error(request, _(f"Error retrieving files: {str(e)}"))
    
    # Filter to show only files uploaded by this user
    user_file_ids = OpenAIFile.objects.filter(user=request.user).values_list('openai_file_id', flat=True)
    user_files = [f for f in openai_files if f.id in user_file_ids]
    
    return render(request, 'openai_integration/file_list.html', {
        'files': user_files,
        'purpose_filter': purpose
    })


@login_required
def file_detail_view(request, file_id):
    """
    View for displaying file details.
    """
    # Get file from database and OpenAI
    openai_file_obj = get_object_or_404(OpenAIFile, openai_file_id=file_id, user=request.user)
    
    try:
        openai_file = retrieve_file(file_id)
    except Exception as e:
        messages.error(request, _(f"Error retrieving file details: {str(e)}"))
        return redirect('openai_integration:file_list')
    
    # Get conversations that use this file
    conversations = Conversation.objects.filter(
        message__openai_files__openai_file=openai_file_obj
    ).distinct()
    
    return render(request, 'openai_integration/file_detail.html', {
        'file': openai_file,
        'local_file': openai_file_obj,
        'conversations': conversations
    })


@login_required
def file_content_view(request, file_id):
    """
    View for displaying/downloading file contents.
    """
    # Check that the file belongs to the user
    get_object_or_404(OpenAIFile, openai_file_id=file_id, user=request.user)
    
    try:
        content = retrieve_file_content(file_id)
        
        # Determine content type based on file extension
        file_obj = OpenAIFile.objects.get(openai_file_id=file_id)
        filename = file_obj.filename
        
        content_type = 'application/octet-stream'  # Default
        if filename.endswith('.json') or filename.endswith('.jsonl'):
            content_type = 'application/json'
        elif filename.endswith('.txt'):
            content_type = 'text/plain'
        elif filename.endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        messages.error(request, _(f"Error retrieving file content: {str(e)}"))
        return redirect('openai_integration:file_detail', file_id=file_id)


@login_required
@require_POST
def file_delete_view(request, file_id):
    """
    View for deleting a file.
    """
    # Check that the file belongs to the user
    get_object_or_404(OpenAIFile, openai_file_id=file_id, user=request.user)
    
    try:
        response = delete_file(file_id)
        
        if response.deleted:
            messages.success(request, _("File deleted successfully."))
        else:
            messages.error(request, _("Failed to delete file."))
        
        # If AJAX request, return JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': response.deleted
            })
        
    except Exception as e:
        messages.error(request, _(f"Error deleting file: {str(e)}"))
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return redirect('openai_integration:file_list')


@login_required
def text_to_speech_view(request):
    """
    View for text-to-speech synthesis.
    """
    if request.method == 'POST':
        form = TextToSpeechForm(request.POST)
        if form.is_valid():
            try:
                text = form.cleaned_data['text']
                voice = form.cleaned_data['voice']
                output_format = form.cleaned_data['format']
                
                audio_data = generate_tts(text, voice, output_format)
                
                # Return audio file
                content_type = 'audio/mpeg' if output_format == 'mp3' else 'audio/opus'
                response = HttpResponse(audio_data, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="tts-output.{output_format}"'
                return response
                
            except Exception as e:
                messages.error(request, _(f"Error generating speech: {str(e)}"))
    else:
        form = TextToSpeechForm()
    
    return render(request, 'openai_integration/text_to_speech.html', {
        'form': form
    })


@login_required
def speech_to_text_view(request):
    """
    View for speech-to-text transcription.
    """
    if request.method == 'POST':
        form = SpeechToTextForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                audio_file = request.FILES['audio_file']
                language = form.cleaned_data['language'] or None
                
                transcription = transcribe_audio(audio_file, language)
                
                # If AJAX request, return JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'transcription': transcription
                    })
                
                # Pass the result to the template
                return render(request, 'openai_integration/speech_to_text.html', {
                    'form': form,
                    'transcription': transcription
                })
                
            except Exception as e:
                messages.error(request, _(f"Error transcribing audio: {str(e)}"))
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=400)
    else:
        form = SpeechToTextForm()
    
    return render(request, 'openai_integration/speech_to_text.html', {
        'form': form
    })


@login_required
@csrf_exempt
def ajax_file_upload(request):
    """
    AJAX endpoint for file uploads from the chat interface.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    try:
        file_obj = request.FILES['file']
        purpose = request.POST.get('purpose', 'assistants')
        
        openai_file = upload_file(file_obj, purpose, request.user)
        
        # If message_id is provided, associate the file with the message
        message_id = request.POST.get('message_id')
        if message_id:
            try:
                message = Message.objects.get(id=message_id, conversation__user=request.user)
                MessageOpenAIFile.objects.create(
                    message=message,
                    openai_file=openai_file
                )
            except Message.DoesNotExist:
                pass  # Skip association if message not found or not owned by user
        
        return JsonResponse({
            'success': True,
            'file_id': openai_file.openai_file_id,
            'filename': openai_file.filename,
            'size': openai_file.bytes_size
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@csrf_exempt
def ajax_speech_to_text(request):
    """
    AJAX endpoint for speech-to-text from the chat interface.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if 'audio' not in request.FILES:
        return JsonResponse({'error': 'No audio provided'}, status=400)
    
    try:
        audio_file = request.FILES['audio']
        language = request.POST.get('language')
        
        transcription = transcribe_audio(audio_file, language)
        
        return JsonResponse({
            'success': True,
            'transcription': transcription
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
