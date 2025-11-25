from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views import View

from rest_framework import routers
from apps.games.views import (GameViewSet, WishlistViewSet, SearchView, 
                             add_game_from_steam, test_api, add_to_wishlist_direct, my_wishlist)
from apps.users.views import UserViewSet, user_register, user_login, user_logout, current_user
from apps.games.views import WishlistPageView

router = routers.DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'users', UserViewSet, basename='users')

class HealthCheck(View):
    def get(self, request):
        return JsonResponse({"status": "ok", "service": "django"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/add-game/', add_game_from_steam, name='add_game'),
    path('api/add-wishlist-direct/', add_to_wishlist_direct, name='add_wishlist_direct'),
    path('api/my-wishlist/', my_wishlist, name='my_wishlist'),
    path('api/test/', test_api, name='test_api'),
    path('api/auth/register/', user_register, name='register'),
    path('api/auth/login/', user_login, name='login'),
    path('api/auth/logout/', user_logout, name='logout'),
    path('api/auth/current-user/', current_user, name='current_user'),
    path('api-auth/', include('rest_framework.urls')),
    path('health/', HealthCheck.as_view(), name='health'),
    path('', SearchView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),
    path('wishlist/', WishlistPageView.as_view(), name='wishlist_page'),
    path('api/telegram/', include('apps.telegram.urls')),
]