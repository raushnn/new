from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Annotated, Any, TypeAlias, List

from django.db.models import Q
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from api.ai import models
from langchain.embeddings import Embedding
from langchain.schema import NodeWithScore
from langchain.llms import LLM


class DocumentsField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> Any:
        qs = super().get_queryset()
        if qs is None:
            return qs

        return qs.filter(
            Q(deleted_at=None),
            Q(
                Q(user=self.context["request"].user)
                | Q(available_for=self.context["request"].user),
            ),
        )


_embedding_model_field = SlugRelatedField(
    queryset=models.EmbeddingModel.objects.filter(is_active=True),
    slug_field="display_name",
    source="embedding_model",
)
EmbeddingModelType: TypeAlias = Annotated[models.EmbeddingModel, _embedding_model_field]

SearchModelType: TypeAlias = Annotated[
    models.SearchModel,
    SlugRelatedField(
        queryset=models.SearchModel.objects.filter(is_active=True),
        slug_field="display_name",
    ),
]

DocumentsType: TypeAlias = Annotated[
    List[models.Document],
    DocumentsField(
        queryset=models.Document.objects.filter(deleted_at=None),
        many=True,
    ),
]

LanguageType: TypeAlias = Annotated[
    models.Language,
    serializers.ChoiceField(
        choices=models.Language.choices,
        help_text="Язык документов",
    ),
]


class BaseAIModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "display_name",
        )
        extra_kwargs = {  # noqa: RUF012
            "id": {"read_only": True},
        }


class EmbeddingModelSerializer(BaseAIModelSerializer):
    class Meta(BaseAIModelSerializer.Meta):
        model = models.EmbeddingModel


class SearchModelSerializer(BaseAIModelSerializer):
    class Meta(BaseAIModelSerializer.Meta):
        model = models.SearchModel


class DocumentSerializer(serializers.ModelSerializer):
    knowledge_model = _embedding_model_field

    def get_name(self, obj: models.Document) -> str:
        return obj.name or obj.file.name

    def create(self, validated_data: dict[str, Any]) -> models.Document:
        if "name" not in validated_data:
            validated_data["name"] = validated_data["file"].name

        return super().create(validated_data)

    class Meta:
        model = models.Document
        fields = (
            "id",
            "file",
            "name",
            "description",
            "knowledge_model",
            "processing_status",
        )
        extra_kwargs = {  # noqa: RUF012
            "id": {"read_only": True},
            "name": {"required": False},
            "file": {"write_only": True},
            "processing_status": {"read_only": True},
        }


@dataclass
class Node:
    id: str
    score: float | None
    content: str
    metadata: dict[str, Any]

    @classmethod
    def from_langchain_node(cls, node: NodeWithScore) -> Self:
        return cls(
            id=node.id,
            score=node.score,
            content=node.content,
            metadata=node.metadata,
        )


@dataclass
class Usage:
    completion_llm_token_count: int
    prompt_llm_token_count: int
    total_llm_token_count: int
    total_embedding_token_count: int

    @classmethod
    def from_token_counter(cls, token_counter: Any) -> Self:
        return cls(
            completion_llm_token_count=token_counter.completion_llm_token_count,
            prompt_llm_token_count=token_counter.prompt_llm_token_count,
            total_llm_token_count=token_counter.total_llm_token_count,
            total_embedding_token_count=token_counter.total_embedding_token_count,
        )

    def as_dict(self) -> dict[str, int]:
        return dataclasses.asdict(self)


@dataclass
class BaseSearchRequest:
    query: str
    documents: DocumentsType
    knowledge_model: EmbeddingModelType


@dataclass
class BaseSearchResponse:
    nodes: list[Node]
    usage: Usage
    metadata: dict[str, Any] | None = None


@dataclass
class QuickSearchRequest(BaseSearchRequest):
    search_model: SearchModelType
    language: LanguageType


@dataclass(kw_only=True)
class QuickSearchResponse(BaseSearchResponse):
    answer: str


@dataclass
class NodesSearchRequest(BaseSearchRequest):
    query: str
    similarity_top_k: int = 100
    similarity_cutoff: Annotated[
        float,
        serializers.FloatField(min_value=0, max_value=1, default=0.5),
    ] = field(default=0.5)


@dataclass
class NodesSearchResponse(BaseSearchResponse):
    pass
