from enum import Enum, auto


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
    GEMINI = "embedding-001"


class LLMModel(Enum):
    GPT_4 = "o4-mini"
