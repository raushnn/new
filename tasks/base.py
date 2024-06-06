from __future__ import annotations

from typing import Any

from billiard.einfo import ExceptionInfo
from celery import Task


class BaseTask(Task):
    ignore_result: bool = True
    retry_backoff: bool = True
    retry_backoff_max: int = 60
    retry_jitter: bool = True
    retry_jitter_max: int = 60
    retry_on_exception: bool = True
    retry_on_request: bool = True
    retry_policy: dict[str, Any] = {  # noqa: RUF012
        "interval_start": 0,
        "interval_step": 2,
        "interval_max": 60,
        "max_retries": 5,
    }

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: ExceptionInfo,
    ) -> None:
        print(f"on_failure {self.request.retries = }")
        print(f"on_failure {self.request.retries = }")
        print(f"on_failure {self.request.retries = }")
        print(f"on_failure {self.request.retries = }")
        print(f"on_failure {self.request.retries = }")
        return super().on_failure(exc, task_id, args, kwargs, einfo)
