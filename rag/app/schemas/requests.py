from pydantic import BaseModel, HttpUrl
from enum import Enum, auto


class TypeOfRequest(str, Enum):
    STREAM = auto()
    FULL = auto()


class ChatRequest(BaseModel):
    question: str
    type_of_request: TypeOfRequest
    name_spaces: list[str] | None = None


class UploadRequest(BaseModel):
    _id: str
    _updatedAt: str
    slug: str
    title: str
    transcriptURL: HttpUrl
