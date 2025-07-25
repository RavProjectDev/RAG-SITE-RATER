from pydantic import BaseModel, Field, HttpUrl


class Metadata(BaseModel):
    chunk_size: int
    time_start: str | None = None
    time_end: str | None = None
    name_space: str


class SanityData(BaseModel):
    id: str
    slug: str
    title: str
    transcriptURL: HttpUrl
    hash: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "transcriptURL": str(self.transcriptURL),
            "hash": self.hash,
        }


class DocumentModel(BaseModel):
    id: str = Field(..., alias="_id")  # e.g. {"$oid": "687c65e061b769c8ff78779f"}
    text: str
    metadata: Metadata
    sanity_data: SanityData
    score: float

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata.model_dump(),
            "sanity_data": self.sanity_data.to_dict(),
            "score": self.score,
        }
