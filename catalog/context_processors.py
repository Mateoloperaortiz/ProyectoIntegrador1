from catalog.models import AITool

def ai_categories(request):
    """
    Context processor to make AI tool categories available in all templates.
    """
    categories = [choice[0] for choice in AITool.Category.choices]
    return {'categories': categories}
