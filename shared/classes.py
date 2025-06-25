from dataclasses import dataclass, asdict


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

    def to_dict(self) -> dict:
        """Converts the Chunk instance to a dictionary."""
        return asdict(self)


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
    text: str
    metadata: dict[str, str]

    def to_dict(self) -> dict:
        """Converts the Embedding instance to a dictionary format for storage or transmission."""
        return {
            "vector": self.vector,
            "text": self.text,
            "metadata": self.metadata
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


