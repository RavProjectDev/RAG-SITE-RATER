from dataclasses import dataclass, asdict
import uuid

@dataclass
class Chunk:
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
    char_start: int
    char_end: int
    time_start: str | None
    time_end: str | None
    name_space: str
    id: uuid.UUID | None

    def to_dict(self) -> dict:
        d = {k: v for k, v in asdict(self).items() if k != "text"}
        for k, v in d.items():
            if isinstance(v, uuid.UUID):
                d[k] = str(v)
        return d


@dataclass
class VectorEmbedding:
    """
    Represents an embedding vector for a chunk of text.

    Attributes:
        vector (list[float]): The embedding vector representation.
        dimension (int): The dimensionality of the embedding.
        data (Chunk): The associated Chunk object containing the source text and metadata.
    """
    vector: list[float]
    dimension: int
    data: Chunk
    def to_dict(self) -> dict:
        """Converts the Embedding instance to a dictionary format for storage or transmission."""

        return {
            "vector": self.vector,
            "text": self.data.text,
            "metadata": self.data.to_dict(),
        }


@dataclass
class Embedding:
    text: str
    vector: list[float]


@dataclass
class Document:
    text: str
    metadata: dict
    vector: list[float]
    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "vector": self.vector,
            "metadata": self.metadata,
        }


