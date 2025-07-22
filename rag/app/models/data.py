from pydantic import BaseModel, Field, HttpUrl


class Metadata(BaseModel):
    chunk_size: int
    time_start: str
    time_end: str
    name_space: str


class SanityData(BaseModel):
    id: str
    slug: str
    title: str
    transcriptURL: HttpUrl


class DocumentModel(BaseModel):
    id: str = Field(..., alias="_id")  # e.g. {"$oid": "687c65e061b769c8ff78779f"}
    text: str
    metadata: Metadata
    sanity_data: SanityData
    score: float
