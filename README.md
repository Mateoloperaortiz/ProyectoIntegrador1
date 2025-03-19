# InspireAI: AI Tools Discovery Platform

![InspireAI Logo](static/images/logo.png)

InspireAI is a comprehensive web application built with Django that serves as a centralized hub for discovering, accessing, and interacting with various artificial intelligence tools. It provides users with a catalog of AI tools, allows them to interact with integrated AI services, and offers features such as user accounts, ratings, favorites, and conversations.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

## Features

- **AI Tools Catalog**: Browse and search through a comprehensive collection of AI tools organized by categories
- **User Accounts**: Register, login, and manage your profile with personalized recommendations
- **AI Interaction**: Chat directly with AI tools that have API integration within the application
- **Rating System**: Rate and review AI tools to share your experiences with other users
- **Favorites**: Save your favorite AI tools for quick access
- **Search & Filtering**: Find tools by name, category, functionality, or popularity
- **Responsive Design**: Modern UI that works seamlessly across devices of all sizes

## Requirements

- Python 3.9+
- Django 5.1.7
- Pillow (for image processing)
- Django-Bootstrap5 (for Bootstrap integration)
- SQLite (default database, can be configured to use other databases)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/inspireai.git
cd inspireai
```

2.Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3.Install dependencies:

```bash
pip install -r requirements.txt
```

4.Apply migrations:

```bash
python manage.py migrate
```

5.Create a superuser:

```bash
python manage.py createsuperuser
```

6.Import AIs

```bash
python manage.py populate_ai_tools
```

7.Run the development server:

```bash
python manage.py runserver
```

8.Access the application at <http://127.0.0.1:8000/>

## Usage

### Admin Interface

- Access the admin interface at <http://127.0.0.1:8000/admin/>
- Use the superuser credentials created during installation
- Add, modify, or delete AI tools, users, categories, and other data

### User Interface

- **Home Page**: Discover featured AI tools and platform highlights
- **Catalog**: Browse all available AI tools with filtering options
- **Tool Detail**: View detailed information and interact with specific AI tools
- **Profile**: Manage your account, favorites, and conversation history
- **Conversations**: Chat with AI tools that have API integration

## Project Structure

The project follows Django's MVC architecture with the following main apps:

- **catalog**: Handles AI tool listings, categories, and tool details
- **users**: Manages user accounts, registration, authentication, and profiles
- **interaction**: Handles user interactions with AI tools (conversations, ratings, favorites)

Key directories:

- **templates/**: HTML templates organized by app
- **static/**: CSS, JavaScript, and images
- **media/**: User-uploaded content
- **inspireai/**: Main project configuration

## Technologies Used

- **Backend**: Django 5.1.7, Python 3.9+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (default)
- **UI Components**: Django-Bootstrap5
- **Image Processing**: Pillow
- **Icons**: Font Awesome

## Development Guidelines

- Follow PEP 8 standards for Python code
- Use Django's class-based views where appropriate
- Maintain separation of concerns between apps
- Write docstrings for all classes and functions
- Follow the code style conventions in CLAUDE.md

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
