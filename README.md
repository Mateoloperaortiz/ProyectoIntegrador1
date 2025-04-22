<div align="center">
  <img src="static/images/icon.png" alt="InspireAI Logo" width="120" height="120">
  <h1>✨ InspireAI: AI Tools Discovery Platform ✨</h1>
  <p><strong>Discover, Connect, and Interact with AI Tools in One Place</strong></p>

  <p>
    <a href="#features">Features</a> •
    <a href="#demo">Demo</a> •
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#team">Team</a>
  </p>
</div>

## 🎓 University Project
This project was developed as part of **Proyecto Integrador 1** at **EAFIT University** during the 2025-1 academic semester.

## 🚀 About InspireAI

InspireAI is a dynamic web platform that serves as your gateway to the world of artificial intelligence tools. Our mission is to simplify how you discover, access, and interact with various AI services through a unified, user-friendly interface.

Whether you're an AI enthusiast, a student, or a professional looking to leverage AI capabilities, InspireAI provides a centralized hub where you can explore tools across different categories, save your favorites, rate your experiences, and directly interact with integrated AI services.

## ✨ Features

- **🔍 AI Tools Catalog**: Browse and search through a curated collection of AI tools organized by categories
- **👤 User Accounts**: Register, login, and manage your profile with personalized recommendations
- **💬 AI Interaction**: Chat directly with AI tools (OpenAI, , Google) through integrated APIs
- **🖼️ Image Understanding**: Upload and analyze images with AI-powered description and object detection
- **🎬 Video Understanding**: Process videos through file upload or YouTube URLs with transcription and analysis
- **🎵 Audio Understanding**: Analyze audio files with transcription, description, and timestamp references
- **⭐ Rating System**: Rate and review AI tools to share your experiences with other users
- **❤️ Favorites**: Save your favorite AI tools for quick access
- **🔎 Search & Filtering**: Find tools by name, category, functionality, or popularity
- **📱 Responsive Design**: Modern UI that works seamlessly across devices of all sizes
- **✨ Markdown Support**: Rich text formatting in chat with support for headings, lists, links, and more
- **🖥️ Code Syntax Highlighting**: Beautiful code blocks with syntax highlighting for 15+ programming languages
- **🎨 Theme Selection**: Choose from multiple syntax highlighting themes (GitHub, Atom One Dark, Dracula, and more)
- **📋 Code Copy**: One-click copy functionality for code blocks with visual feedback

## 🎮 Demo

### Home Page
Discover featured AI tools and get started with exploring the platform.

### AI Tool Catalog
Browse all available AI tools with filtering options by category, provider, and more.

### Chat Interface
Interact directly with AI tools through our integrated chat interface.

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Mateoloperaortiz/ProyectoIntegrador1.git
cd ProyectoIntegrador1
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.envrc` file in the root directory with the following content:
```
export OPENAI_API_KEY=your_openai_api_key
export =your_huggingface_api_key
```

5. Apply migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Import AI tools:
```bash
python manage.py populate_ai_tools
```

8. Run the server with Daphne (for WebSocket support):
```bash
daphne -b 0.0.0.0 -p 8000 inspireai.asgi:application
```

9. Alternatively, for development without WebSocket features:
```bash
python manage.py runserver
```

10. Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 📚 Usage

### Admin Interface
- Access the admin interface at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Use the superuser credentials created during installation
- Add, modify, or delete AI tools, users, categories, and other data

### User Interface
- **Home Page**: Discover featured AI tools and platform highlights
- **Catalog**: Browse all available AI tools with filtering options
- **Tool Detail**: View detailed information and interact with specific AI tools
- **Profile**: Manage your account, favorites, and conversation history
- **Conversations**: Chat with AI tools that have API integration
  - **Media Understanding**: Upload images, videos, or audio files for AI analysis
  - **YouTube Integration**: Paste YouTube URLs for video analysis
  - **Timestamp References**: Reference specific points in videos or audio using MM:SS format

## 🧩 Project Structure

The project follows Django's MVC architecture with the following main apps:

- **catalog**: Handles AI tool listings, categories, and tool details
- **users**: Manages user accounts, registration, authentication, and profiles
- **interaction**: Handles user interactions with AI tools (conversations, ratings, favorites)

Key directories:
- **templates/**: HTML templates organized by app
- **static/**: CSS, JavaScript, and images
- **media/**: User-uploaded content
- **inspireai/**: Main project configuration

## 💻 Tech Stack

### Backend
- **Django 5.1.7**: High-level Python web framework
- **Django Channels**: WebSocket support for real-time features
- **Python 3.9+**: Programming language
- **SQLite**: Database (default, configurable)
- **Daphne**: ASGI server for WebSocket support

### Frontend
- **HTML5/CSS3**: Markup and styling
- **JavaScript**: Client-side scripting
- **Bootstrap 5**: Frontend framework
- **Font Awesome**: Icon library
- **Marked.js**: Markdown parsing and rendering
- **Highlight.js**: Code syntax highlighting with 15+ language support

### APIs
- **OpenAI API**: For AI chat interactions
- ** API**: For AI model integrations
- **Google Gemini API**: For multimodal AI capabilities including:
  - Image understanding and analysis
  - Video processing (file upload and YouTube URLs)
  - Audio transcription and analysis
  - Text generation and chat

## 👥 Team

<div align="center">
  <table>
    <tr>
      <td align="center">
        <strong>Mateo Lopera</strong><br>
        Developerr<br>
        EAFIT University
      </td>
      <td align="center">
        <strong>Maria Mercedes Olaya</strong><br>
        Developer<br>
        EAFIT University
      </td>
      <td align="center">
        <strong>Sofia Acosta</strong><br>
        Developer<br>
        EAFIT University
      </td>
    </tr>
  </table>
</div>

## 📝 Development Guidelines

- Follow PEP 8 standards for Python code
- Use Django's class-based views where appropriate
- Maintain separation of concerns between apps
- Write docstrings for all classes and functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <p>Made with ❤️ at EAFIT University | Proyecto Integrador 1 | 2025-1</p>
</div>
