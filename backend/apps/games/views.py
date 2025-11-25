from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views import View
from django.shortcuts import render
from django.db import IntegrityError
from .models import Game, Wishlist
from .serializers import GameSerializer, WishlistSerializer

class SearchView(View):
    def get(self, request):
        return render(request, 'search.html')
    
class WishlistPageView(View):
    def get(self, request):
        return render(request, 'wishlist.html')

class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск игр в локальной базе данных"""
        query = request.GET.get('q', '')
        if len(query) < 2:
            return Response([])
        
        games = Game.objects.filter(name__icontains=query)[:10]
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('game')
    
    def perform_create(self, serializer):
        game_id = serializer.validated_data['game_id']
        game = get_object_or_404(Game, id=game_id)
        
        # Проверяем нет ли уже игры в вишлисте
        if Wishlist.objects.filter(user=self.request.user, game=game).exists():
            from rest_framework import serializers
            raise serializers.ValidationError("Игра уже в списке желаний")
        
        serializer.save(user=self.request.user, game=game)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_game_from_steam(request):
    """Добавить игру из Steam в базу данных"""
    try:
        steam_data = request.data
        steam_app_id = steam_data.get('steam_app_id')
        
        if not steam_app_id:
            return Response(
                {"error": "steam_app_id обязателен"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем корректность данных
        if not isinstance(steam_app_id, int):
            try:
                steam_app_id = int(steam_app_id)
            except (ValueError, TypeError):
                return Response(
                    {"error": "steam_app_id должен быть числом"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Подготавливаем данные для создания игры
        game_data = {
            'steam_app_id': steam_app_id,
            'name': steam_data.get('name', 'Unknown Game'),
            'current_price': steam_data.get('current_price', 0) or 0,
            'original_price': steam_data.get('original_price', 0) or 0,
            'discount_percent': steam_data.get('discount_percent', 0) or 0,
            'image_url': steam_data.get('image_url', ''),
            'store_url': steam_data.get('store_url', ''),
        }
        
        # Проверяем есть ли игра уже в базе
        try:
            game = Game.objects.get(steam_app_id=steam_app_id)
            created = False
            
            # Обновляем данные если игра уже есть
            game.name = game_data['name']
            game.current_price = game_data['current_price']
            game.original_price = game_data['original_price']
            game.discount_percent = game_data['discount_percent']
            game.image_url = game_data['image_url']
            game.store_url = game_data['store_url']
            game.save()
            
        except Game.DoesNotExist:
            # Создаем новую игру
            game = Game.objects.create(**game_data)
            created = True
        
        return Response({
            "id": game.id,
            "created": created,
            "game": GameSerializer(game).data,
            "message": "Игра успешно добавлена в базу"
        }, status=status.HTTP_201_CREATED)
        
    except IntegrityError as e:
        return Response(
            {"error": f"Ошибка целостности данных: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Неожиданная ошибка: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_api(request):
    """Тестовый эндпоинт для проверки API"""
    return Response({
        "message": "API работает",
        "user": request.user.username if request.user.is_authenticated else "Не авторизован",
        "method": request.method,
        "authenticated": request.user.is_authenticated
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_wishlist_direct(request):
    """Прямое добавление игры в вишлист (альтернативный метод)"""
    try:
        data = request.data
        steam_app_id = data.get('steam_app_id')
        
        if not steam_app_id:
            return Response(
                {"error": "steam_app_id обязателен"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем или создаем игру
        game, created = Game.objects.get_or_create(
            steam_app_id=steam_app_id,
            defaults={
                'name': data.get('name', 'Unknown Game'),
                'current_price': data.get('current_price', 0) or 0,
                'original_price': data.get('original_price', 0) or 0,
                'discount_percent': data.get('discount_percent', 0) or 0,
                'image_url': data.get('image_url', ''),
                'store_url': data.get('store_url', ''),
            }
        )
        
        # Проверяем нет ли уже в вишлисте
        if Wishlist.objects.filter(user=request.user, game=game).exists():
            return Response(
                {"error": "Игра уже в списке желаний"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем запись в вишлисте
        wishlist_item = Wishlist.objects.create(
            user=request.user,
            game=game,
            target_price=data.get('target_price'),
            target_discount=data.get('target_discount')
        )
        
        return Response({
            "success": True,
            "message": "Игра добавлена в список желаний",
            "wishlist_item": WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": f"Ошибка: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_wishlist(request):
    """Получить список желаний текущего пользователя"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('game')
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response({
        "count": wishlist_items.count(),
        "results": serializer.data
    })