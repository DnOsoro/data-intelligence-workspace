from time import perf_counter
from uuid import uuid4

from app.agents.domain_architect import DomainArchitect
from app.agents.sql_agent import SQLAgent
from app.database.duckdb_manager import DuckDBManager
from app.models.query import (
    QueryExecutionMetadata,
    QueryExecutionResponse,
    QueryResult,
)
from app.models.schema import DatasetSchema
from app.services.domain_architect_service import (
    DomainArchitectService,
)
from app.services.query_executor import QueryExecutor
from app.services.sql_generation_service import (
    SQLGenerationService,
)


class QueryOrchestrator:
    def __init__(
        self,
        database: DuckDBManager,
        domain_architect: DomainArchitect,
        sql_agent: SQLAgent,
    ) -> None:
        self.domain_architect_service = (
            DomainArchitectService(
                agent=domain_architect
            )
        )

        self.sql_generation_service = (
            SQLGenerationService(
                agent=sql_agent
            )
        )

        self.executor = QueryExecutor(
            database=database
        )

    def execute(
        self,
        question: str,
        dataset_schema: DatasetSchema,
    ) -> QueryExecutionResponse:
        query_id = str(uuid4())

        total_start = perf_counter()

        # Agent 1: Domain Architect
        agent_1_start = perf_counter()

        architect_response = (
            self.domain_architect_service
            .select_relevant_tables(
                question=question,
                dataset_schema=dataset_schema,
            )
        )

        agent_1_duration_ms = (
            perf_counter() - agent_1_start
        ) * 1000

        selected_table_names = [
            selection.table_name
            for selection in architect_response.selected_tables
        ]

        if not selected_table_names:
            raise ValueError(
                "Domain Architect did not select any tables."
            )

        selected_tables = {
            table.name
            for table in dataset_schema.tables
            if table.name in selected_table_names
        }

        selected_schema = DatasetSchema(
            dataset_name=dataset_schema.dataset_name,
            tables=[
                table
                for table in dataset_schema.tables
                if table.name in selected_tables
            ],
        )

        # Agent 2: SQL generation
        agent_2_start = perf_counter()

        sql_response = (
            self.sql_generation_service
            .generate_sql(
                question=question,
                dataset_schema=selected_schema,
            )
        )

        agent_2_duration_ms = (
            perf_counter() - agent_2_start
        ) * 1000

        # SQL validation
        validation_start = perf_counter()

        sql_response = (
            self.sql_generation_service
            .validate_sql(
                sql_response=sql_response,
                authorized_tables=selected_tables,
            )
        )

        sql_validation_duration_ms = (
            perf_counter() - validation_start
        ) * 1000

        # Database execution
        database_start = perf_counter()

        execution_result = self.executor.execute_validated(
            sql=sql_response.sql,
        )

        database_execution_duration_ms = (
            perf_counter() - database_start
        ) * 1000

        rows_returned = len(
            execution_result["rows"]
        )

        total_duration_ms = (
            perf_counter() - total_start
        ) * 1000

        metadata = QueryExecutionMetadata(
            query_id=query_id,
            selected_tables=selected_table_names,
            rows_returned=rows_returned,
            agent_1_duration_ms=agent_1_duration_ms,
            agent_2_duration_ms=agent_2_duration_ms,
            sql_validation_duration_ms=(
                sql_validation_duration_ms
            ),
            database_execution_duration_ms=(
                database_execution_duration_ms
            ),
            total_duration_ms=total_duration_ms,
        )

        return QueryExecutionResponse(
            question=question,
            selected_tables=selected_table_names,
            sql=sql_response.sql,
            explanation=sql_response.explanation,
            result=QueryResult(
                columns=execution_result["columns"],
                rows=execution_result["rows"],
            ),
            metadata=metadata,
        )