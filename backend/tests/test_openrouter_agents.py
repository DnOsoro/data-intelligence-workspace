from app.agents.openrouter_domain_architect import (
    OpenRouterDomainArchitect,
)
from app.agents.openrouter_sql_agent import (
    OpenRouterSQLAgent,
)
from app.models.agent import DomainArchitectRequest
from app.models.sql_agent import SQLAgentRequest


def test_openrouter_domain_architect_parses_response(
    monkeypatch,
):
    def fake_generate_json(
        self,
        system_prompt,
        user_prompt,
    ):
        return {
            "selected_tables": [
                {
                    "table_name": "customers",
                    "relevance_reason": (
                        "Contains customer lifetime value."
                    ),
                }
            ],
            "confidence": 0.95,
        }

    monkeypatch.setattr(
        "app.clients.openrouter_client.OpenRouterClient.generate_json",
        fake_generate_json,
    )

    agent = OpenRouterDomainArchitect()

    request = DomainArchitectRequest(
        question=(
            "Which customers have the "
            "highest lifetime value?"
        ),
        schema_context="""
TABLE: customers

COLUMNS:
- customer_id: BIGINT
- name: VARCHAR
- country: VARCHAR
- segment: VARCHAR
- lifetime_value: DOUBLE
""",
    )

    response = agent.select_tables(request)

    assert len(response.selected_tables) == 1
    assert (
        response.selected_tables[0].table_name
        == "customers"
    )
    assert response.confidence == 0.95


def test_openrouter_sql_agent_parses_response(
    monkeypatch,
):
    def fake_generate_json(
        self,
        system_prompt,
        user_prompt,
    ):
        return {
            "sql": (
                "SELECT customer_id, name, "
                "lifetime_value "
                "FROM customers "
                "ORDER BY lifetime_value DESC "
                "LIMIT 1"
            ),
            "explanation": (
                "Returns the customer with "
                "the highest lifetime value."
            ),
        }

    monkeypatch.setattr(
        "app.clients.openrouter_client.OpenRouterClient.generate_json",
        fake_generate_json,
    )

    agent = OpenRouterSQLAgent()

    request = SQLAgentRequest(
        question=(
            "Which customers have the "
            "highest lifetime value?"
        ),
        schema_context="""
TABLE: customers

COLUMNS:
- customer_id: BIGINT
- name: VARCHAR
- country: VARCHAR
- segment: VARCHAR
- lifetime_value: DOUBLE
""",
    )

    response = agent.generate_sql(request)

    assert (
        response.sql
        == (
            "SELECT customer_id, name, "
            "lifetime_value "
            "FROM customers "
            "ORDER BY lifetime_value DESC "
            "LIMIT 1"
        )
    )

    assert (
        response.explanation
        == (
            "Returns the customer with "
            "the highest lifetime value."
        )
    )