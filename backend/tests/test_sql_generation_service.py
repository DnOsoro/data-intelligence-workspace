import pytest

from app.agents.mock_sql_agent import MockSQLAgent
from app.agents.sql_agent import SQLAgent
from app.core.sql_guardrails import SQLGuardrailError
from app.models.schema import (
    ColumnSchema,
    DatasetSchema,
    TableSchema,
)
from app.models.sql_agent import (
    SQLAgentRequest,
    SQLAgentResponse,
)
from app.services.sql_generation_service import (
    SQLGenerationService,
)


def build_dataset_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="customer_analytics",
        tables=[
            TableSchema(
                name="customers",
                row_count=8,
                columns=[
                    ColumnSchema(
                        name="customer_id",
                        data_type="BIGINT",
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


def test_service_returns_validated_sql() -> None:
    service = SQLGenerationService(
        agent=MockSQLAgent()
    )

    response = service.generate_validated_sql(
        question=(
            "Which country has the highest "
            "lifetime customer value?"
        ),
        dataset_schema=build_dataset_schema(),
    )

    assert response.sql
    assert "SELECT" in response.sql
    assert "customers" in response.sql
    assert response.explanation


class UnauthorizedSQLAgent(SQLAgent):
    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        return SQLAgentResponse(
            sql=(
                "SELECT * "
                "FROM internal_users"
            ),
            explanation="Unauthorized query.",
        )


class WriteSQLAgent(SQLAgent):
    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        return SQLAgentResponse(
            sql="DELETE FROM customers",
            explanation="Malicious query.",
        )


def test_service_rejects_unauthorized_table() -> None:
    service = SQLGenerationService(
        agent=UnauthorizedSQLAgent()
    )

    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        service.generate_validated_sql(
            question="Show internal users.",
            dataset_schema=build_dataset_schema(),
        )


def test_service_rejects_write_query() -> None:
    service = SQLGenerationService(
        agent=WriteSQLAgent()
    )

    with pytest.raises(
        SQLGuardrailError,
        match="read-only",
    ):
        service.generate_validated_sql(
            question="Delete customers.",
            dataset_schema=build_dataset_schema(),
        )

class MaliciousJoinSQLAgent(SQLAgent):
    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        return SQLAgentResponse(
            sql=(
                "SELECT * "
                "FROM customers "
                "JOIN internal_users "
                "ON customers.customer_id = internal_users.customer_id"
            ),
            explanation="Attempted unauthorized join.",
        )


def test_service_rejects_unauthorized_join() -> None:
    service = SQLGenerationService(
        agent=MaliciousJoinSQLAgent()
    )

    with pytest.raises(
        SQLGuardrailError,
        match="unauthorized tables",
    ):
        service.generate_validated_sql(
            question="Show customer and internal user data.",
            dataset_schema=build_dataset_schema(),
        )
