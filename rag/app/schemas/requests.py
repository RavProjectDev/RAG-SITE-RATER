from pydantic import BaseModel, HttpUrl, field_validator, Field
from enum import Enum, auto


class TypeOfRequest(str, Enum):
    STREAM = "STREAM"
    FULL = "FULL"


class ChatRequest(BaseModel):
    question: str
    type_of_request: TypeOfRequest
    name_spaces: list[str] | None = None

    class ChatRequest(BaseModel):
        question: str
        type_of_request: TypeOfRequest
        name_spaces: list[str] | None = None

        @classmethod
        @field_validator("question")
        def question_validator(cls, v: str) -> str:
            if not v.strip():
                raise ValueError("question cannot be empty")
            return v


class UploadRequest(BaseModel):
    id: str
    _updatedAt: str
    slug: str
    title: str
    transcriptURL: HttpUrl

    @classmethod
    @field_validator("transcriptURL")
    def must_be_srt(cls, v):
        if not str(v).lower().endswith(".srt"):
            raise ValueError("transcriptURL must end with .srt")
        return v
