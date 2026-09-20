from pathlib import Path

from app.agents.openrouter_domain_architect import (
    OpenRouterDomainArchitect,
)
from app.agents.openrouter_sql_agent import OpenRouterSQLAgent
from app.core.dataset_paths import DatasetPathValidator
from app.database.duckdb_manager import DuckDBManager
from app.services.dataset_manager import DatasetManager
from app.services.dataset_service import DatasetService
from app.services.query_orchestrator import QueryOrchestrator


class ApplicationRuntime:
    def __init__(self) -> None:
        self.database = DuckDBManager()

        self.dataset_service = DatasetService(
            database=self.database
        )

        project_root = Path(__file__).resolve().parents[3]
        data_root = project_root / "data"

        self.dataset_path_validator = DatasetPathValidator(
            allowed_root=data_root
        )

        self.dataset_manager = DatasetManager(
            dataset_service=self.dataset_service,
            path_validator=self.dataset_path_validator,
        )

        self.query_orchestrator = QueryOrchestrator(
            database=self.database,
            domain_architect=OpenRouterDomainArchitect(),
            sql_agent=OpenRouterSQLAgent(),
        )

    def close(self) -> None:
        self.database.close()


runtime = ApplicationRuntime()