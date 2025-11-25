from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'games', views.GameViewSet)
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
    path('add-game/', views.add_game_from_steam, name='add_game'),
    path('add-wishlist-direct/', views.add_to_wishlist_direct, name='add_wishlist_direct'),
    path('my-wishlist/', views.my_wishlist, name='my_wishlist'),
]