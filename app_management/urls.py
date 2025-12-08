from django.urls import path
from . import views

urlpatterns = [
    path('latest-version/', views.latest_version, name='latest-version'),
]
