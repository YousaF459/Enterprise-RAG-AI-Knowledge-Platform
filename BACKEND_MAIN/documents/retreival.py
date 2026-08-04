from pgvector.django import CosineDistance
from documents.models import DocumentChunk
from .exceptions import RetrievalError
import logging


logger=logging.getLogger(__name__)

def retrieve_chunks(question_embedding,organization,top_k=5):

    try:

        logger.info("Chunks Retreival Started")

        return (
        DocumentChunk.objects.filter(document__organization=organization).annotate(distance=CosineDistance('embedding',question_embedding)).order_by('distance')[:top_k]
        )
    except Exception as e:

        logger.exception("Chunks Retreival Failed")

        raise RetrievalError("Failed to retrieve relevant document chunks.") from e