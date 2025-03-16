# Component Diagram & Functional Requirements

## System Architecture Diagram

```
+---------------------------+
|                           |
|      Django Framework     |
|                           |
+---------------------------+
            |
            |
            v
+---------------------------+
|      Base Templates       |
|    (Navigation, Layout)   |
+---------------------------+
            |
            |    +--------------------------------------------------+
            |    |                                                  |
            v    v                                                  |
+---------------+        +---------------+        +---------------+ |
|    Users      |        |    Catalog    |        |  Interaction  | |
|   Component   |------->|   Component   |------->|   Component   | |
+---------------+        +---------------+        +---------------+ |
| - Registration|        | - AI Tool List|        | - Conversations| |
| - Login       |        | - Categories  |        | - Messages    | |
| - Profiles    |        | - Search      |        | - Favorites   | |
| - Auth        |        | - Ratings     |        |               | |
+---------------+        +---------------+        +---------------+ |
         |                      |  ^                     |          |
         |                      |  |                     |          |
         |                      |  +---------------------+          |
         |                      |                        |          |
         |                      v                        v          |
         |              +------------------+     +------------------+
         +------------->|   Database Layer |<----|  External APIs  |
                        +------------------+     +------------------+
```

## Components and Functional Requirements

### 1. User Management Component

**Models:** CustomUser

**Views:** RegisterView, CustomLoginView, ProfileView

**Templates:** register.html, login.html, profile.html

**Functional Requirements:**
- FR1: User Registration
- FR2: User Authentication
- FR3: Profile Management
- FR4: User Identification

### 2. Catalog Component

**Models:** AITool, Rating

**Views:** HomeView, CatalogView, ToolDetailView, SearchView, StatisticsView

**Templates:** home.html, catalog.html, tool_detail.html, search_results.html, statistics.html

**Functional Requirements:**
- FR5: AI Tool Catalog
- FR6: Tool Categories
- FR7: Tool Details
- FR8: Tool Ratings
- FR9: Tool Search
- FR10: Tool Statistics

### 3. Interaction Component

**Models:** Conversation, Message, Favorite

**Views:** ConversationListView, ConversationDetailView, start_conversation, send_message

**Templates:** conversation_list.html, conversation_detail.html

**Functional Requirements:**
- FR11: Tool Interaction
- FR12: Conversation Management
- FR13: Favorites Management
- FR14: Chat Interface

## Component Relationships

1. **User → Catalog**
   - Users can browse, search, and rate AI tools
   - Users can view AI tool details and statistics

2. **User → Interaction**
   - Users can start conversations with AI tools
   - Users can manage their conversations
   - Users can favorite AI tools

3. **Catalog → Interaction**
   - AI tools in catalog can be interacted with through conversations
   - AI tools can be favorited by users
   - AI tools display ratings and reviews from users

## Detailed Functional Requirements Implementation

### User Management
- FR1: User Registration - Implemented by RegisterView, CustomUserCreationForm
- FR2: User Authentication - Implemented by CustomLoginView, CustomAuthenticationForm
- FR3: Profile Management - Implemented by ProfileView, ProfileUpdateForm
- FR4: User Identification - CustomUser model with profile picture, username, and email

### Catalog
- FR5: AI Tool Catalog - CatalogView lists all tools with sorting and filtering
- FR6: Tool Categories - CATEGORY_CHOICES constant defines available categories
- FR7: Tool Details - ToolDetailView shows comprehensive tool information
- FR8: Tool Ratings - Rating model and RatingForm enable user ratings and reviews
- FR9: Tool Search - SearchView with SearchForm implements search functionality
- FR10: Tool Statistics - StatisticsView provides analytics on tools and categories

### Interaction
- FR11: Tool Interaction - send_message function enables interaction with AI tools
- FR12: Conversation Management - ConversationListView and ConversationDetailView manage conversations
- FR13: Favorites Management - toggle_favorite function manages user favorites
- FR14: Chat Interface - conversation_detail.html provides chat interface with AI tools

## Cross-Cutting Features

1. **Navigation**
   - base.html implements common navigation UI
   - Includes search bar, user dropdown, and section navigation

2. **Data Visualization**
   - statistics.html displays charts for tool data
   - Tool cards show ratings visually

3. **Responsive Design**
   - Bootstrap-based responsive UI
   - Mobile-friendly templates

4. **API Integration**
   - AITool model includes api_type, api_endpoint, and api_model fields
   - simulate_ai_response function provides fallback responses
