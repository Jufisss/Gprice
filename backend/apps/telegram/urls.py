# apps/telegram/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.connect_telegram, name='connect_telegram'),
    path('status/', views.get_telegram_status, name='telegram_status'),
    path('disconnect/', views.disconnect_telegram, name='disconnect_telegram'),
]