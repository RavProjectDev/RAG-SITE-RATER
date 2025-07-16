import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from rag.app.schemas.data import VectorEmbedding
from contextlib import contextmanager


class EmbeddingConnection(ABC):
    """
    Abstract class that represents a connection to the database.
    Providing an additional abstraction to connect to the database.
    """

    @abstractmethod
    async def insert(self, embedded_data: List[VectorEmbedding]):
        """
        Inserts one vector to the database.
        :param embedded_data:
        A transcript "chunk"
        :return:
        """
        pass

    @abstractmethod
    async def retrieve(
        self, embedded_data: List[float], name_spaces: list[str] | None = None
    ):
        """
        Retrieves documents based on vector
        """
        pass


class MetricsConnection(ABC):
    @abstractmethod
    def log(self, metric_type: str, data: Dict[str, Any]):
        pass

    @contextmanager
    def timed(self, metric_type: str, data: Dict[str, Any]):
        """
        Context manager to time a block and automatically log the duration.
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            data_with_duration = {**data, "duration": f"{duration:.4f}"}
            self.log(metric_type, data_with_duration)
