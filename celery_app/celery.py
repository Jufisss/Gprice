import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('steam_wishlist')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Расписание периодических задач
app.conf.beat_schedule = {
    'check-game-prices-every-6-hours': {
        'task': 'celery_app.tasks.check_game_prices',
        'schedule': crontab(hour='*/6'),  # Каждые 6 часов
    },
    'update-game-prices-daily': {
        'task': 'celery_app.tasks.update_game_prices',
        'schedule': crontab(hour=3, minute=0),  # Ежедневно в 3:00
    },
}

app.conf.timezone = 'Europe/Moscow'