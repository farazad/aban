from celery import Celery
from celery.schedules import crontab

app = Celery('your_project_name')

app.conf.beat_schedule = {
    'process_pending_transactions': {
        'task': 'your_app.tasks.process_pending_transactions',
        'schedule': crontab(minute='*/5'),  # Runs every 5 minutes
    },
}