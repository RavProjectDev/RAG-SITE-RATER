from pydantic import BaseModel, Field

from rag.app.models.data import DocumentModel, SanityData, Metadata


class UploadRatingsDocument(BaseModel):
    id: str = Field(..., alias="_id")  # e.g. {"$oid": "687c65e061b769c8ff78779f"}
    text: str
    metadata: Metadata
    sanity_data: SanityData
    score: float
    rating: float


class UploadRatingsRequest(BaseModel):
    user_question: str
    data: list[tuple[DocumentModel, int]]
    embedding_type: str


class RatingsModel(BaseModel):
    user_question: str
    ratings: tuple[DocumentModel, int]
    embedding_type: str

    def to_dict(self) -> dict:
        return {
            "user_question": self.user_question,
            "document": self.ratings[0].to_dict(),
            "rating": self.ratings[1],
            "embedding_type": self.embedding_type,
        }


class Ratings(BaseModel):
    user_question: str
    ratings: list[tuple[DocumentModel, int]]
