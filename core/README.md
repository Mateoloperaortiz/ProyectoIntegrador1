# Core App

This app contains centralized functionality used across the entire project.

## Utility Functions

The core app provides utility functions that are used by multiple other apps, helping to eliminate code duplication.

### Logging Utilities (`logging_utils.py`)

These utilities provide consistent logging and audit functionality across the application:

- `get_logger(name)` - Get a configured logger instance
- `LoggingMixin` - Class mixin that adds logging capabilities to a class
- `log_exception(logger, exc, message, extra)` - Log an exception with context
- `log_api_request(...)` - Log API request details consistently
- `redact_sensitive_data(data)` - Safely redact sensitive information from logs
- `get_client_ip(request)` - Get client IP address from request
- `log_user_activity(...)` - Log user actions for audit purposes

### General Utilities (`utils.py`)

General purpose utilities for the entire application:

- `safe_json_loads(json_str, default)` - Safely parse JSON with a default fallback
- `format_file_size(size_in_bytes)` - Format file sizes in human-readable format
- `is_valid_image_extension(filename)` - Check if a file has a valid image extension
- `truncate_text(text, max_length, suffix)` - Truncate text to a specific length
- `create_unique_slug(...)` - Create a unique slug for a model instance
- `call_api(...)` - Generic API call function with logging and error handling
- `format_conversation_for_download(...)` - Format conversations for export

## Context Processors

Context processors add variables to the template context:

- `site_settings` - Adds global site settings to all templates

## Templates

The core app provides base templates and common components that other apps can extend and include.

## Middleware Integration

The core logging utilities are integrated with the request logging middleware in `inspireIA.middleware`.