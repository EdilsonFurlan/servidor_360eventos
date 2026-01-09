from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, VideoViewSet, SavedEffectViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'effects', SavedEffectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]