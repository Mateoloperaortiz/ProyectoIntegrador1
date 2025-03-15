# Shared JavaScript Files

This directory contains centralized JavaScript files that are used across multiple apps in the project.

## main.js

The `main.js` file contains common JavaScript functionality used throughout the application. 
It replaces the duplicate versions that were previously located in:

- `/catalog/static/catalog/js/main.js`
- `/users/static/users/js/main.js`

Those files now import this centralized version for backward compatibility.

## Functionality

The main.js file includes the following key functions:

- `initFadeInSections()` - Adds scroll animation to elements
- `initFormValidation()` - Handles client-side form validation
- `initPopularityBars()` - Animates popularity indicators
- `initCategoryFilters()` - Manages category filtering UI
- `initSearchLoading()` - Adds loading state to search forms

## Usage

To use these functions in a template, include the centralized file:

```html
<script src="{% static 'core/js/shared/main.js' %}"></script>
```