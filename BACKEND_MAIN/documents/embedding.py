from sentence_transformers import SentenceTransformer
import logging
from .exceptions import EmbeddingGenerationError

embedding_model=SentenceTransformer("all-MiniLM-L6-v2")
logger=logging.getLogger(__name__)

def generate_embedding(text):
    try:
        logger.info("Generating text embedding")
        
        return embedding_model.encode(text)
    
    except Exception as e:
        logging.exception("Embedding Generation Failed")

        raise EmbeddingGenerationError("Failed to generate embedding") from e