from __future__ import annotations

from typing import Any, cast

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import GenericAPIView

from api.user.models import User


class BaseAPIView(GenericAPIView):
    """Base class for API views.

    This class adds the following features:
    - adds response serializer to OpenAPI schema;
    - adds query parameters to OpenAPI schema;
    - adds `get_validated_data` method.
    """

    serializer_class: type[serializers.Serializer] = serializers.Serializer
    response_serializer_class: type[serializers.Serializer] = serializers.Serializer

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        cls._add_response_to_openapi()
        cls._add_query_params_to_openapi()

    @classmethod
    def _add_response_to_openapi(cls) -> None:
        for method_name in (
            "get",
            "post",
            "put",
            "patch",
            "delete",
        ):
            method = getattr(cls, method_name, None)
            if method:
                setattr(
                    cls,
                    method_name,
                    extend_schema(
                        responses=cls.response_serializer_class,
                    )(method),
                )

    @classmethod
    def _add_query_params_to_openapi(cls) -> None:
        if not hasattr(cls, "get"):
            return

        serializer = cast(serializers.Serializer, cls.serializer_class())
        fields = serializer.get_fields()

        parameters = [
            OpenApiParameter(
                name=field_name,
                required=field.required,
                description=field.help_text,
            )
            for field_name, field in fields.items()
        ]

        cls.get = extend_schema(
            parameters=parameters,
        )(cls.get)

    def get_validated_data(self) -> Any:
        raw_data = self.request.data or self.request.query_params
        serializer = self.get_serializer(data=raw_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_user(self) -> User:
        if not isinstance(self.request.user, User):
            raise NotAuthenticated

        return self.request.user
