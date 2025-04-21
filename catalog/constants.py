"""
Constants for the catalog app.
"""

# AI Tool Categories
CATEGORY_CHOICES = [
    ('TEXT', 'Text Generation'),
    ('IMAGE', 'Image Generation'),
    ('VIDEO', 'Video Generation'),
    ('AUDIO', 'Audio Generation'),
    ('CODE', 'Code Generation'),
    ('CHAT', 'Conversational'),
    ('SEARCH', 'Search & Research'),
    ('DATA', 'Data Analysis'),
    ('TRANS', 'Translation'),
    ('SUM', 'Summarization'),
    ('OTHER', 'Other'),
]

# API Types 
API_TYPE_CHOICES = [
    ('OPENAI', 'OpenAI API'),
    ('HUGGINGFACE', 'Hugging Face API'),
    ('ANTHROPIC', 'Anthropic API'),
    ('GOOGLE', 'Google AI API'),
    ('CUSTOM', 'Custom API'),
    ('NONE', 'No API Integration'),
    ('GEMINI', 'Google Gemini API'),
]

# Rating Choices (1-5 stars)
RATING_CHOICES = [
    (1, '1 - Poor'),
    (2, '2 - Fair'),
    (3, '3 - Good'),
    (4, '4 - Very Good'),
    (5, '5 - Excellent'),
]