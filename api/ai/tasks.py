from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any, ClassVar

import requests
from billiard.einfo import ExceptionInfo
from celery import shared_task
from langchain.document_loaders import UnstructuredFileLoader
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

from api.ai import models
from api.config.ai import STORAGE_CONTEXT, VECTOR_STORE
from tasks.base import BaseTask

logger = logging.getLogger(__name__)

class AIDeepTalkFileReader:
    API_URL: ClassVar = "https://core-ai.cdo-global.com/feature-tool/file-to-string"
    SESSION: ClassVar = requests.Session()

    is_remote: bool = True

    def load_data(
        self,
        file: Path,
        metadata: dict[str, Any] | None = None,
    ) -> list[Document]:
        """Parse file."""
        logger.info("Parsing file %r", file)
        response = self.SESSION.post(
            url=self.API_URL,
            files={"file": file.open("rb")},
        )

        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.exception("Failed to parse file %r: %r", file, response.text)
            raise

        text = response.text
        metadata_ = {"file_name": file.name}
        if metadata is not None:
            metadata.update(metadata_)

        logger.info("Successfully parsed file %r", file)
        return [Document(page_content=text, metadata=metadata)]


AI_DEEP_TALK_FILE_READER = AIDeepTalkFileReader()


class AddDocumentEmbeddingTask(BaseTask):
    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: ExceptionInfo,
    ) -> None:
        logger.exception(
            "Failed to add embedding for document %r: %r",
            kwargs["doc_id"],
            exc,
        )
        models.Document.objects.filter(pk=kwargs["doc_id"]).update(
            processing_status=models.Document.ProcessingStatus.ERROR,
        )
        return super().on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(
    base=AddDocumentEmbeddingTask,
    autoretry_for=(Exception,),
)
def add_document_embedding(doc_id: str) -> None:
    document = models.Document.objects.get(pk=doc_id)
    if document.processing_status == models.Document.ProcessingStatus.DONE:
        logger.info("Document %r already has embeddings", document)
        return

    logger.info("Adding embedding for document '%r'", document)
    document.processing_status = models.Document.ProcessingStatus.IN_PROGRESS
    document.save()

    service_context = document.embedding_model.as_service_context()

    with (
        document.file.open("rb") as f,
        tempfile.TemporaryDirectory() as temp_dir,
    ):
        directory = Path(temp_dir)
        filename = document.file.name.split("/")[-1]
        file_path = directory / filename
        file_path.write_bytes(f.read())

        metadata = {
            "doc_id": str(document.pk),
            "file_name": document.file.name,
            "description": document.description,
        }

        documents = AI_DEEP_TALK_FILE_READER.load_data(
            file=file_path,
            metadata=metadata,
        )

        for doc in documents:
            doc.metadata["id"] = str(document.pk)

    embeddings = OpenAIEmbeddings()
    faiss_index = FAISS.from_documents(documents, embeddings)

    # Save the FAISS index and documents in VECTOR_STORE
    VECTOR_STORE.save_index(faiss_index)
    VECTOR_STORE.save_documents(documents)

    # check if files were uploaded
    data = VECTOR_STORE.get_by_id(doc_id=str(document.pk))
    if not data:
        logger.error("Failed to add embedding for document %r", document)
    else:
        logger.info("Successfully added embedding for document %r", document)
        document.processing_status = models.Document.ProcessingStatus.DONE
        document.save()
