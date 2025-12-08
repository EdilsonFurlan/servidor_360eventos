from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, VideoViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]