from pgvector.django import CosineDistance
from documents.models import DocumentChunk


def retrieve_chunks(question_embedding,organization,top_k=5):

    return (
        DocumentChunk.objects.filter(document__organization=organization).annotate(distance=CosineDistance('embedding',question_embedding)).order_by('distance')[:top_k]
    )