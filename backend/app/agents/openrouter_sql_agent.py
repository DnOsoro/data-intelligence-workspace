import time

from app.agents.sql_agent import SQLAgent
from app.clients.openrouter_client import OpenRouterClient
from app.core.settings import settings
from app.models.sql_agent import (
    SQLAgentRequest,
    SQLAgentResponse,
)


class OpenRouterSQLAgent(SQLAgent):
    def __init__(self) -> None:
        self.client = OpenRouterClient()

    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        system_prompt = """
You are the SQL Analyst in an enterprise
natural-language data analytics system.

Your responsibility is to generate ONE read-only
DuckDB SQL query that answers the user's question.

STRICT RULES:

1. Generate SQL only for the tables provided below.
2. Do not invent tables or columns.
3. Do not modify data.
4. Do not create, alter, drop, insert, update, or delete.
5. Do not execute SQL.
6. Return exactly one SQL query.
7. Use DuckDB-compatible SQL.
8. Prefer explicit column names over SELECT *.
9. Do not use tables outside the supplied schema.

Return JSON with exactly this structure:

{
  "sql": "SELECT ...",
  "explanation": "Brief explanation of what the query does."
}
"""

        user_prompt = f"""
USER QUESTION:
{request.question}

AUTHORIZED SCHEMA:
{request.schema_context}
"""

        response = None

        for attempt in range(
            settings.openrouter_max_retries + 1
        ):
            try:
                response = self.client.generate_json(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                break

            except Exception:
                if attempt >= settings.openrouter_max_retries:
                    raise

                delay = (
                    settings.openrouter_retry_delay_seconds
                    * (attempt + 1)
                )

                time.sleep(delay)

        if response is None:
            raise ValueError(
                "OpenRouter returned an empty SQL response."
            )

        try:
            return SQLAgentResponse.model_validate(
                response
            )
        except Exception as exc:
            raise ValueError(
                "OpenRouter returned an invalid "
                "SQL Agent response."
            ) from exc