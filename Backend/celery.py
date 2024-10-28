import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

app = Celery('Backend')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process_pending_transactions': {
        'task': 'accounting.tasks.process_pending_transactions',
        'schedule': crontab(minute='*/5'),  # Runs every 5 minutes
    },
}