from fastapi.testclient import TestClient

from app.main import app
from app.core.runtime import runtime
from app.database.duckdb_manager import DuckDBManager
from app.models.schema import (
    ColumnSchema,
    DatasetSchema,
    TableSchema,
)
from app.services.query_orchestrator import QueryOrchestrator
from app.agents.mock_domain_architect import MockDomainArchitect
from app.agents.mock_sql_agent import MockSQLAgent


client = TestClient(app)


def setup_runtime() -> str:
    runtime.database = DuckDBManager()

    runtime.database.execute(
        """
        CREATE TABLE customers (
            customer_id INTEGER,
            country VARCHAR,
            lifetime_value DOUBLE
        )
        """
    )

    runtime.database.execute(
        """
        INSERT INTO customers VALUES
            (1, 'Kenya', 125000.50),
            (2, 'Uganda', 98200.00),
            (3, 'Kenya', 67400.00)
        """
    )

    schema = DatasetSchema(
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

    dataset_id = "test-dataset-id"

    runtime.dataset_manager._datasets = {
        dataset_id: schema
    }

    runtime.query_orchestrator = QueryOrchestrator(
        database=runtime.database,
        domain_architect=MockDomainArchitect(),
        sql_agent=MockSQLAgent(),
    )

    return dataset_id


def teardown_runtime() -> None:
    runtime.database.close()


def test_query_api_returns_expected_response_contract() -> None:
    dataset_id = setup_runtime()

    try:
        response = client.post(
            "/api/query",
            json={
                "question": (
                    "Which country has the highest "
                    "lifetime customer value?"
                ),
                "dataset_id": dataset_id,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["question"] == (
            "Which country has the highest "
            "lifetime customer value?"
        )

        assert body["selected_tables"] == [
            "customers"
        ]

        assert body["sql"]
        assert body["explanation"]

        assert body["result"]["columns"]
        assert body["result"]["rows"]

        metadata = body["metadata"]

        assert metadata["query_id"]
        assert metadata["selected_tables"] == [
            "customers"
        ]
        assert metadata["rows_returned"] == (
            len(body["result"]["rows"])
        )

        assert metadata["agent_1_duration_ms"] >= 0
        assert metadata["agent_2_duration_ms"] >= 0
        assert metadata["sql_validation_duration_ms"] >= 0
        assert metadata["database_execution_duration_ms"] >= 0
        assert metadata["total_duration_ms"] >= 0

    finally:
        teardown_runtime()


def test_query_api_rejects_unknown_dataset() -> None:
    response = client.post(
        "/api/query",
        json={
            "question": "Show all customers.",
            "dataset_id": "missing-dataset-id",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Dataset not found."
    )


def test_query_api_rejects_invalid_request() -> None:
    response = client.post(
        "/api/query",
        json={
            "dataset_id": "test-dataset-id",
        },
    )

    assert response.status_code == 422