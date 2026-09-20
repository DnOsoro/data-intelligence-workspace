from google import genai

from app.agents.domain_architect import DomainArchitect
from app.core.settings import settings
from app.models.agent import (
    DomainArchitectRequest,
    DomainArchitectResponse,
)


class GeminiDomainArchitect(DomainArchitect):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.gemini_model

    def select_tables(
        self,
        request: DomainArchitectRequest,
    ) -> DomainArchitectResponse:
        prompt = f"""
You are the Domain Architect in an enterprise
natural-language data analytics system.

Your ONLY responsibility is to identify which database
tables are relevant to answering the user's question.

Do NOT generate SQL.
Do NOT execute queries.
Do NOT invent tables.

USER QUESTION:
{request.question}

AVAILABLE SCHEMA:
{request.schema_context}

Select only tables that are relevant to answering
the user's question.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": DomainArchitectResponse,
            },
        )

        if not response.parsed:
            raise ValueError(
                "Gemini returned an empty structured response."
            )

        return DomainArchitectResponse.model_validate(
            response.parsed
        )