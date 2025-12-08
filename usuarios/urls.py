from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='api_login'),
    path('validate-user/', views.validate_user, name='validate_user'),
    path('renovar-assinatura/', views.renovar_assinatura), 
]