from .models import AITool
from django.shortcuts import render, get_object_or_404


def home(request):
    return render(request, 'catalog/home.html')  

def catalog(request):
    searchTerm = request.GET.get('searchAITool')
    if searchTerm:
        ai_tools = AITool.objects.filter(name__icontains=searchTerm)
    else:
        ai_tools = AITool.objects.all()
    
    return render(request, 'catalog/catalog.html', {'searchTerm': searchTerm, 'ai_tools': ai_tools})

def presentationAI(request, id):
    ai_tool = get_object_or_404(AITool, id=id)  # Se obtiene la IA específica
    return render(request, 'catalog/presentationAI.html', {'ai_tool': ai_tool})



CATEGORIES = ["Transcription", "Image Generator", "Word Processor"]  

def catalog_view(request):
    searchTerm = request.GET.get('searchAITool')
    category = request.GET.get('category')  

    ai_tools = AITool.objects.all()

    if category in CATEGORIES:
        ai_tools = ai_tools.filter(category=category) 
    if searchTerm:
        ai_tools = ai_tools.filter(name__icontains=searchTerm)  

    return render(request, 'catalog/catalog.html', {
        'ai_tools': ai_tools,
        'categories': CATEGORIES,
        'searchTerm': searchTerm
    })

