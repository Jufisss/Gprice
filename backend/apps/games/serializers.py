from rest_framework import serializers
from .models import Game, Wishlist

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'steam_app_id', 'name', 'current_price', 'original_price', 
                 'discount_percent', 'image_url', 'store_url', 'last_updated']

class WishlistSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    game_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'game', 'game_id', 'target_price', 'target_discount', 'created_at']
        read_only_fields = ['id', 'created_at']