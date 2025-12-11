from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='api_login'),
    path('register/', views.user_register, name='api_register'),
    path('validate-user/', views.validate_user, name='validate_user'),
    path('renovar-assinatura/', views.renovar_assinatura),
    path('video-config/', views.update_video_config, name='update_video_config'), 
]