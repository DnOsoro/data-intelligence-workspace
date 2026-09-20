from app.agents.mock_domain_architect import MockDomainArchitect
from app.agents.mock_sql_agent import MockSQLAgent
from app.database.duckdb_manager import DuckDBManager
from app.models.schema import (
    ColumnSchema,
    DatasetSchema,
    TableSchema,
)
from app.services.query_orchestrator import QueryOrchestrator


def build_dataset_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="customer_analytics",
        tables=[
            TableSchema(
                name="customers",
                row_count=3,
                columns=[
                    ColumnSchema(
                        name="customer_id",
                        data_type="INTEGER",
                    ),
                    ColumnSchema(
                        name="country",
                        data_type="VARCHAR",
                    ),
                    ColumnSchema(
                        name="lifetime_value",
                        data_type="DOUBLE",
                    ),
                ],
            )
        ],
    )


def test_orchestrator_runs_complete_pipeline() -> None:
    database = DuckDBManager()

    try:
        database.execute(
            """
            CREATE TABLE customers (
                customer_id INTEGER,
                country VARCHAR,
                lifetime_value DOUBLE
            )
            """
        )

        database.execute(
            """
            INSERT INTO customers VALUES
                (1, 'Kenya', 125000.50),
                (2, 'Uganda', 98200.00),
                (3, 'Kenya', 67400.00)
            """
        )

        orchestrator = QueryOrchestrator(
            database=database,
            domain_architect=MockDomainArchitect(),
            sql_agent=MockSQLAgent(),
        )

        response = orchestrator.execute(
            question=(
                "Which country has the highest "
                "lifetime customer value?"
            ),
            dataset_schema=build_dataset_schema(),
        )

        assert response.selected_tables == [
            "customers"
        ]

        assert "SELECT" in response.sql
        assert "customers" in response.sql

        assert response.result.columns
        assert response.result.rows

    finally:
        database.close()