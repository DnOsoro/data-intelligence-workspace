from abc import ABC, abstractmethod

from app.models.sql_agent import (
    SQLAgentRequest,
    SQLAgentResponse,
)


class SQLAgent(ABC):
    @abstractmethod
    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        raise NotImplementedError