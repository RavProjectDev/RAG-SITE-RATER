from dataclasses import dataclass

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


