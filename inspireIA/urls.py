""" urls.py  in inspireIA project
URL configuration for inspireIA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from catalog import views as catalog_views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main Pages
    path('', catalog_views.HomeView.as_view(), name='home'),
    path('catalog/', catalog_views.CatalogView.as_view(), name='catalog'),
    path('catalog/presentation/<uuid:id>/', catalog_views.AIToolDetailView.as_view(), name='presentationAI'),
    
    # Legacy URLs - can be kept for backward compatibility
    # These use the function-based views that now call the class-based views
    # path('legacy/', catalog_views.home, name='legacy_home'),
    # path('legacy/catalog/', catalog_views.catalog_view, name='legacy_catalog'),
    # path('legacy/catalog/presentation/<uuid:id>/', catalog_views.presentationAI, name='legacy_presentationAI'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add debug toolbar URLs only in debug mode
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
else:
    # In production, add proper Media file serving
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
