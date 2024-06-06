from __future__ import annotations

from typing import Any, cast, get_type_hints

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer


def as_serializer[
    DataClass: Any
](dataclass_type: DataClass, **kwargs: Any) -> type[DataclassSerializer[DataClass]]:
    """Create a serializer from a dataclass.

    This is a helper function to make it easier to create serializers from dataclasses.
    It is equivalent to:
    ```
    class MySerializer(DataclassSerializer):
        class Meta:
            dataclass = MyDataclass
    ```
    """
    field_overrides: dict[str, serializers.Field] = {}

    type_hints = get_type_hints(dataclass_type, include_extras=True)
    for field_name, field_type in type_hints.items():
        metadata = getattr(field_type, "__metadata__", None)
        if not metadata:
            continue

        for value in metadata:
            if not isinstance(value, serializers.Field):
                continue

            field_overrides[field_name] = value
            break

    return cast(
        type[DataclassSerializer[DataClass]],
        type(
            f"{dataclass_type.__name__}Serializer",
            (DataclassSerializer,),
            {
                "Meta": type("Meta", (), {"dataclass": dataclass_type}),
                **field_overrides,
                **kwargs,
            },
        ),
    )


class UserRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> Any:
        request = self.context["request"]
        return super().get_queryset().filter(user=request.user)
