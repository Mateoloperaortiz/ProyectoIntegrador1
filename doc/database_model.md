# Database Model Documentation

## Entity-Relationship Diagram

```
+---------------+       +---------------+       +---------------+
|  CustomUser   |       |    AITool     |       | Conversation  |
+---------------+       +---------------+       +---------------+
| id            |       | id            |       | id            |
| email         |       | name          |       | user          |----+
| password      |       | slug          |       | tool          |--+ |
| bio           |       | description   |       | title         | | |
| profile_pic   |       | provider      |       | created_at    | | |
| date_joined   |----+  | website_url   |  +----| updated_at    | | |
+---------------+    |  | category      |  |    +---------------+ | |
                     |  | image         |  |                      | |
                     |  | created_at    |  |    +---------------+ | |
                     |  | updated_at    |  |    |    Message    | | |
                     |  | is_featured   |  |    +---------------+ | |
                     |  | popularity    |  |    | id            | | |
                     |  | api_type      |  |    | conversation  |<+ |
                     |  | api_endpoint  |  |    | is_from_user  |   |
                     |  | api_model     |  |    | content       |   |
                     |  +---------------+  |    | timestamp     |   |
                     |                     |    +---------------+   |
                     |                     |                        |
                     |  +---------------+ |                        |
                     |  |    Rating     | |                        |
                     |  +---------------+ |                        |
                     +->| id            | |                        |
                     |  | user          |-+                        |
                     |  | tool          |-+                        |
                     |  | stars         |                          |
                     |  | comment       |                          |
                     |  | created_at    |                          |
                     |  +---------------+                          |
                     |                                             |
                     |  +---------------+                          |
                     |  |   Favorite    |                          |
                     |  +---------------+                          |
                     +->| id            |                          |
                        | user          |--------------------------+
                        | tool          |-+
                        | added_at      |
                        +---------------+
```

## Models Description

### User Model (users app)
- `CustomUser` - extends Django's AbstractUser
  - Fields: email (unique), bio, profile_picture, date_joined
  - Authentication uses email instead of username
  - Related to: Conversation, Favorite, Rating (via ForeignKey)

### Catalog Models (catalog app)
- `AITool`
  - Fields: name, slug (unique), description, provider, website_url, category, image, created_at, updated_at, is_featured, popularity
  - API fields: api_type, api_endpoint, api_model
  - Methods: get_average_rating() calculates/stores tool popularity based on ratings
  - Related to: Rating, Conversation, Favorite (via ForeignKey)

- `Rating`
  - Fields: id (UUID), user (FK to CustomUser), tool (FK to AITool), stars (1-5), comment, created_at
  - Constraints: unique_together (user, tool) - one rating per tool per user

### Interaction Models (interaction app)
- `Conversation`
  - Fields: id (UUID), user (FK to CustomUser), tool (FK to AITool), title, created_at, updated_at
  - Methods: Auto-generates title from first message if not provided
  - Related to: Message (via ForeignKey)

- `Message`
  - Fields: conversation (FK to Conversation), is_from_user (boolean), content, timestamp
  - Represents individual messages in a conversation

- `Favorite`
  - Fields: user (FK to CustomUser), tool (FK to AITool), added_at
  - Constraints: unique_together (user, tool) - can't favorite same tool twice

## Database Configuration

```python
# From settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom user model configuration
AUTH_USER_MODEL = 'users.CustomUser'
```

## Constants Used in the Database

### Categories (from catalog/constants.py)
- Text, Image, Video, Audio, Code, Chat, Search, Data Analysis, Translation, Summarization, Other

### API Types (from catalog/constants.py)
- OpenAI, HuggingFace, Anthropic, Google, Custom, None

### Rating System
- 1-5 stars numeric rating scale
