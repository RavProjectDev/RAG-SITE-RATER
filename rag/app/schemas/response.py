from pydantic import BaseModel

from rag.app.models.data import SanityData, Metadata


class TranscriptData(BaseModel):
    sanity_data: SanityData
    metadata: Metadata


class ChatResponse(BaseModel):
    message: str
    transcript_data: list[TranscriptData]


class UploadResponse(BaseModel):
    message: str
