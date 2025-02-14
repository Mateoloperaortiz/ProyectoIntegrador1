from django.shortcuts import render
from .models import AITool

# Vista para la página principal
def home(request):
    return render(request, 'catalog/home.html')  # Redirige a home.html

# Vista para la página de catálogo
def catalog(request):
    searchTerm = request.GET.get('searchAITool')
    if searchTerm:
        ai_tools = AITool.objects.filter(name__icontains=searchTerm)
    else:
        ai_tools = AITool.objects.all()
    
    return render(request, 'catalog/catalog.html', {'searchTerm': searchTerm, 'ai_tools': ai_tools})


CATEGORIES = ["Transcription", "Image Generator", "Word Processor"]  # Categorías predefinidas

def catalog_view(request):
    searchTerm = request.GET.get('searchAITool')
    category = request.GET.get('category')  # Obtiene la categoría desde la URL

    ai_tools = AITool.objects.all()

    if category in CATEGORIES:
        ai_tools = ai_tools.filter(category=category)  # Filtra por categoría
    if searchTerm:
        ai_tools = ai_tools.filter(name__icontains=searchTerm)  # Aplica búsqueda si hay término

    return render(request, 'catalog/catalog.html', {
        'ai_tools': ai_tools,
        'categories': CATEGORIES,
        'searchTerm': searchTerm
    })

