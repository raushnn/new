from __future__ import annotations

from typing import Any

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

from api.user.models import User


class UserResource(resources.ModelResource):
    class Meta:
        model = User

        # update on conflict
        import_id_fields = ("username",)

    # Run set password after import
    def after_import_instance(
        self,
        instance: User,
        new: bool,
        row_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        if instance.username != "admin":
            instance.save()
            instance.set_password(instance.raw_password)
            instance.save()

        super().after_import_instance(instance, new)


@admin.register(User)
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = UserResource
    filter_horizontal = ("groups", "user_permissions", "available_documents")

    list_display = (
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "raw_password",
                    "password",
                    # "email",
                    # "first_name",
                    # "last_name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "has_full_access",
                    "available_documents",
                ),
            },
        ),
    )

    def save_model(
        self,
        request: Any,
        obj: User,
        form: None,
        change: bool,
    ) -> None:
        has_raw_password = obj.password.startswith("pbkdf2_sha256")
        if not has_raw_password:
            obj.set_password(obj.password)

        super().save_model(request, obj, form, change)
