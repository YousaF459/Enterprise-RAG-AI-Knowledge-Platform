
class LLMServiceUnavailable(Exception):
    """Raised when the LLM service cannot generate an answer."""

    pass


class EmbeddingGenerationError(Exception):
    """Raised when Embedding Model cannot generate an embedding for text"""
    pass


class RetrievalError(Exception):
    """Raised when chunk retrieval fails."""
    pass