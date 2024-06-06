from __future__ import annotations

from typing import Any, ClassVar, cast

import langchain
import tiktoken
from django.db.models import Q
from django.utils import timezone
from langchain.prompts import ChatMessage, ChatPromptTemplate, MessageRole
from langchain.schema import BasePromptTemplate
from langchain.vectorstores import FAISS
from langchain.callbacks import CallbackManager, TokenCountingHandler
from langchain.docstore.document import Document
from rest_framework import mixins, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.routers import SimpleRouter
from rest_framework.viewsets import GenericViewSet

from api.ai import models
from api.ai import serializers as dto
from api.ai.models import Document, EmbeddingModel, SearchModel, Usage
from api.common.routers import APIViewRouter
from api.common.serializers import as_serializer
from api.common.views import BaseAPIView
from api.config.ai import DEFAULT_LLM, VECTOR_STORE
from api.user.models import User

router = APIViewRouter(drf_router=SimpleRouter(trailing_slash=True))


# region Models


@router.register(r"knowledge-models", basename="ai")
class KnowledgeModelsView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = EmbeddingModel.objects.filter(is_active=True)
    serializer_class = dto.EmbeddingModelSerializer


@router.register(r"search-models", basename="ai")
class SearchModelsView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = SearchModel.objects.filter(is_active=True)
    serializer_class = dto.SearchModelSerializer


# endregion Models


# region Documents


@router.register(r"documents", basename="ai")
class DocumentsView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    queryset = Document.objects.filter(deleted_at__isnull=True)
    serializer_class = dto.DocumentSerializer

    def get_queryset(self) -> Any:
        user = cast(User, self.request.user)
        if user.has_full_access:
            return super().get_queryset().filter()

        return (
            super()
            .get_queryset()
            .filter(
                Q(user=user)
                # Add docs from user.available_documents
                | Q(pk__in=user.available_documents.all()),
            )
        )

    def perform_create(self, serializer: dto.DocumentSerializer) -> None:
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance: Document) -> None:
        instance.deleted_at = timezone.now()
        instance.save()


# endregion Documents


# region Search


class BaseSearchViewMixin:
    request: Request
    data: dto.QuickSearchRequest | dto.NodesSearchRequest
    token_counter: TokenCountingHandler

    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def _get_vector_index(self) -> FAISS:
        callback_manager = CallbackManager([self.token_counter])

        if isinstance(self.data, dto.QuickSearchRequest):
            llm = self.data.search_model.as_llm()
        else:
            llm = DEFAULT_LLM

        service_context = self.data.knowledge_model.as_service_context(
            llm=llm,
            callback_manager=callback_manager,
        )

        return FAISS.from_existing_index(
            vector_store=VECTOR_STORE,
            service_context=service_context,
        )

    def _get_query_engine(self) -> BaseQueryEngine:
        index = self._get_vector_index()
        filters = self._get_metadata_filters()
        chat_template = self._get_prompt_template()

        return index.as_query_engine(
            filters=filters,
            text_qa_template=chat_template,
        )

    def _get_metadata_filters(self) -> MetadataFilters:
        return MetadataFilters(
            filters=[
                MetadataFilter(key="doc_id", value=str(doc.pk))
                for doc in self.data.documents
            ],
            condition=FilterCondition.OR,  # Change AND to OR
        )

    def _get_prompt_template(self) -> BasePromptTemplate | None:
        if isinstance(self.data, dto.QuickSearchRequest):
            language = self.data.language
        else:
            language = models.Language.RU

        prompt = models.Prompt.objects.filter(
            language=language,
            is_active=True,
        ).first()

        if prompt is None:
            return None

        return ChatPromptTemplate(
            message_templates=[
                ChatMessage(
                    content=prompt.system_prompt,
                    role=MessageRole.SYSTEM,
                ),
                ChatMessage(
                    content=prompt.user_prompt,
                    role=MessageRole.USER,
                ),
            ],
        )

    def _get_usage(self, result: langchain.Response) -> tuple[dto.Usage, Usage]:
        usage = dto.Usage.from_token_counter(self.token_counter)

        prompt = " ".join(event.prompt for event in self.token_counter.llm_token_counts)

        type_ = (
            models.Usage.Type.QUICK_SEARCH
            if isinstance(
                self.data,
                dto.QuickSearchRequest,
            )
            else models.Usage.Type.NODES_SEARCH
        )

        usage_obj = Usage.objects.create(
            user=self.request.user,
            type=type_,
            query=self.data.query,
            prompt=prompt,
            response=result.response,
            **usage.as_dict(),
        )

        return usage, usage_obj


@router.register(r"search/quick/", name="search")
class QuickSearchView(BaseSearchViewMixin, BaseAPIView):
    """Quick search by query."""

    serializer_class = as_serializer(dto.QuickSearchRequest)
    response_serializer_class = as_serializer(dto.QuickSearchResponse)

    data: dto.QuickSearchRequest
    token_counter: TokenCountingHandler

    def post(self, request: Request) -> Response:  # noqa: ARG002
        self.data = cast(dto.QuickSearchRequest, self.get_validated_data())
        self.token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(self.data.search_model.name).encode,
        )

        engine = self._get_query_engine()
        result = cast(langchain.Response, engine.query(self.data.query))
        usage, _ = self._get_usage(result)

        self.token_counter.reset_counts()

        response = dto.QuickSearchResponse(
            answer=str(result),
            usage=usage,
            nodes=[dto.Node.from_langchain_node(node) for node in result.source_nodes],
            metadata=result.metadata,
        )

        return Response(self.response_serializer_class(response).data)


@router.register(r"search/nodes/", name="search")
class NodesSearchView(BaseSearchViewMixin, BaseAPIView):
    """Search nodes by query."""

    serializer_class = as_serializer(dto.NodesSearchRequest)
    response_serializer_class = as_serializer(dto.NodesSearchResponse)

    def post(self, request: Request) -> Response:  # noqa: ARG002
        self.data = cast(dto.NodesSearchRequest, self.get_validated_data())

        self.token_counter = TokenCountingHandler(
            tokenizer=tiktoken.encoding_for_model(DEFAULT_LLM.model).encode,
        )

        index = self._get_vector_index()
        retriever = index.as_retriever(
            similarity_top_k=self.data.similarity_top_k,
            filters=self._get_metadata_filters(),
        )

        nodes_with_score = retriever.retrieve(self.data.query)
        nodes_with_score = SimilarityPostprocessor(
            similarity_cutoff=self.data.similarity_cutoff,
        ).postprocess_nodes(nodes_with_score)

        nodes = [
            dto.Node.from_langchain_node(node_with_score)
            for node_with_score in nodes_with_score
        ]

        usage, _ = self._get_usage(langchain.Response(response=""))

        self.token_counter.reset_counts()

        response = dto.NodesSearchResponse(
            nodes=nodes,
            usage=usage,
        )

        return Response(self.response_serializer_class(response).data)


# endregion Search
