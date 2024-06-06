from __future__ import annotations

import logging
import threading
from typing import Any, Callable, ParamSpec, cast

P = ParamSpec("P")

logger = logging.getLogger(__name__)


def run_in_background(f: Callable[P, Any]) -> Callable[P, threading.Thread]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info("Run '%r' in background", f)
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)

        thread.start()

        return thread

    return cast(Callable[P, threading.Thread], wrapper)
