import hashlib
import hmac
import time
from django.conf import settings
from django.utils import timezone
from apps.users.models import UserProfile

class TelegramOAuth:
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    
    def verify_auth_data(self, auth_data):
        """
        Проверяет подпись Telegram Web App
        https://core.telegram.org/widgets/login
        """
        try:
            # Извлекаем параметры
            hash_str = auth_data.pop('hash', '')
            auth_date = auth_data.get('auth_date', '')
            
            # Проверяем срок действия (не старше 1 дня)
            if time.time() - int(auth_date) > 86400:
                return False, "Auth data expired"
            
            # Сортируем параметры по алфавиту
            data_check_string = '\n'.join(
                f"{key}={auth_data[key]}" 
                for key in sorted(auth_data.keys())
            )
            
            # Вычисляем секретный ключ
            secret_key = hashlib.sha256(self.bot_token.encode()).digest()
            
            # Вычисляем хеш
            computed_hash = hmac.new(
                secret_key, 
                data_check_string.encode(), 
                hashlib.sha256
            ).hexdigest()
            
            # Сравниваем хеши
            if computed_hash == hash_str:
                return True, "Verification successful"
            else:
                return False, "Invalid hash"
                
        except Exception as e:
            return False, f"Verification error: {str(e)}"
    
    def connect_telegram_account(self, user, auth_data):
        """Привязывает Telegram аккаунт к пользователю"""
        try:
            profile = user.userprofile
            
            # Сохраняем данные Telegram
            profile.telegram_id = int(auth_data.get('id'))
            profile.telegram_username = auth_data.get('username', '')
            profile.telegram_first_name = auth_data.get('first_name', '')
            profile.telegram_last_name = auth_data.get('last_name', '')
            profile.telegram_connected = True
            profile.telegram_auth_date = timezone.now()
            profile.save()
            
            return True, "Telegram account connected successfully"
            
        except Exception as e:
            return False, f"Connection error: {str(e)}"

# Глобальный экземпляр
telegram_oauth = TelegramOAuth()