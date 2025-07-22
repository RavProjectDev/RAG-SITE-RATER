from pydantic import BaseModel

from rag.app.models.data import DocumentModel


class UploadRatingsRequest(BaseModel):
    user_question: str
    ratings: tuple[DocumentModel, int]


class RatingsModel(BaseModel):
    user_question: str
    ratings: tuple[DocumentModel, int]
