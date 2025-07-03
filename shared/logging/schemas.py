from pydantic import BaseModel

from shared.enums import LLMModel


class Logmodel(BaseModel):
    pass


class TimingLog(Logmodel):
    operation: str
    duration_seconds: float
    message: str | None = None


class RequestLog(Logmodel):
    endpoint: str
    method: str
    status_code: int
    user_id: str | None = None


class ErrorLog(Logmodel):
    operation: str
    error_message: str
    exception_type: str | None = None


class LLMCostLog(Logmodel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_model: LLMModel
    model: str
