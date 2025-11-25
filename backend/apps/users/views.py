from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.http import JsonResponse
from rest_framework.decorators import api_view
from apps.telegram.bot import notification_bot
from .models import UserProfile
from .serializers import (UserSerializer, UserProfileSerializer, 
                         UserRegistrationSerializer, UserLoginSerializer)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        profile = request.user.userprofile
        if request.method == 'PUT':
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_register(request):
    """Регистрация нового пользователя"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Создаем токен для API
        token, created = Token.objects.get_or_create(user=user)
        
        # Логиним пользователя
        login(request, user)
        
        return Response({
            "message": "Пользователь успешно зарегистрирован",
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """Аутентификация пользователя"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "message": "Успешный вход",
                "user": UserSerializer(user).data,
                "token": token.key
            })
        else:
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    return Response({"message": "Успешный выход"})

@api_view(['GET'])
def current_user(request):
    """Получить текущего пользователя"""
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    return Response({"error": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)







telegram_verifications = {}

@api_view(['POST'])
def start_telegram_verification(request):
    """Начинает процесс верификации Telegram - возвращает код"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация'
        }, status=401)
    
    try:
        profile = request.user.userprofile
        
        # Генерируем код
        code = profile.generate_verification_code()
        
        return JsonResponse({
            'success': True,
            'code': code,
            'message': 'Код сгенерирован. Отправьте его боту в Telegram.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка: {str(e)}'
        }, status=500)

@api_view(['POST'])
def verify_telegram(request):
    """Завершает верификацию Telegram"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация'
        }, status=401)
    
    try:
        code = request.data.get('code', '').strip()
        chat_id = request.data.get('chat_id', '').strip()
        
        if not code or len(code) != 6:
            return JsonResponse({
                'success': False,
                'error': 'Введите 6-значный код'
            }, status=400)
        
        if not chat_id:
            return JsonResponse({
                'success': False,
                'error': 'Введите Chat ID'
            }, status=400)
        
        profile = request.user.userprofile
        
        # Проверяем код
        if profile.telegram_verification_code != code:
            return JsonResponse({
                'success': False,
                'error': 'Неверный код'
            }, status=400)
        
        # Верифицируем
        profile.verify_telegram(chat_id, request.user.username)
        
        # Отправляем приветственное сообщение
        telegram_bot.send_message(
            chat_id,
            f"✅ <b>Аккаунт успешно привязан!</b>\n\n"
            f"Привет, {request.user.username}!\n"
            f"Теперь вы будете получать уведомления о скидках на игры из вашего вишлиста."
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Telegram успешно привязан!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка: {str(e)}'
        }, status=500)

@api_view(['POST'])
def disconnect_telegram(request):
    """Отключает Telegram"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация'
        }, status=401)
    
    try:
        profile = request.user.userprofile
        profile.telegram_chat_id = None
        profile.telegram_username = None
        profile.telegram_verified = False
        profile.telegram_verification_code = None
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Telegram отключен'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка: {str(e)}'
        }, status=500)

@api_view(['GET'])
def get_telegram_status(request):
    """Возвращает статус Telegram"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'telegram_connected': False,
            'telegram_username': None
        })
    
    try:
        profile = request.user.userprofile
        return JsonResponse({
            'telegram_connected': profile.telegram_verified,
            'telegram_username': profile.telegram_username
        })
    except:
        return JsonResponse({
            'telegram_connected': False,
            'telegram_username': None
        })