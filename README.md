# Inspire AI Project

## Overview
Inspire AI is a web application designed to help students and teachers discover, access, search, and interact with Artificial Intelligence tools. The project is part of "Proyecto Integrador 1" at EAFIT University.

## Main Objectives
- Provide a centralized catalog of AI tools
- Facilitate searching and filtering tools by category and functionality
- Offer detailed information about each tool
- Allow limited interaction with selected external AI APIs

## Technologies
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5.3
- **Database**: SQLite (development), PostgreSQL (production)

## Project Structure
The project follows the standard Django structure, with the following main components:

```
inspireIA/          # Main project
├── catalog/        # Main application
│   ├── migrations/ # Database migrations
│   ├── static/     # Static files (CSS, JS)
│   ├── templates/  # HTML templates
│   ├── admin.py    # Admin panel configuration
│   ├── models.py   # Data models
│   ├── urls.py     # URL configuration
│   └── views.py    # Views and business logic
└── inspireIA/      # Project configuration
    ├── settings/   # Settings for different environments
    ├── urls.py     # Project URLs
    └── wsgi.py     # WSGI configuration for deployment
```

## Implemented Features
- Catalog of AI tools with detailed information
- Search and filtering by category and popularity
- Detail pages for each tool
- Responsive design with Bootstrap

## Getting Started

### Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Start the server: `python manage.py runserver`

### Configuration
- Environment-specific configurations are in `inspireIA/settings/`
- To add AI tools, access the admin panel at `/admin/`

## Contact
For more information about the project, contact the development team.
