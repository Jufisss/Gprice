from django.utils import timezone
from apps.games.models import Wishlist
from apps.telegram.bot import notification_bot
import logging

logger = logging.getLogger(__name__)

class DiscountNotificationService:
    def __init__(self):
        self.sent_notifications = set()
    
    def check_discounts(self):
        """Проверяет достижение целевых скидок"""
        try:
            # Ищем элементы вишлиста с привязанными Telegram аккаунтами
            wishlist_items = Wishlist.objects.select_related(
                'user', 'user__userprofile', 'game'
            ).filter(
                user__userprofile__telegram_connected=True,
                target_discount__isnull=False,
                game__discount_percent__isnull=False
            )
            
            notifications_sent = 0
            
            for item in wishlist_items:
                if self._should_send_notification(item):
                    success = self.send_discount_notification(item)
                    if success:
                        notifications_sent += 1
                        # Сохраняем ID отправленного уведомления
                        self.sent_notifications.add(f"{item.id}_{item.game.discount_percent}")
            
            logger.info(f"Sent {notifications_sent} discount notifications")
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error checking discounts: {e}")
            return 0
    
    def _should_send_notification(self, wishlist_item):
        """Проверяет, нужно ли отправлять уведомление"""
        game = wishlist_item.game
        
        # Проверяем условие скидки
        discount_condition = (
            wishlist_item.target_discount and 
            game.discount_percent >= wishlist_item.target_discount
        )
        
        # Проверяем, не отправляли ли уже уведомление для этой комбинации
        notification_key = f"{wishlist_item.id}_{game.discount_percent}"
        already_sent = notification_key in self.sent_notifications
        
        return discount_condition and not already_sent
    
    def send_discount_notification(self, wishlist_item):
        """Отправляет уведомление о скидке"""
        try:
            profile = wishlist_item.user.userprofile
            game = wishlist_item.game
            
            success = notification_bot.send_discount_alert(
                profile.telegram_id,
                game.name,
                game.discount_percent,
                wishlist_item.target_discount,
                game.current_price,
                game.store_url
            )
            
            if success:
                logger.info(f"Discount notification sent to {wishlist_item.user.username}")
                # Обновляем время последнего уведомления
                wishlist_item.last_notification_sent = timezone.now()
                wishlist_item.save()
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending discount notification: {e}")
            return False

# Глобальный экземпляр
discount_service = DiscountNotificationService()