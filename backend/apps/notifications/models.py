from django.db import models
from django.contrib.auth.models import User
from apps.games.models import Game

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    message = models.TextField()
    sent_via_email = models.BooleanField(default=False)
    sent_via_telegram = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Уведомление для {self.user.username} - {self.game.name}"
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'