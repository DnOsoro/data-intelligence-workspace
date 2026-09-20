from app.agents.domain_architect import DomainArchitect
from app.clients.openrouter_client import OpenRouterClient
from app.models.agent import (
    DomainArchitectRequest,
    DomainArchitectResponse,
)


class OpenRouterDomainArchitect(DomainArchitect):
    def __init__(self) -> None:
        self.client = OpenRouterClient()

    def select_tables(
        self,
        request: DomainArchitectRequest,
    ) -> DomainArchitectResponse:
        system_prompt = """
You are the Domain Architect in an enterprise
natural-language data analytics system.

Your ONLY responsibility is to identify which database
tables are relevant to answering the user's question.

Do NOT generate SQL.
Do NOT execute queries.
Do NOT invent tables.

For every selected table, provide:
- table_name
- relevance_reason

Also provide a confidence value between 0 and 1.

Return JSON with exactly this structure:

{
  "selected_tables": [
    {
      "table_name": "example_table",
      "relevance_reason": "This table contains the data needed to answer the question."
    }
  ],
  "confidence": 0.95
}

Select only tables that are relevant to answering
the user's question.

If no available table is relevant, return:

{
  "selected_tables": [],
  "confidence": 0.0
}
"""

        user_prompt = f"""
USER QUESTION:
{request.question}

AVAILABLE SCHEMA:
{request.schema_context}
"""

        response = self.client.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        try:
            return DomainArchitectResponse.model_validate(
                response
            )
        except Exception as exc:
            raise ValueError(
                "OpenRouter returned an invalid "
                "Domain Architect response."
            ) from exc