from app.agents.mock_domain_architect import MockDomainArchitect
from app.models.agent import DomainArchitectRequest


def test_domain_architect_selects_relevant_table() -> None:
    agent = MockDomainArchitect()

    request = DomainArchitectRequest(
        question="Which country has the highest lifetime customer value?",
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

    response = agent.select_tables(request)

    assert len(response.selected_tables) == 1
    assert response.selected_tables[0].table_name == "customers"
    assert response.confidence == 1.0


def test_domain_architect_returns_no_tables_when_schema_is_empty() -> None:
    agent = MockDomainArchitect()

    request = DomainArchitectRequest(
        question="Which country has the highest lifetime customer value?",
        schema_context="",
    )

    response = agent.select_tables(request)

    assert response.selected_tables == []
    assert response.confidence == 0.0