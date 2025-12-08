from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('plataforma/', include('plataforma.urls')),
    path('videos/', include('videos.urls')),
    path('app/', include('app_management.urls')),
    # Rotas de Autenticação
    path('auth/', include('usuarios.urls')),
    path('sync/', include('videos.urls_sync')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)