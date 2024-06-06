from __future__ import annotations

from typing import Any, ClassVar

from cachetools import TTLCache
from django.contrib.auth.models import AbstractUser
from django.db import models
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.schema import Document as LangChainDocument
from api.config.ai import VECTOR_STORE

class User(AbstractUser):
    _vector_store_cache: ClassVar = TTLCache[Any, Qdrant](
        maxsize=100,
        ttl=60 * 10,
    )
    """Cache for vector stores. Key is user id."""

    raw_password = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Пароль (не хешированный)",
    )

    has_full_access = models.BooleanField(
        default=False,
        verbose_name="Полный доступ ?",
    )

    available_documents = models.ManyToManyField(
        "ai.Document",
        related_name="available_for",
        blank=True,
        verbose_name="Доступные документы",
    )

    def _get_vector_store(self) -> Qdrant:
        return VECTOR_STORE

    def _get_service_context(self) -> dict:
        return {
            "embed_model": OpenAIEmbeddings(),
        }

    def get_vector_store_index(self) -> Qdrant:
        vector_store = self._get_vector_store()
        service_context = self._get_service_context()
        return vector_store

    def add_documents_to_vector_store(self, documents: list[LangChainDocument]) -> None:
        vector_store = self.get_vector_store_index()
        vector_store.add_texts(
            texts=[doc.page_content for doc in documents],
            metadatas=[doc.metadata for doc in documents],
        )
