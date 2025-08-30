import os
from celery import Celery

broker  = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
celery_app = Celery("vakta-worker", broker=broker, backend=backend)
celery_app.autodiscover_tasks(["tasks"])
