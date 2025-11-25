from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import requests
import json
from apps.games.models import Game, Wishlist
from apps.notifications.models import Notification

@shared_task
def check_game_prices():
    """Периодическая проверка цен игр в вишлистах"""
    print("Запуск проверки цен игр...")
    
    # Здесь будет логика проверки цен
    # Пока просто заглушка
    wishlist_items = Wishlist.objects.all().select_related('game', 'user')
    
    for item in wishlist_items:
        # Проверяем достигнуты ли целевые цены/скидки
        game = item.game
        should_notify = False
        message = ""
        
        if item.target_price and game.current_price and game.current_price <= item.target_price:
            should_notify = True
            message = f"Игра {game.name} достигла целевой цены! Текущая цена: {game.current_price}€"
        
        elif item.target_discount and game.discount_percent >= item.target_discount:
            should_notify = True
            message = f"Игра {game.name} достигла целевой скидки! Текущая скидка: {game.discount_percent}%"
        
        if should_notify and message:
            # Создаем запись уведомления
            notification = Notification.objects.create(
                user=item.user,
                game=game,
                message=message
            )
            
            # Отправляем уведомления
            send_user_notification.delay(notification.id)

@shared_task
def send_user_notification(notification_id):
    """Отправка уведомления пользователю"""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user
        profile = user.userprofile
        
        # Отправка email
        if profile.email_notifications and user.email:
            send_email_notification.delay(notification.id)
        
        # Отправка в Telegram
        if profile.telegram_notifications and profile.telegram_chat_id:
            send_telegram_notification.delay(notification.id)
            
    except Notification.DoesNotExist:
        print(f"Уведомление {notification_id} не найдено")

@shared_task
def send_email_notification(notification_id):
    """Отправка email уведомления"""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user
        
        subject = f"Steam Wishlist - Уведомление о цене"
        message = f"""
        Здравствуйте, {user.username}!
        
        {notification.message}
        
        Ссылка на игру: {notification.game.store_url}
        
        ---
        Steam Wishlist Bot
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        notification.sent_via_email = True
        notification.save()
        print(f"Email уведомление отправлено пользователю {user.username}")
        
    except Exception as e:
        print(f"Ошибка отправки email: {e}")

@shared_task
def send_telegram_notification(notification_id):
    """Отправка уведомления в Telegram"""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user
        profile = user.userprofile
        
        if not profile.telegram_chat_id:
            return
        
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            print("TELEGRAM_BOT_TOKEN не настроен")
            return
        
        message = f"🎮 Steam Wishlist Alert!\n\n{notification.message}\n\n{notification.game.store_url}"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': profile.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            notification.sent_via_telegram = True
            notification.save()
            print(f"Telegram уведомление отправлено пользователю {user.username}")
        else:
            print(f"Ошибка Telegram API: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Ошибка отправки Telegram: {e}")

@shared_task
def update_game_prices():
    """Обновление цен игр из Steam"""
    print("Запуск обновления цен игр...")
    # Здесь будет логика парсинга актуальных цен
    # Пока просто заглушка
    games_to_update = Game.objects.all()[:5]  # Ограничим для теста
    
    for game in games_to_update:
        # В реальности здесь будет парсинг актуальной цены
        # Сейчас просто имитируем обновление
        print(f"Обновление цены для игры: {game.name}")
    
    print("Обновление цен завершено")