import pytest

from app.agents.gemini_domain_architect import (
    GeminiDomainArchitect,
)
from app.core.settings import settings
from app.models.agent import DomainArchitectRequest


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not settings.gemini_api_key,
    reason="GEMINI_API_KEY is not configured.",
)
def test_gemini_domain_architect_selects_customer_table() -> None:
    agent = GeminiDomainArchitect()

    request = DomainArchitectRequest(
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

    response = agent.select_tables(request)

    table_names = {
        selection.table_name
        for selection in response.selected_tables
    }

    assert "customers" in table_names
    assert 0.0 <= response.confidence <= 1.0