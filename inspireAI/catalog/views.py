# catalog/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import IA

class IAListView(ListView):
    model = IA
    template_name = 'catalog/ia_list.html'
    context_object_name = 'ias'

    def get_queryset(self):
        queryset = IA.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '')
        cat_slug = self.request.GET.get('category', '')

        # Filtro por texto
        if q:
            queryset = queryset.filter(name__icontains=q) | queryset.filter(description__icontains=q)

        # Filtro por categoría
        if cat_slug:
            queryset = queryset.filter(category__slug=cat_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Category
        context['categories'] = Category.objects.all()
        return context

class IADetailView(DetailView):
    model = IA
    template_name = 'catalog/ia_detail.html'
    context_object_name = 'ia'

class IACreateView(CreateView):
    model = IA
    fields = ['name', 'description', 'category']
    template_name = 'catalog/ia_form.html'
    success_url = reverse_lazy('catalog:ia_list')

class IAUpdateView(UpdateView):
    model = IA
    fields = ['name', 'description', 'category']
    template_name = 'catalog/ia_form.html'
    success_url = reverse_lazy('catalog:ia_list')

class IADeleteView(DeleteView):
    model = IA
    template_name = 'catalog/ia_confirm_delete.html'
    success_url = reverse_lazy('catalog:ia_list')
