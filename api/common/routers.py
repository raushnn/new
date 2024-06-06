from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, cast

from django.urls import URLResolver, path
from rest_framework.routers import SimpleRouter
from rest_framework.viewsets import GenericViewSet, ViewSet


@dataclass
class APIViewRouter:
    drf_router: SimpleRouter = field(default_factory=SimpleRouter)

    _paths: list[URLResolver] = field(default_factory=list)

    def register[T: Any](self, route: str, **kwargs: Any) -> Callable[[T], T]:
        def decorator(view: T) -> T:
            if issubclass(view, (ViewSet, GenericViewSet)):
                self.drf_router.register(route, view, **kwargs)
            else:
                self._paths.append(
                    path(route, view.as_view(), **kwargs),
                )

            return cast(T, view)

        return decorator

    @property
    def urls(self) -> list[Any]:
        return self._paths + self.drf_router.urls
