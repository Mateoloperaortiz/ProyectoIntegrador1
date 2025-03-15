# Chat Template Migration Guide

This document details the process of migrating the chat templates to the new unified component-based architecture.

## Overview

We've transitioned from multiple duplicate chat templates to a single unified component-based template system. The new system offers:

1. **Reduced Code Duplication**: Common components are now shared across all chat interfaces
2. **Consistent Styling**: Visual themes provide consistent styling with customization options
3. **Flexible Configuration**: Templates can be configured through parameters without code duplication
4. **Improved Maintainability**: Changes to components automatically apply across all chat interfaces
5. **Better Developer Experience**: Clearly separated components with documented interfaces

## Migration Process

The migration was completed in five steps:

1. **Component Structure**: Created reusable components for each part of the chat interface
   - Header component
   - Message list component
   - Message bubble component
   - Input area component
   - Debug panel component
   - Typing indicator component

2. **Theme System**: Developed a CSS theme system with interchangeable themes
   - Default theme (matches original chat UI)
   - Modern theme (enhanced visuals with animations)
   - Minimal theme (simplified interface for embedding)

3. **Unified Base Template**: Built a configurable base template that loads components based on parameters
   - Supports all context variables from original templates
   - Offers extensive configuration options
   - Maintains backward compatibility with legacy code

4. **View Updates**: Modified view functions to use the new templates
   - Added template parameter to chat view functions
   - Updated render calls to use the new unified templates
   - Added URL routes for different template variants

5. **Testing & Migration**: Created testing tools and migration scripts
   - Added deprecation notices to original templates
   - Created script to test template parity
   - Documented the component system for future developers

## Component Documentation

The unified chat template accepts the following configuration options:

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

## Usage Example

To use the unified template in a view, render it with the appropriate context:

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

To include the template in another template:

```django
{% include "core/partials/chat/chat_base.html" with 
    conversation=conversation 
    messages_list=messages_list 
    form_action="interaction:direct_chat_message"
    theme="default"
    show_debug=False
    chat_header_title="Chat with AI Assistant"
%}
```

## New Template Variations

We now have four pre-configured template variations available:

1. **Default Chat** (`unified/direct_chat.html`): Standard chat interface
2. **Modern Chat** (`unified/modern_chat.html`): Enhanced visuals with animations
3. **Minimal Debug Chat** (`unified/minimal_debug_chat.html`): Minimal theme with debug panel
4. **Enhanced Chat** (`unified/enhanced_chat.html`): Default theme with debug panel

## Migration Testing

To test the migration, we've created a script that:
1. Renders both original and unified templates with the same context
2. Outputs the HTML for comparison
3. Allows visual inspection of differences

Run the test script with:

```
python scripts/test_templates.py
```

## Completion Status

- ✅ Component structure complete
- ✅ Unified base template complete
- ✅ View code updated
- ✅ Old templates deprecated
- ✅ Old templates deleted
- ✅ Template backups created
- ✅ Documentation complete
- ✅ Testing script created

The migration is now complete! All duplicate templates have been removed and replaced with the unified component-based system. Backups of all original templates were created in the `/backups/templates/` directory.

## Next Steps

1. **Monitor and Fix Issues**: Watch for any issues with the unified templates and fix them
2. **Add More Themes**: Create additional visual themes as needed
3. **Enhance Components**: Add more features to components as requirements evolve
4. **Extend to Other Templates**: Apply the component-based approach to other areas of the application