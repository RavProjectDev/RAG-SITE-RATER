from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid
from enum import Enum, auto


class Chunk(BaseModel):
    """
    Represents a chunk of text with metadata and character position.

    Attributes:
        metadata (dict[str, str]): Additional metadata about the chunk (e.g., source, date).
        text (str): The raw text content of the chunk.
        chunk_size (int): The total size of the chunk in characters.
        char_start (int): The starting character index of the chunk in the original text.
        char_end (int): The ending character index of the chunk in the original text.
    """

    text: str
    chunk_size: int
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    name_space: str
    id: Optional[uuid.UUID] = None

    def to_dict(self) -> dict:
        d = self.model_dump(exclude={"text"})
        for k, v in d.items():
            if isinstance(v, uuid.UUID):
                d[k] = str(v)
        return d


class VectorEmbedding(BaseModel):
    """
    Represents an embedding vector for a chunk of text.

    Attributes:
        vector (list[float]): The embedding vector representation.
        dimension (int): The dimensionality of the embedding.
        data (Chunk): The associated Chunk object containing the source text and metadata.
    """

    vector: List[float]
    dimension: int
    data: Chunk

    def to_dict(self) -> dict:
        return {
            "vector": self.vector,
            "text": self.data.text,
            "metadata": self.data.to_dict(),
        }


class Embedding(BaseModel):
    text: str
    vector: List[float]


class Document(BaseModel):
    text: str
    metadata: Dict[str, object]
    vector: List[float]

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "vector": self.vector,
            "metadata": self.metadata,
        }


class DataSourceConfiguration(Enum):
    LOCAL = auto()


class TypeOfFormat(Enum):
    SRT = auto()
    TXT = auto()


class DataBaseConfiguration(Enum):
    PINECONE = auto()
    MONGO = auto()


class EmbeddingConfiguration(Enum):
    BERT_SMALL = "all-MiniLM-L6-v2"
    BERT_SMALL_TRANSLATED = "all-MiniLM-L6-v2"
    GEMINI = "gemini-embedding-001"
    MOCK = "mock"


class LLMModel(Enum):
    GPT_4 = "o4-mini"
    MOCK = "mock"
