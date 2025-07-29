from pydantic import BaseModel

from rag.app.models.data import SanityData, Metadata, DocumentModel


class TranscriptData(BaseModel):
    sanity_data: SanityData
    metadata: Metadata
    score: float

    def to_dict(self) -> dict:
        return {
            **self.metadata.model_dump(),
            "sanity_data": self.sanity_data.to_dict(),
            "score": self.score,
        }


class ChatResponse(BaseModel):
    message: str
    transcript_data: list[TranscriptData]


class UploadResponse(BaseModel):
    message: str


class FormGetChunksResponse(BaseModel):
    embedding_type: str
    documents: list[DocumentModel]
