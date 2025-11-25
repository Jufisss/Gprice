import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class NotificationBot:
    def __init__(self):
        self.token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Отправляет сообщение в Telegram"""
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_connection_success(self, chat_id, username):
        """Отправляет сообщение об успешной привязке"""
        text = f"""
✅ <b>Аккаунт успешно привязан!</b>

Привет, {username}!

Теперь вы будете получать уведомления о скидках на игры из вашего вишлиста.

<b>Как это работает:</b>
• Добавляйте игры в вишлист на сайте
• Указывайте желаемую скидку
• Получайте уведомления когда скидка достигнута

Приятных покупок! 🎮
        """
        return self.send_message(chat_id, text)
    
    def send_discount_alert(self, chat_id, game_name, current_discount, target_discount, current_price, store_url):
        """Отправляет уведомление о достижении скидки"""
        text = f"""
🎯 <b>Целевая скидка достигнута!</b>

🎮 <b>{game_name}</b>

📉 <b>Текущая скидка:</b> {current_discount}%
🎯 <b>Ваша цель:</b> {target_discount}%
💰 <b>Цена:</b> {current_price}₽

🛒 <a href="{store_url}">Купить на Steam</a>

Не упустите выгоду! 🏃‍♂️
        """
        return self.send_message(chat_id, text)

# Глобальный экземпляр бота
notification_bot = NotificationBot()