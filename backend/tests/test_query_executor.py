import pytest

from app.core.sql_guardrails import SQLGuardrailError
from app.database.duckdb_manager import DuckDBManager
from app.services.query_executor import (
    QueryExecutionError,
    QueryExecutor,
)


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


@pytest.fixture
def executor(
    database: DuckDBManager,
) -> QueryExecutor:
    return QueryExecutor(
        database=database
    )


def test_execute_returns_columns_and_rows(
    executor: QueryExecutor,
) -> None:
    result = executor.execute(
        sql="""
        SELECT customer_id, country, lifetime_value
        FROM customers
        ORDER BY customer_id
        """,
        authorized_tables={"customers"},
    )

    assert result["columns"] == [
        "customer_id",
        "country",
        "lifetime_value",
    ]

    assert result["rows"] == [
        [1, "Kenya", 125000.50],
        [2, "Uganda", 98200.00],
        [3, "Kenya", 67400.00],
    ]


def test_execute_validates_sql_before_execution(
    executor: QueryExecutor,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        executor.execute(
            sql="""
            SELECT *
            FROM internal_users
            """,
            authorized_tables={"customers"},
        )


def test_execute_validated_runs_already_validated_sql(
    executor: QueryExecutor,
) -> None:
    result = executor.execute_validated(
        """
        SELECT country, COUNT(*) AS customer_count
        FROM customers
        GROUP BY country
        ORDER BY customer_count DESC
        """
    )

    assert result["columns"] == [
        "country",
        "customer_count",
    ]

    assert result["rows"] == [
        ["Kenya", 2],
        ["Uganda", 1],
    ]


def test_execute_validated_wraps_database_errors(
    executor: QueryExecutor,
) -> None:
    with pytest.raises(
        QueryExecutionError,
        match="Database query execution failed",
    ):
        executor.execute_validated(
            """
            SELECT *
            FROM customers
            WHERE missing_column = 1
            """
        )