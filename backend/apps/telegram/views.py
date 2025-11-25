from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .oauth import telegram_oauth
from .bot import notification_bot

@csrf_exempt
@login_required
def connect_telegram(request):
    """Обрабатывает OAuth данные от Telegram Web App"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Проверяем подпись
            is_valid, message = telegram_oauth.verify_auth_data(data)
            
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'error': message
                })
            
            # Привязываем аккаунт
            success, message = telegram_oauth.connect_telegram_account(request.user, data)
            
            if success:
                # Отправляем приветственное сообщение в Telegram
                telegram_id = data.get('id')
                username = data.get('username', request.user.username)
                notification_bot.send_connection_success(telegram_id, username)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Telegram аккаунт успешно привязан!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': message
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })

@login_required
def get_telegram_status(request):
    """Возвращает статус привязки Telegram"""
    try:
        profile = request.user.userprofile
        return JsonResponse({
            'connected': profile.telegram_connected,
            'telegram_username': profile.telegram_username,
            'telegram_first_name': profile.telegram_first_name
        })
    except Exception as e:
        return JsonResponse({
            'connected': False,
            'error': str(e)
        })

@login_required
def disconnect_telegram(request):
    """Отвязывает Telegram аккаунт"""
    try:
        profile = request.user.userprofile
        profile.telegram_id = None
        profile.telegram_username = None
        profile.telegram_first_name = None
        profile.telegram_last_name = None
        profile.telegram_connected = False
        profile.telegram_auth_date = None
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Telegram аккаунт отвязан'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })