from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from django.db import models
from langchain import Embedding, LLM, ServiceContext
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbedding


from api.config.ai import DEFAULT_LLM, LLM_HTTPX_CLIENT

if TYPE_CHECKING:
    from api.user.models import User


class Language(models.TextChoices):
    RU = "ru", "Русский"
    EN = "en", "Английский"


def _upload_document_path(instance: Document, filename: str) -> str:
    return f"documents/user/{instance.user.pk}/{filename}"


class Document(models.Model):
    class ProcessingStatus(models.TextChoices):
        ERROR = "error", "❌ Ошибка векторизации"
        NOT_STARTED = "not_started", "❕ Не векторизован"
        IN_PROGRESS = "in_progress", "🔎 Векторизуется"
        DONE = "done", "✅ Векторизован"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    file = models.FileField(upload_to=_upload_document_path)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    embedding_model: models.ForeignKey[EmbeddingModel] = models.ForeignKey(
        "EmbeddingModel",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    available_for: models.QuerySet[User]

    processing_status = models.CharField(
        max_length=32,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.NOT_STARTED,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.name or str(self.file.name) or str(self.id)


class BaseAIModel(models.Model):
    class Provider(models.TextChoices):
        OPENAI = "openai", "OpenAI"
        GIGA_CHAT = "giga_chat", "Giga Chat"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    is_active = models.BooleanField(default=True)

    api_key = models.CharField(max_length=2048, verbose_name="API ключ")
    provider = models.CharField(
        max_length=32,
        choices=Provider.choices,
        default=Provider.OPENAI,
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Название модели у провайдера",
        default="",
    )

    display_name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="Отображаемое имя",
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание",
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.display_name or str(self.id)


class EmbeddingModel(BaseAIModel):
    chunk_size = models.PositiveIntegerField(
        default=100,
        verbose_name="Размер чанка",
    )
    chunk_overlap = models.PositiveIntegerField(
        default=10,
        verbose_name="Перекрытие чанков",
    )

    def as_embed_model(self) -> Embedding:
        if self.provider == self.Provider.OPENAI:
            

            return OpenAIEmbedding(
                api_key=self.api_key,
                model=self.name,
                http_client=LLM_HTTPX_CLIENT,
            )

        msg = "Unknown provider"
        raise NotImplementedError(msg)

    def as_service_context(self, **kwargs: Any) -> ServiceContext:
        if "llm" not in kwargs:
            kwargs["llm"] = DEFAULT_LLM

        return ServiceContext(
            embed_model=self.as_embed_model(),
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            **kwargs,
        )


class SearchModel(BaseAIModel):
    price_per_1k_input_tokens = models.DecimalField(
        default=Decimal("0.0015"),
        decimal_places=8,
        max_digits=16,
        verbose_name="Цена за 1000 input токенов",
    )

    price_per_1k_output_tokens = models.DecimalField(
        default=Decimal("0.002"),
        decimal_places=8,
        max_digits=16,
        verbose_name="Цена за 1000 output токенов",
    )

    def as_llm(self) -> LLM:
        if self.provider == self.Provider.OPENAI:

            return OpenAI(
                api_key=self.api_key,
                model=self.name,
                http_client=LLM_HTTPX_CLIENT,
            )

        msg = "Unknown provider"
        raise NotImplementedError(msg)


class Usage(models.Model):
    class Type(models.TextChoices):
        QUICK_SEARCH = "quick_search", "Быстрый поиск"
        NODES_SEARCH = "nodes_search", "Поиск по узлам"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    type = models.CharField(
        max_length=32,
        choices=Type.choices,
        default=Type.QUICK_SEARCH,
    )

    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="usages",
    )

    completion_llm_token_count = models.PositiveIntegerField(default=0)
    prompt_llm_token_count = models.PositiveIntegerField(default=0)
    total_llm_token_count = models.PositiveIntegerField(default=0)

    total_embedding_token_count = models.PositiveIntegerField(default=0)

    prompt = models.TextField(blank=True, default="")
    query = models.TextField(blank=True, default="")
    response = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)


class Prompt(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    is_active = models.BooleanField(default=True)

    language = models.CharField(
        max_length=32,
        choices=Language.choices,
        default=Language.RU,
    )

    system_prompt = models.TextField(blank=True, default="")
    user_prompt = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.id)
