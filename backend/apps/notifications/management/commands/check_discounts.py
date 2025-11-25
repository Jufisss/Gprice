from django.core.management.base import BaseCommand
from apps.notifications.service import discount_service

class Command(BaseCommand):
    help = 'Check discounts and send Telegram notifications'
    
    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking for discount notifications...')
        
        notifications_sent = discount_service.check_discounts()
        
        if notifications_sent > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Sent {notifications_sent} discount notifications')
            )
        else:
            self.stdout.write('ℹ️ No discount notifications to send')