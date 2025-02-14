import uuid
from django.db import models

class AITool(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    name = models.CharField(max_length=255)  # Nombre del IA
    provider = models.CharField(max_length=255)  # Proveedor del IA
    endpoint = models.URLField()  # URL del servicio
    category = models.CharField(max_length=100)  # Categoría (Ej: Chatbot, Visión, NLP)
    description = models.TextField()  # Descripción del IA
    popularity = models.IntegerField()  # Popularidad del IA
    image = models.ImageField(upload_to='ai_images/', null=True, blank=True)  # Imagen del IA

    def __str__(self):
        return self.name  # Representación legible en el admin
