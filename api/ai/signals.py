from __future__ import annotations

import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from api.ai import models, tasks

logger = logging.getLogger(__name__)


@receiver(post_save, sender=models.Document)
def add_embedding(
    sender: type[models.Document],  # noqa: ARG001
    instance: models.Document,
    created: bool,  # noqa: FBT001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    if not created:
        return

    logger.info("Add embedding for document %r", instance)

    tasks.add_document_embedding.delay(doc_id=str(instance.pk))
