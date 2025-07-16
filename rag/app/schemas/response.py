from pydantic import BaseModel


class ChatResponse(BaseModel):
    message: str
    metadatas: list[dict[str, object]]


class UploadResponse(BaseModel):
    message: str
