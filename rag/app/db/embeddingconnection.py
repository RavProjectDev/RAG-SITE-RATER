from abc import ABC, abstractmethod
from typing import List, Dict, Any
from rag.app.schemas.data import VectorEmbedding


class EmbeddingConnection(ABC):
    """
    Abstract class that represents a connection to the database.
    Providing an additional abstraction to connect to the database.
    """

    @abstractmethod
    def insert(self, embedded_data: List[VectorEmbedding]):
        """
        Inserts one vector to the database.
        :param embedded_data:
        A transcript "chunk"
        :return:
        """
        pass

    @abstractmethod
    def retrieve(self, embedded_data: List[float]):
        """
        Retrieves documents based on vector
        """
        pass


class MetricsConnection(ABC):
    @abstractmethod
    def log(self, metric_type: str, data: Dict[str, Any]):
        pass
