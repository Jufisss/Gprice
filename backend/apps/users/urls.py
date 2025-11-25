from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('current-user/', views.current_user, name='current_user'),


    path('telegram/start/', views.start_telegram_verification, name='start_telegram'),
    path('telegram/verify/', views.verify_telegram, name='verify_telegram'),
    path('telegram/disconnect/', views.disconnect_telegram, name='disconnect_telegram'),
    path('telegram/status/', views.get_telegram_status, name='telegram_status'),
]