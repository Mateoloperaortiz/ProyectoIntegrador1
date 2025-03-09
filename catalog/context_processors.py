from catalog.views import CATEGORIES

def ai_categories(request):
    """
    Context processor to make AI tool categories available in all templates.
    """
    return {'categories': CATEGORIES}
