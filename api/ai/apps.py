from __future__ import annotations

from django.apps import AppConfig


class AIConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api.ai"

    def ready(self) -> None:
        from api.ai import signals  # noqa: F401

        return super().ready()
