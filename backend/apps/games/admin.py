from django.contrib import admin
from .models import Game, Wishlist

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'steam_app_id', 'current_price', 'discount_percent', 'last_updated']
    search_fields = ['name']
    list_filter = ['discount_percent']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'target_price', 'target_discount', 'created_at']
    list_filter = ['user', 'created_at']