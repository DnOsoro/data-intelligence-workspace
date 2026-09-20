import time
from google import genai
from google.genai import errors

from app.agents.sql_agent import SQLAgent
from app.core.settings import settings
from app.models.sql_agent import (
    SQLAgentRequest,
    SQLAgentResponse,
)


class GeminiSQLAgent(SQLAgent):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.gemini_model

    def generate_sql(
        self,
        request: SQLAgentRequest,
    ) -> SQLAgentResponse:
        prompt = f"""
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

USER QUESTION:
{request.question}

AUTHORIZED SCHEMA:
{request.schema_context}
"""

        response = None

        for attempt in range(
            settings.gemini_max_retries + 1
        ):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": SQLAgentResponse,
                    },
                )
                break

            except errors.ServerError:
                if attempt >= settings.gemini_max_retries:
                    raise

                delay = (
                    settings.gemini_retry_delay_seconds
                    * (attempt + 1)
                )

                time.sleep(delay)

        if response is None or not response.parsed:
            raise ValueError(
                "Gemini returned an empty structured response."
            )

        return SQLAgentResponse.model_validate(
            response.parsed
        )