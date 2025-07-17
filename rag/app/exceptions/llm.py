from rag.app.exceptions.base import BaseAppException


class LLMBaseException(BaseAppException):
    status_code: int = 500
    code: str = "embedding_error"
    description: str = "General LLM embedding error."

    def __init__(self, message: str | None = None):
        self.message = message or self.description
        super().__init__(self.message)


class LLMConnectionBaseException(LLMBaseException):
    status_code: int = 500
    code: str = "embedding_connection_error"
    description: str = "LLM embedding connection error."


class LLMTimeoutBaseException(LLMBaseException):
    status_code: int = 500
    code: str = "timeout_error"
    description: str = "LLM request timed out."


class LLMRequestBaseException(LLMBaseException):
    status_code: int = 500
    code: str = "request_error"
    description: str = "LLM request error."
