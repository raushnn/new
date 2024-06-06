from __future__ import annotations

from os import environ

broker_url = environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Europe/Moscow"
enable_utc = True
