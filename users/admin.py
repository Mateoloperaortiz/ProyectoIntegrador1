from django.contrib import admin
from .models import CustomUser  # Importa tu modelo personalizado

from catalog.models import AITool
# Register your models here.
#admin.site.register(CustomUser)  #



class CustomUserAdmin(admin.ModelAdmin):
    # Incluye un campo de favoritos que no muestre objetos innecesarios
    filter_horizontal = ('favorites',)

    # Muestra los campos que deseas en el formulario del admin
    fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'favorites')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
