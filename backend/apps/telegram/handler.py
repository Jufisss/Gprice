from django.contrib.auth.models import User
from apps.users.models import UserProfile
from .bot import telegram_bot

class TelegramHandler:
    def handle_message(self, message_data):
        """Обрабатывает входящие сообщения"""
        try:
            message = message_data.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '').strip()
            username = message.get('from', {}).get('username', '')
            
            if not chat_id or not username:
                return {'success': False}
            
            # Обрабатываем только команду /start
            if text == '/start':
                return self.handle_start(chat_id, username)
            else:
                # На любое другое сообщение отправляем инструкцию
                telegram_bot.send_message(
                    chat_id,
                    "Отправьте /start для получения кода привязки аккаунта."
                )
                return {'success': True}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_start(self, chat_id, username):
        """Обрабатывает команду /start"""
        try:
            # Ищем пользователя
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                telegram_bot.send_message(
                    chat_id,
                    f"❌ Аккаунт с username @{username} не найден.\n\n"
                    f"Убедитесь, что вы зарегистрированы на сайте."
                )
                return {'success': False, 'error': 'User not found'}
            
            profile = user.userprofile
            
            # Если уже привязан
            if profile.telegram_verified:
                telegram_bot.send_message(
                    chat_id,
                    "✅ Ваш аккаунт уже привязан!\n\n"
                    "Вы будете получать уведомления о скидках."
                )
                return {'success': True}
            
            # Генерируем и отправляем код
            code = profile.generate_code()
            success = telegram_bot.send_code(chat_id, code, username)
            
            if success:
                return {'success': True, 'code': code}
            else:
                return {'success': False, 'error': 'Failed to send code'}
                
        except Exception as e:
            telegram_bot.send_message(chat_id, "❌ Ошибка. Попробуйте позже.")
            return {'success': False, 'error': str(e)}

# Глобальный экземпляр
telegram_handler = TelegramHandler()