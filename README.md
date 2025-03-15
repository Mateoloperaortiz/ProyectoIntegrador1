# InspireAI - AI Tools Hub

InspireAI is a centralized platform for discovering, accessing, and interacting with various artificial intelligence services. It provides users with detailed information about a wide catalog of AI tools, organized categories, and optimized search functionality.

## Features

- Browse a comprehensive catalog of AI tools
- Search and filter tools by category, provider, and functionality
- View detailed information about each tool
- Rate and review AI tools
- Interact with selected AI tools through a conversation interface
- User profiles with favorites and interaction history
- View statistics about the most popular and highly-rated tools

## Tech Stack

- Django 5.1.7
- Bootstrap 5 (via django-bootstrap5)
- SQLite (development) / PostgreSQL (production)
- Python 3.x

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/inspireai.git
   cd inspireai
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the site at http://127.0.0.1:8000/

## Project Structure

- **catalog**: Core app for AI tools catalog, search, and details
- **users**: Custom user model and authentication functionality
- **interaction**: Handles user interactions like favorites and conversations

## Development Guidelines

- Follow PEP 8 for Python code style
- Write docstrings for all functions, classes, and methods
- Create unit tests for new functionality
- Use Django's ORM for database operations
- Follow model-view-template pattern

## License

This project is licensed under the MIT License - see the LICENSE file for details.