from app.agents.mock_sql_agent import MockSQLAgent
from app.models.sql_agent import SQLAgentRequest


def test_mock_sql_agent_generates_sql() -> None:
    agent = MockSQLAgent()

    request = SQLAgentRequest(
        question=(
            "Which country has the highest "
            "lifetime customer value?"
        ),
        schema_context="""DATASET: customer_analytics

TABLE: customers
ROWS: 8

COLUMNS:
- customer_id: BIGINT
- name: VARCHAR
- country: VARCHAR
- segment: VARCHAR
- lifetime_value: DOUBLE
""",
    )

    response = agent.generate_sql(request)

    assert response.sql
    assert "SELECT" in response.sql
    assert "customers" in response.sql
    assert "lifetime_value" in response.sql
    assert response.explanation