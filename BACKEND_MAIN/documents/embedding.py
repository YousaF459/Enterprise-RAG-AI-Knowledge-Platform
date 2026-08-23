from sentence_transformers import SentenceTransformer
import logging
from .exceptions import EmbeddingGenerationError


logger=logging.getLogger(__name__)

embedding_model = None


def get_embedding_model():

    global embedding_model

    if embedding_model is None:
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    return embedding_model

def generate_embedding(text):
    try:
        logger.info("Generating text embedding")

        model = get_embedding_model()
        
        return model.encode(text)
    
    except Exception as e:
        logging.exception("Embedding Generation Failed")

        raise EmbeddingGenerationError("Failed to generate embedding") from e