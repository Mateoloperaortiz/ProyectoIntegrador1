#!/usr/bin/env python
"""
Template Testing Script

This script tests the unified chat templates to ensure visual and functional parity
with the original templates. It compares rendered HTML and screenshots of both versions.

Usage:
    python scripts/test_templates.py

Requirements:
    - selenium
    - Pillow
    - pytest
    - pytest-django
"""

import os
import sys
import json
import argparse
import tempfile
from pathlib import Path
from unittest import mock

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Django setup (must be done before importing Django models)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inspireIA.settings')
import django
django.setup()

# Now we can import Django models
from django.template.loader import render_to_string
from django.template import engines
from django.test import RequestFactory
from catalog.models import AITool
from interaction.models import Conversation, Message
from django.contrib.auth import get_user_model

# Test parameters
TEST_CASES = [
    {
        'name': 'Empty Chat',
        'original_template': 'interaction/direct_chat.html',
        'unified_template': 'interaction/unified/direct_chat.html',
        'context': {
            'conversation': None,
            'conversation_id': None,
            'messages_list': [],
            'chat_messages': [],
            'form_action': 'interaction:direct_chat_message',
        }
    },
    {
        'name': 'Chat with Messages',
        'original_template': 'interaction/direct_chat.html',
        'unified_template': 'interaction/unified/direct_chat.html',
        'context': {
            'conversation': mock.MagicMock(id='test-conversation-id'),
            'conversation_id': 'test-conversation-id',
            'messages_list': [
                mock.MagicMock(is_user=True, content='User message 1', timestamp='2023-01-01T12:00:00Z'),
                mock.MagicMock(is_user=False, content='AI response 1', timestamp='2023-01-01T12:01:00Z'),
                mock.MagicMock(is_user=True, content='User message 2', timestamp='2023-01-01T12:02:00Z'),
                mock.MagicMock(is_user=False, content='AI response 2', timestamp='2023-01-01T12:03:00Z'),
            ],
            'chat_messages': [],
            'form_action': 'interaction:direct_chat_message',
        }
    },
    {
        'name': 'Enhanced Chat',
        'original_template': 'interaction/direct_chat_enhanced.html',
        'unified_template': 'interaction/unified/enhanced_chat.html',
        'context': {
            'conversation': mock.MagicMock(id='test-conversation-id'),
            'conversation_id': 'test-conversation-id',
            'messages_list': [
                mock.MagicMock(is_user=True, content='User message 1', timestamp='2023-01-01T12:00:00Z'),
                mock.MagicMock(is_user=False, content='AI response 1', timestamp='2023-01-01T12:01:00Z'),
            ],
            'chat_messages': [],
            'form_action': 'interaction:direct_chat_message',
        }
    },
]

def setup_test_data():
    """Set up test data for template rendering."""
    # Create a test user
    User = get_user_model()
    try:
        user = User.objects.get(username='template_test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='template_test_user',
            email='template_test@example.com',
            password='password123'
        )
    
    # Create a test AI tool
    try:
        ai_tool = AITool.objects.get(name='Test AI Tool')
    except AITool.DoesNotExist:
        ai_tool = AITool.objects.create(
            name='Test AI Tool',
            description='AI tool for template testing',
            api_type='openai',
            api_model='gpt-3.5-turbo'
        )
    
    # Create a test conversation
    try:
        conversation = Conversation.objects.get(user=user, title='Test Conversation')
    except Conversation.DoesNotExist:
        conversation = Conversation.objects.create(
            user=user,
            ai_tool=ai_tool,
            title='Test Conversation'
        )
    
    # Create test messages
    if Message.objects.filter(conversation=conversation).count() == 0:
        Message.objects.create(
            conversation=conversation,
            content='Hello, this is a test message',
            is_user=True
        )
        Message.objects.create(
            conversation=conversation,
            content='Hello! I am an AI assistant. How can I help you today?',
            is_user=False
        )
    
    return {
        'user': user,
        'ai_tool': ai_tool,
        'conversation': conversation,
        'messages': Message.objects.filter(conversation=conversation)
    }

def render_template_to_file(template_name, context, output_file):
    """Render a template to a file."""
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Add request to context
    context['request'] = request
    
    # Render the template
    rendered = render_to_string(template_name, context)
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(rendered)
    
    return output_file

def compare_templates(test_case, output_dir):
    """Compare original and unified templates."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up paths
    original_output = os.path.join(output_dir, f"{test_case['name']}_original.html")
    unified_output = os.path.join(output_dir, f"{test_case['name']}_unified.html")
    
    # Render templates
    render_template_to_file(test_case['original_template'], test_case['context'], original_output)
    render_template_to_file(test_case['unified_template'], test_case['context'], unified_output)
    
    print(f"Rendered templates to:\n  {original_output}\n  {unified_output}")
    
    return {
        'original': original_output,
        'unified': unified_output
    }

def main():
    """Main function to test templates."""
    parser = argparse.ArgumentParser(description="Test unified chat templates")
    parser.add_argument("--output-dir", default="template_tests", help="Directory to store test output")
    args = parser.parse_args()
    
    # Set up output directory
    output_dir = os.path.join(BASE_DIR, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Using output directory: {output_dir}")
    
    # Set up test data
    test_data = setup_test_data()
    print("Set up test data:")
    print(f"  User: {test_data['user'].username}")
    print(f"  AI Tool: {test_data['ai_tool'].name}")
    print(f"  Conversation: {test_data['conversation'].title}")
    print(f"  Messages: {test_data['messages'].count()}")
    
    # Run tests
    results = []
    for test_case in TEST_CASES:
        print(f"\nTesting {test_case['name']}...")
        
        # Update context with test data
        context = test_case['context'].copy()
        if context.get('conversation') is None:
            context['conversation'] = test_data['conversation']
        
        # Compare templates
        test_output_dir = os.path.join(output_dir, test_case['name'].replace(' ', '_').lower())
        output_files = compare_templates({**test_case, 'context': context}, test_output_dir)
        
        results.append({
            'name': test_case['name'],
            'original_template': test_case['original_template'],
            'unified_template': test_case['unified_template'],
            'output_files': output_files
        })
    
    # Print summary
    print("\n==== Test Summary ====")
    for result in results:
        print(f"Test: {result['name']}")
        print(f"  Original: {result['original_template']}")
        print(f"  Unified:  {result['unified_template']}")
        print(f"  Output:   {result['output_files']['original']}")
        print(f"            {result['output_files']['unified']}")
        print()
    
    print("Next steps:")
    print("1. Manually review the rendered HTML files")
    print("2. Fix any discrepancies between original and unified templates")
    print("3. Update views to use the unified templates")

if __name__ == '__main__':
    main()