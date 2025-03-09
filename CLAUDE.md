# CLAUDE.md - Django Project Guide

## Commands
```bash
# Server and database
python manage.py runserver              # Start development server
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py createsuperuser        # Create admin user

# Testing
python manage.py test                   # Run all tests
python manage.py test catalog.tests.TestCase  # Run specific test class
python manage.py test catalog.tests.TestCase.test_method  # Run single test
```

## Code Style Guidelines
- **Imports**: Group in order: standard library, Django, local apps
- **Naming**: Models=CamelCase singular, Views/URLs=lowercase_with_underscores
- **Documentation**: Use docstrings for complex functions
- **Model Fields**: Include field descriptions in comments, define `__str__`
- **Templates**: Use inheritance from base.html, organize by app name
- **Project Structure**: Django app-based organization (inspireIA=config, catalog=main app)
- **Media Files**: Store in media/ai_images directory