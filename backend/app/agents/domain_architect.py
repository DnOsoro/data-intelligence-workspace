from abc import ABC, abstractmethod

from app.models.agent import (
    DomainArchitectRequest,
    DomainArchitectResponse,
)


class DomainArchitect(ABC):
    @abstractmethod
    def select_tables(
        self,
        request: DomainArchitectRequest,
    ) -> DomainArchitectResponse:
        raise NotImplementedError