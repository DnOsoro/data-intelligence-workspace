from app.agents.sql_agent import SQLAgent
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


class FakeSQLAgent(SQLAgent):
    def __init__(self) -> None:
        self.last_request: SQLAgentRequest | None = None

    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        self.last_request = request

        return SQLAgentResponse(
            sql=(
                "SELECT country, "
                "MAX(lifetime_value) "
                "FROM customers "
                "GROUP BY country"
            ),
            explanation=(
                "Groups customers by country and "
                "calculates the maximum lifetime value."
            ),
        )


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


def test_generate_sql_passes_schema_context_to_agent() -> None:
    agent = FakeSQLAgent()

    service = SQLGenerationService(
        agent=agent
    )

    response = service.generate_sql(
        question="What is the highest lifetime value?",
        dataset_schema=build_dataset_schema(),
    )

    assert response.sql.startswith("SELECT")
    assert agent.last_request is not None
    assert "TABLE: customers" in (
        agent.last_request.schema_context
    )
    assert "customer_id: INTEGER" in (
        agent.last_request.schema_context
    )


def test_generate_sql_uses_only_provided_schema() -> None:
    agent = FakeSQLAgent()

    service = SQLGenerationService(
        agent=agent
    )

    schema = build_dataset_schema()

    response = service.generate_sql(
        question="Show customer values",
        dataset_schema=schema,
    )

    assert response.sql
    assert agent.last_request is not None
    assert "TABLE: customers" in (
        agent.last_request.schema_context
    )
    assert "TABLE: orders" not in (
        agent.last_request.schema_context
    )


def test_validate_sql_returns_guarded_sql() -> None:
    agent = FakeSQLAgent()

    service = SQLGenerationService(
        agent=agent
    )

    response = SQLAgentResponse(
        sql=(
            "SELECT country "
            "FROM customers"
        ),
        explanation="Lists customer countries.",
    )

    validated = service.validate_sql(
        sql_response=response,
        authorized_tables={"customers"},
    )

    assert validated.sql == (
        "SELECT country FROM customers"
    )
    assert validated.explanation == (
        "Lists customer countries."
    )