class BaseAppException(Exception):
    """Base class for all custom exceptions."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(BaseAppException):
    """Raised when input validation fails."""
    pass


class EmbeddingError(BaseAppException):
    """Raised when embedding model fails."""
    pass


class VectorSearchError(BaseAppException):
    """Raised when MongoDB vector search fails."""
    pass


class LLMError(BaseAppException):
    """Raised when the LLM call fails."""
    pass


class PromptGenerationError(BaseAppException):
    """Raised when prompt construction fails."""
    pass
