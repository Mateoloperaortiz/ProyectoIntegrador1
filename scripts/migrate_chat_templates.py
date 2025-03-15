#!/usr/bin/env python3
"""
Script to migrate existing chat templates to use the new unified component-based template.

This script helps with transitioning from the old chat templates to the new
unified component-based template system. It adds a deprecation warning to old templates
and provides instructions for migrating to the new system.
"""

import os
import re
import argparse
from pathlib import Path

# Templates to be migrated
TEMPLATE_PATHS = [
    "interaction/templates/interaction/direct_chat.html",
    "interaction/templates/interaction/direct_chat_enhanced.html",
    "interaction/templates/interaction/direct_chat_fixed.html",
    "interaction/templates/interaction/direct_chat_minimal.html",
    "interaction/templates/interaction/direct_chat_fixed_alignment.html",
    "interaction/templates/interaction/direct_chat_no_debug.html",
    "interaction/templates/interaction/direct_chat_new.html",
]

# Deprecation warning to add to old templates
DEPRECATION_WARNING = """
{# 
DEPRECATION WARNING: 
This template is deprecated and will be removed in a future version. 
Please use the unified template system instead:

{% extends 'base.html' %}
{% load static %}

{% block title %}Chat - Inspire AI{% endblock %}

{% block content %}
{% include "core/partials/chat/chat_base.html" with 
    conversation=conversation 
    messages_list=messages_list 
    form_action="interaction:direct_chat_message"
    theme="default"  # or "minimal" or "modern"
    show_debug=False
    chat_header_title="Chat with AI Assistant"
%}
{% endblock %}

For more options, see the documentation in 
/core/templates/core/partials/chat/chat_base.html
#}

"""

def add_deprecation_warning(template_path, base_dir):
    """Add a deprecation warning to the specified template."""
    full_path = os.path.join(base_dir, template_path)
    if not os.path.exists(full_path):
        print(f"Warning: Template {template_path} does not exist")
        return False
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    # Check if the deprecation warning is already present
    if "DEPRECATION WARNING" in content:
        print(f"Skipping {template_path}: Deprecation warning already present")
        return False
    
    # Add the warning at the top of the template
    content = DEPRECATION_WARNING + content
    
    # Write the updated content back to the file
    with open(full_path, 'w') as f:
        f.write(content)
    
    print(f"Added deprecation warning to {template_path}")
    return True

def create_unified_version(template_path, base_dir):
    """Create a unified version of the template in the unified/ directory."""
    # Create the target directory if it doesn't exist
    unified_dir = os.path.join(base_dir, "interaction/templates/interaction/unified")
    os.makedirs(unified_dir, exist_ok=True)
    
    # Determine the template name
    template_name = os.path.basename(template_path)
    base_name = os.path.splitext(template_name)[0]
    
    # Create the unified template path
    unified_path = os.path.join(unified_dir, f"{base_name}_unified.html")
    
    # If the file already exists, don't overwrite it
    if os.path.exists(unified_path):
        print(f"Skipping creation of {unified_path}: File already exists")
        return False
    
    # Determine theme based on template name
    theme = "default"
    if "minimal" in base_name:
        theme = "minimal"
    elif "enhanced" in base_name:
        theme = "modern"
    
    # Determine debug setting based on template name
    show_debug = "True" if "debug" in base_name else "False"
    
    # Create the unified template content
    unified_content = f"""{% extends 'base.html' %}
{% load static %}

{% block title %}Chat - Inspire AI{% endblock %}

{% block content %}
{{% include "core/partials/chat/chat_base.html" with 
    conversation=conversation 
    messages_list=messages_list 
    form_action="interaction:direct_chat_message"
    theme="{theme}"
    show_debug={show_debug}
    chat_header_title="Chat with AI Assistant"
%}}
{% endblock %}
"""
    
    # Write the unified template
    with open(unified_path, 'w') as f:
        f.write(unified_content)
    
    print(f"Created unified version at {unified_path}")
    return True

def main():
    """Main function to add deprecation warnings and create unified templates."""
    parser = argparse.ArgumentParser(description="Migrate chat templates to the new unified system")
    parser.add_argument("--base-dir", default=".", help="Base directory of the project")
    parser.add_argument("--dry-run", action="store_true", help="Don't make any changes, just show what would be done")
    args = parser.parse_args()
    
    # Expand the base directory to an absolute path
    base_dir = os.path.abspath(args.base_dir)
    
    print(f"Using base directory: {base_dir}")
    print(f"Dry run: {args.dry_run}")
    
    if args.dry_run:
        print("\nTemplates that would be processed:")
        for template_path in TEMPLATE_PATHS:
            full_path = os.path.join(base_dir, template_path)
            exists = os.path.exists(full_path)
            print(f"  {'✓' if exists else '✗'} {template_path}")
        return
    
    # Add deprecation warnings to existing templates
    warning_count = 0
    for template_path in TEMPLATE_PATHS:
        if add_deprecation_warning(template_path, base_dir):
            warning_count += 1
    
    # Create unified versions of the templates
    unified_count = 0
    for template_path in TEMPLATE_PATHS:
        if create_unified_version(template_path, base_dir):
            unified_count += 1
    
    print(f"\nSummary: Added {warning_count} deprecation warnings and created {unified_count} unified templates")
    print("\nNext steps:")
    print("1. Update views to use the unified templates in interaction/templates/interaction/unified/")
    print("2. Test thoroughly to ensure the new templates work correctly")
    print("3. Eventually remove the deprecated templates when they are no longer used")

if __name__ == "__main__":
    main()