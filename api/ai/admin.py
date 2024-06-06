from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource

from api.api.ai import models


class EmbeddingModelResource(ModelResource):
    class Meta:
        model = models.EmbeddingModel


class SearchModelResource(ModelResource):
    class Meta:
        model = models.SearchModel


@admin.register(models.Document)
class DocumentAdmin(ModelAdmin):
    readonly_fields = ("content",)
    list_display = (
        "id",
        "name",
        "embedding_model",
        "processing_status",
        "user",
        "available_for_str",
        "created_at",
    )

    list_filter = (
        "embedding_model",
        "processing_status",
        "user",
        "available_for",
    )

    def available_for_str(self, obj: models.Document) -> str:
        return ", ".join([str(user) for user in obj.available_for.all()])

    def content(self, obj: models.Document) -> str:
        return obj.file.read().decode()


@admin.register(models.EmbeddingModel)
class EmbeddingModelAdmin(ImportExportMixin, ModelAdmin):
    resource_class = EmbeddingModelResource
    list_display = (
        "id",
        "display_name",
        "provider",
        "name",
        "is_active",
        "chunk_size",
        "chunk_overlap",
    )

    list_editable = (
        "is_active",
        "chunk_size",
        "chunk_overlap",
    )


@admin.register(models.SearchModel)
class SearchModelAdmin(ImportExportMixin, ModelAdmin):
    resource_class = SearchModelResource
    list_display = (
        "id",
        "display_name",
        "provider",
        "name",
        "is_active",
        "price_per_1k_input_tokens",
        "price_per_1k_output_tokens",
    )

    list_editable = (
        "is_active",
        "price_per_1k_input_tokens",
        "price_per_1k_output_tokens",
    )


@admin.register(models.Usage)
class UsageAdmin(ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )


@admin.register(models.Prompt)
class PromptAdmin(ModelAdmin):
    list_display = (
        "id",
        "language",
        "is_active",
        "created_at",
    )

    list_editable = ("is_active",)
