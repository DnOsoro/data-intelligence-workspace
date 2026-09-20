import pytest

from app.core.sql_guardrails import SQLGuardrailError
from app.database.duckdb_manager import DuckDBManager
from app.services.query_executor import QueryExecutor


@pytest.fixture
def database() -> DuckDBManager:
    database = DuckDBManager()

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

    yield database

    database.close()


def test_executor_returns_rows(
    database: DuckDBManager,
) -> None:
    executor = QueryExecutor(database)

    result = executor.execute(
        sql=(
            "SELECT country, "
            "SUM(lifetime_value) AS total_value "
            "FROM customers "
            "GROUP BY country "
            "ORDER BY total_value DESC"
        ),
        authorized_tables={"customers"},
    )

    assert result["columns"] == [
        "country",
        "total_value",
    ]

    assert len(result["rows"]) == 2
    assert result["rows"][0][0] == "Kenya"


def test_executor_rejects_unauthorized_table(
    database: DuckDBManager,
) -> None:
    executor = QueryExecutor(database)

    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        executor.execute(
            sql="SELECT * FROM internal_users",
            authorized_tables={"customers"},
        )


def test_executor_rejects_write_query(
    database: DuckDBManager,
) -> None:
    executor = QueryExecutor(database)

    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        executor.execute(
            sql="DELETE FROM customers",
            authorized_tables={"customers"},
        )
