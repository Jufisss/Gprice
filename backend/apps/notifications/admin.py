from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'sent_via_email', 'sent_via_telegram', 'created_at']
    list_filter = ['sent_via_email', 'sent_via_telegram', 'created_at']