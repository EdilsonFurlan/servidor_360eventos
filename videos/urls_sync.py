from django.urls import path
from . import views_sync

urlpatterns = [
    path('download/', views_sync.sync_download, name='sync_download'),
    path('upload/', views_sync.sync_upload, name='sync_upload'),
]
