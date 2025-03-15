# Base Template Refactoring Documentation

## Problem

The project currently has two separate `base.html` templates:

1. **users/templates/base.html**: A simple base template (93 lines)
2. **catalog/templates/base.html**: A more advanced base template (637 lines) with enhanced styling and features

This duplication leads to:
- Inconsistent user experience across the application
- Maintenance challenges when updating features or styles
- Potential bugs when components differ between templates

## Solution

Consolidate to a single base template located in a central location, using the more advanced `catalog/templates/base.html` as the source since it includes:

1. Better responsive design
2. Advanced styling with custom CSS variables
3. More elaborate navigation
4. Better favicon and font handling
5. Theme support
6. Feedback messaging system
7. CDN fallback mechanisms

## Implementation Steps

### 1. Create a Core Templates Directory Structure

Create a central template directory structure:
```
core/templates/
  base.html
  partials/
    _header.html
    _footer.html
    _messages.html
```

### 2. Move the Enhanced Base Template

Move the enhanced base template from `catalog/templates/base.html` to `core/templates/base.html` with improvements:
- Add more customization hooks via block tags
- Ensure all app-specific references are neutralized
- Maintain all existing functionality

### 3. Update Template References

Create redirect templates that extend the core template:
```html
<!-- catalog/templates/base.html -->
{% extends "core/base.html" %}

<!-- users/templates/base.html -->
{% extends "core/base.html" %}
```

### 4. Update Settings

Ensure Django's template settings include the core templates first in the search path:

```python
# inspireIA/settings/base.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'core/templates'),
            # other template directories
        ],
        # ...
    },
]
```

## Implementation Details

### The New Base Template Structure

```html
{% load static %}
<!DOCTYPE html>
<html lang="{% block html_lang %}es{% endblock %}">
<head>
  <!-- Meta Tags -->
  {% block meta_tags %}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{% block meta_description %}Inspire AI - Discover and interact with the best AI tools{% endblock %}">
  <meta name="keywords" content="{% block meta_keywords %}AI, artificial intelligence, tools, catalog, chat{% endblock %}">
  <meta name="author" content="{% block meta_author %}Inspire AI Team{% endblock %}">
  {% endblock %}
  
  <title>{% block title %}Inspire AI{% endblock %}</title>
  
  <!-- CSS -->
  {% block core_css %}
  <!-- Bootstrap and other core CSS -->
  {% endblock %}
  
  <!-- Custom styles -->
  {% block custom_styles %}{% endblock %}
  
  <!-- Page-specific styles -->
  {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">

  <!-- Header -->
  {% block header %}
  <nav class="navbar navbar-expand-lg navbar-light navbar-custom sticky-top">
    <!-- Navigation content -->
  </nav>
  {% endblock %}

  <!-- Messages -->
  {% block messages %}
  <div class="container py-4">
    {% if messages %}
      <!-- Messages display -->
    {% endif %}
  </div>
  {% endblock %}

  <!-- Main Content -->
  <main>
    <div class="container py-4">
      {% block content %}{% endblock %}
    </div>
  </main>

  <!-- Footer -->
  {% block footer %}
  <footer class="footer">
    <!-- Footer content -->
  </footer>
  {% endblock %}

  <!-- Core Scripts -->
  {% block core_scripts %}
  <!-- Bootstrap and other core scripts -->
  {% endblock %}

  <!-- Custom scripts -->
  {% block custom_scripts %}{% endblock %}
  
  <!-- Page-specific scripts -->
  {% block scripts %}{% endblock %}
</body>
</html>
```

## Migration Path

1. **Phase 1: Create Core Base Template**
   - Create the core base template
   - Test with a few key templates

2. **Phase 2: Add Redirect Templates**
   - Create the redirect templates that extend the core base
   - Test with remaining templates 

3. **Phase 3: Complete Migration**
   - Update all templates to use the core base
   - Remove redundant styles

## Benefits

1. **Consistent UI**: All pages will have a consistent look and feel
2. **Easier Maintenance**: Changes to the base template only need to be made in one place
3. **Better Organization**: Clearer separation of concerns with common elements in core
4. **Enhanced Features**: All pages benefit from the improved styling and utilities