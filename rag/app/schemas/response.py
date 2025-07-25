from pydantic import BaseModel

from rag.app.models.data import SanityData, Metadata


class TranscriptData(BaseModel):
    sanity_data: SanityData
    metadata: Metadata

    def to_dict(self) -> dict:
        return {
            **self.metadata.model_dump(),
            "sanity_data": self.sanity_data.to_dict(),
        }


class ChatResponse(BaseModel):
    message: str
    transcript_data: list[TranscriptData]


class UploadResponse(BaseModel):
    message: str
