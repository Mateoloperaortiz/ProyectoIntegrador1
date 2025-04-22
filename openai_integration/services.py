import os
import base64
import json
from openai import AzureOpenAI, AsyncAzureOpenAI
from .models import OpenAIFile, OpenAIThread, MessageOpenAIFile
from interaction.models import Conversation, Message


def get_openai_client():
    """
    Create and return an Azure OpenAI client with environment variables.
    """
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
    api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
    
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version
    )
    return client


async def get_async_openai_client():
    """
    Create and return an AsyncAzureOpenAI client with environment variables.
    """
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
    api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version
    )
    return client


def upload_file(file_obj, purpose="assistants", user=None):
    """
    Upload a file to Azure OpenAI and store its metadata.
    
    Args:
        file_obj: File object (Django UploadedFile or similar)
        purpose: The purpose of the file ('assistants', 'fine-tune', etc.)
        user: Django User object
        
    Returns:
        The OpenAIFile model instance with metadata
    """
    client = get_openai_client()
    
    # Upload to OpenAI
    response = client.files.create(
        file=file_obj,
        purpose=purpose
    )
    
    # Create record in our database
    openai_file = OpenAIFile.objects.create(
        user=user,
        openai_file_id=response.id,
        filename=file_obj.name,
        purpose=purpose,
        bytes_size=response.bytes
    )
    
    return openai_file


def retrieve_file(file_id):
    """
    Retrieve file metadata from OpenAI.
    
    Args:
        file_id: OpenAI File ID
        
    Returns:
        File details
    """
    client = get_openai_client()
    return client.files.retrieve(file_id=file_id)


def retrieve_file_content(file_id):
    """
    Retrieve the contents of a file uploaded to OpenAI.
    
    Args:
        file_id: OpenAI File ID
        
    Returns:
        File content
    """
    client = get_openai_client()
    return client.files.content(file_id=file_id)


def delete_file(file_id):
    """
    Delete a file from OpenAI and remove our database record.
    
    Args:
        file_id: OpenAI File ID
        
    Returns:
        Deletion status
    """
    client = get_openai_client()
    response = client.files.delete(file_id=file_id)
    
    # Delete our database record if successful
    if response.deleted:
        try:
            OpenAIFile.objects.filter(openai_file_id=file_id).delete()
        except Exception as e:
            print(f"Error deleting local file record: {e}")
    
    return response


def list_files(purpose=None, limit=100):
    """
    List files uploaded to OpenAI.
    
    Args:
        purpose: Optional filter by purpose
        limit: Maximum number of files to return
        
    Returns:
        List of file metadata
    """
    client = get_openai_client()
    
    if purpose:
        return client.files.list(purpose=purpose, limit=limit)
    else:
        return client.files.list(limit=limit)


def get_or_create_thread(conversation):
    """
    Get or create an OpenAI thread for a conversation.
    
    Args:
        conversation: Conversation model instance
        
    Returns:
        Thread ID
    """
    # First, check if the conversation already has a thread
    try:
        thread = OpenAIThread.objects.get(conversation=conversation)
        return thread.thread_id
    except OpenAIThread.DoesNotExist:
        # Create a new thread
        client = get_openai_client()
        response = client.beta.threads.create()
        
        # Store the thread ID in our database
        thread = OpenAIThread.objects.create(
            conversation=conversation,
            thread_id=response.id
        )
        
        return thread.thread_id


def add_message_to_thread(thread_id, content, files=None, is_user=True):
    """
    Add a message to an OpenAI thread.
    
    Args:
        thread_id: OpenAI Thread ID
        content: Message content
        files: List of OpenAI File IDs
        is_user: Whether the message is from the user (True) or assistant (False)
        
    Returns:
        Message object
    """
    client = get_openai_client()
    
    # Set the role based on is_user
    role = "user" if is_user else "assistant"
    
    # Add the file IDs if present
    file_ids = files if files else []
    
    # Create the message
    response = client.beta.threads.messages.create(
        thread_id=thread_id,
        role=role,
        content=content,
        file_ids=file_ids
    )
    
    return response


def create_thread_run(thread_id, assistant_id, instructions=None, tools=None):
    """
    Create a run to execute an assistant on a thread.
    
    Args:
        thread_id: OpenAI Thread ID
        assistant_id: OpenAI Assistant ID
        instructions: Optional override instructions
        tools: Optional tools to enable
        
    Returns:
        Run object
    """
    client = get_openai_client()
    
    params = {
        "thread_id": thread_id,
        "assistant_id": assistant_id
    }
    
    if instructions:
        params["instructions"] = instructions
    
    if tools:
        params["tools"] = tools
    
    response = client.beta.threads.runs.create(**params)
    
    return response


def list_thread_messages(thread_id, limit=100):
    """
    List messages in a thread.
    
    Args:
        thread_id: OpenAI Thread ID
        limit: Maximum number of messages to return
        
    Returns:
        List of messages
    """
    client = get_openai_client()
    return client.beta.threads.messages.list(
        thread_id=thread_id,
        limit=limit
    )


async def stream_chat_completion(messages, tool=None, image_url=None):
    """
    Stream a chat completion from Azure OpenAI.
    
    Args:
        messages: List of message objects (role, content)
        tool: AITool model instance (for parameters)
        image_url: Optional base64 image URL
        
    Returns:
        Async generator of completion chunks
    """
    api_version = os.environ.get('AZURE_OPENAI_API_VERSION')
    deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT')
    
    # Get parameters from tool or use defaults
    max_tokens = getattr(tool, 'max_completion_tokens', 800)
    temperature = getattr(tool, 'temperature', 1.0)
    top_p = getattr(tool, 'top_p', 1.0)
    frequency_penalty = getattr(tool, 'frequency_penalty', 0.0)
    presence_penalty = getattr(tool, 'presence_penalty', 0.0)
    
    async with await get_async_openai_client() as client:
        if image_url and image_url.startswith('data:image'):
            # Handle image input
            user_message = messages[-1]['content']  # Extract the last user message
            input_content = [
                {"type": "text", "text": user_message},
                {
                    "type": "image_url",
                    "image_url": {"url": image_url, "detail": "auto"}
                }
            ]
            # Reconstruct messages with the multimodal content
            messages = messages[:-1] + [{"role": "user", "content": input_content}]
        
        stream = await client.chat.completions.create(
            model=deployment,
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        return stream


def generate_tts(text, voice="alloy", output_format="mp3"):
    """
    Generate text-to-speech audio.
    
    Args:
        text: The text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        output_format: Output format (mp3 or opus)
        
    Returns:
        Audio data
    """
    client = get_openai_client()
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format=output_format
    )
    
    return response.content


def transcribe_audio(audio_file, language="en"):
    """
    Transcribe audio to text.
    
    Args:
        audio_file: Audio file object
        language: Optional language code
        
    Returns:
        Transcription text
    """
    client = get_openai_client()
    
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=language
    )
    
    return response.text
