# catalog/views.py
from django.views.generic import ListView
from .models import IA

class IAListView(ListView):
    model = IA
    template_name = 'catalog/ia_list.html'
    context_object_name = 'ias'
