from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Celery app
app = Celery('workflow')

# Config
app.conf.update(
    broker_url='memory://',
    result_backend='cache+memory://',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Jakarta',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=20 * 60,
)

# Import tasks
from app.tasks import tasks

if __name__ == '__main__':
    app.start()
