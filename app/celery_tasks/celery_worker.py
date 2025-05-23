from celery import Celery

from app.core.config import load_config

config = load_config()

celery_app = Celery(
    "app",
    broker=config.celery.broker_url,
    backend=config.celery.result_backend,
)

celery_app.autodiscover_tasks(["app.celery_tasks"])
