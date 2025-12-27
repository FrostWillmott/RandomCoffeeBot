"""Celery application configuration."""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "randomcoffee",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    beat_schedule={
        # Example: weekly matching task
        # "weekly-matching": {
        #     "task": "app.workers.tasks.run_weekly_matching",
        #     "schedule": 604800.0,  # Weekly (7 days in seconds)
        # },
    },
)
