import pytest

from app.agents.gemini_sql_agent import GeminiSQLAgent
from app.core.settings import settings
from app.models.sql_agent import SQLAgentRequest


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not settings.gemini_api_key,
    reason="GEMINI_API_KEY is not configured.",
)
def test_gemini_sql_agent_generates_customer_query() -> None:
    agent = GeminiSQLAgent()

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
    assert response.explanation

    sql = response.sql.upper()

    assert "SELECT" in sql
    assert "CUSTOMERS" in sql
    assert "LIFETIME_VALUE" in sql
    assert "COUNTRY" in sql