import pytest

from app.core.sql_guardrails import (
    SQLGuardrailError,
    SQLGuardrails,
)


@pytest.fixture
def guardrails() -> SQLGuardrails:
    return SQLGuardrails()


def test_accepts_authorized_select(
    guardrails: SQLGuardrails,
) -> None:
    sql = """
    SELECT country, SUM(lifetime_value) AS total_value
    FROM customers
    GROUP BY country
    ORDER BY total_value DESC
    """

    result = guardrails.validate(
        sql=sql,
        authorized_tables={"customers"},
    )

    assert result == sql.strip()


def test_rejects_empty_sql(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="cannot be empty",
    ):
        guardrails.validate(
            sql="",
            authorized_tables={"customers"},
        )


def test_rejects_insert(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        guardrails.validate(
            sql=(
                "INSERT INTO customers "
                "(customer_id) VALUES (99)"
            ),
            authorized_tables={"customers"},
        )


def test_rejects_update(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        guardrails.validate(
            sql=(
                "UPDATE customers "
                "SET country = 'Kenya'"
            ),
            authorized_tables={"customers"},
        )


def test_rejects_delete(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        guardrails.validate(
            sql="DELETE FROM customers",
            authorized_tables={"customers"},
        )


def test_rejects_drop(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        guardrails.validate(
            sql="DROP TABLE customers",
            authorized_tables={"customers"},
        )


def test_rejects_create(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        guardrails.validate(
            sql=(
                "CREATE TABLE malicious "
                "(id INTEGER)"
            ),
            authorized_tables={"customers"},
        )


def test_rejects_unauthorized_table(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        guardrails.validate(
            sql=(
                "SELECT * "
                "FROM internal_users"
            ),
            authorized_tables={"customers"},
        )


def test_rejects_invalid_sql(
    guardrails: SQLGuardrails,
) -> None:
    with pytest.raises(
        SQLGuardrailError,
        match="Invalid SQL",
    ):
        guardrails.validate(
            sql="SELECT FROM",
            authorized_tables={"customers"},
        )


def test_accepts_authorized_join(
    guardrails: SQLGuardrails,
) -> None:
    sql = """
    SELECT c.country, o.total
    FROM customers AS c
    JOIN customer_orders AS o
        ON c.customer_id = o.customer_id
    """

    result = guardrails.validate(
        sql=sql,
        authorized_tables={
            "customers",
            "customer_orders",
        },
    )

    assert result == sql.strip()


def test_rejects_unauthorized_table_in_join(
    guardrails: SQLGuardrails,
) -> None:
    sql = """
    SELECT c.country, u.email
    FROM customers AS c
    JOIN internal_users AS u
        ON c.customer_id = u.customer_id
    """

    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        guardrails.validate(
            sql=sql,
            authorized_tables={"customers"},
        )


def test_accepts_authorized_subquery(
    guardrails: SQLGuardrails,
) -> None:
    sql = """
    SELECT *
    FROM customers
    WHERE lifetime_value > (
        SELECT AVG(lifetime_value)
        FROM customers
    )
    """

    result = guardrails.validate(
        sql=sql,
        authorized_tables={"customers"},
    )

    assert result == sql.strip()


def test_rejects_unauthorized_table_in_subquery(
    guardrails: SQLGuardrails,
) -> None:
    sql = """
    SELECT *
    FROM customers
    WHERE lifetime_value > (
        SELECT AVG(balance)
        FROM internal_accounts
    )
    """

    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        guardrails.validate(
            sql=sql,
            authorized_tables={"customers"},
        )


def test_accepts_table_alias(
    guardrails: SQLGuardrails,
) -> None:
    sql = """
    SELECT c.country
    FROM customers AS c
    """

    result = guardrails.validate(
        sql=sql,
        authorized_tables={"customers"},
    )

    assert result == sql.strip()