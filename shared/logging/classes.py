from abc import ABC, abstractmethod
from enum import Enum
from shared.logging.schemas import *


class LogType(Enum):
    TIMING = "TimingLog"
    REQUEST = "RequestLog"
    ERROR = "ErrorLog"
    LLM_COST = "LLMCostLog"


class AbstractLogger(ABC):
    @abstractmethod
    def log(self, log_type: type(LogType), fields: Logmodel):
        """
        Log a message of a certain type.

        :param log_type: e.g. 'timing', 'request', 'error'
        :param fields: additional structured fields
        """
        pass
