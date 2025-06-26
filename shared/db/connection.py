from abc import ABC, abstractmethod
from typing import List
from shared.classes import VectorEmbedding
from shared.logger_config import timing_decorator,db_logger


class Connection(ABC):
    """
    Abstract class that represents a connection to the database.
    Providing an additional abstraction to connect to the database.
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @abstractmethod
    @timing_decorator(db_logger)
    def insert(self, embedded_data: list[VectorEmbedding]):
        """
        Inserts one vector to the database.
        :param embedded_data:
        A transcript "chunk"
        :return:
        """
        pass
    
    @abstractmethod
    @timing_decorator(db_logger)
    def retrieve(self, embedded_data: list[float]):
        """
        Retrieves documents based on vector 
        """
        pass


    @abstractmethod
    def close(self):
        pass
