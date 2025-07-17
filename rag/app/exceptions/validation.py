from rag.app.exceptions.base import BaseAppException


class InputValidationError(BaseAppException):
    code: str = "input_error"
    status_code: int = 400
    description: str = "Input validation failed."

    def __init__(self, message: str | None = None):
        self.message = message or self.description
        super().__init__(self.message)
