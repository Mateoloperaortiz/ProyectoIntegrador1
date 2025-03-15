# Unified Chat Template System

This directory contains a component-based chat template system designed to eliminate duplicate code and provide a flexible, configurable chat interface for the application.

## Architecture

The system is organized into the following parts:

1. **Base Template**: `chat_base.html` - The main template that loads all components
2. **Components**: Individual parts of the chat interface in the `components/` directory
3. **Themes**: CSS themes that can be applied to change the visual style
4. **JavaScript**: Shared JavaScript functionality to handle the interactive elements

## Components

The following components are available:

- `header.html`: The chat header with title and status indicator
- `message_list.html`: The list of chat messages
- `message_bubble.html`: Individual message bubbles
- `input_area.html`: The message input and send button
- `typing_indicator.html`: Animation showing when the AI is "typing"
- `debug_panel.html`: Collapsible panel with debug information

## Usage

To use the unified chat template in your views, include it with template parameters:

```django
{% include "core/partials/chat/chat_base.html" with 
    # Required variables
    conversation=conversation 
    messages_list=messages_list 
    form_action="interaction:direct_chat_message"
    
    # Optional configuration
    theme="default"
    show_debug=False
    chat_header_title="Chat with AI Assistant"
    show_status=True
    show_empty_state=True
    enable_markdown=True
    enable_keyboard_shortcuts=True
    enable_auto_scroll=True
    enable_auto_focus=True
%}
```

## Configuration Options

The base template accepts the following configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `theme` | Visual theme to apply (default, minimal, modern) | "default" |
| `show_debug` | Whether to show debug information | False |
| `collapsible_debug` | Whether debug panel should be collapsible | True |
| `container_height` | Height of the chat container | "calc(100vh - 64px)" |
| `chat_header_title` | Title to display in the chat header | "Chat with AI Assistant" |
| `show_status` | Whether to show online status indicator | True |
| `show_empty_state` | Whether to show empty state when no messages | True |
| `enable_markdown` | Whether to enable markdown processing | True |
| `enable_keyboard_shortcuts` | Whether to enable keyboard shortcuts | True |
| `enable_auto_scroll` | Whether to enable auto-scrolling | True |
| `enable_auto_focus` | Whether to auto-focus input on load | True |
| `debug` | Whether to enable debug logging | False |

## View Integration

The template system is designed to work with the existing views. In your view, render the template with appropriate context:

```python
def direct_chat(request, template='interaction/unified/direct_chat.html'):
    # View logic...
    
    return render(request, template, {
        'conversation': conversation,
        'conversation_id': conversation_id,
        'messages_list': messages_list,
        'form': form,
        'form_action': 'interaction:direct_chat_message'
    })
```

## Example Templates

The interaction app includes example templates that demonstrate different configurations:

- `direct_chat.html`: Default configuration
- `modern_chat.html`: Modern theme with animations
- `minimal_debug_chat.html`: Minimal theme with debug panel
- `enhanced_chat.html`: Enhanced version with debug info

## Backward Compatibility

The system supports backward compatibility with existing views through:

- Multiple message list variables (`messages_list`, `chat_messages`, `messages`)
- Support for the Django form instance (`form`)
- Support for AI tool information (`ai_tool`, `ai_tools`)