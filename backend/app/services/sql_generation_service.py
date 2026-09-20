from app.agents.sql_agent import SQLAgent
from app.core.sql_guardrails import SQLGuardrails
from app.models.schema import DatasetSchema
from app.models.sql_agent import (
    SQLAgentRequest,
    SQLAgentResponse,
)


class SQLGenerationService:
    def __init__(
        self,
        agent: SQLAgent,
    ) -> None:
        self.agent = agent
        self.guardrails = SQLGuardrails()

    def generate_sql(
        self,
        question: str,
        dataset_schema: DatasetSchema,
    ) -> SQLAgentResponse:
        schema_context = self._build_schema_context(
            dataset_schema
        )

        request = SQLAgentRequest(
            question=question,
            schema_context=schema_context,
        )

        return self.agent.generate_sql(request)

    def validate_sql(
        self,
        sql_response: SQLAgentResponse,
        authorized_tables: set[str],
    ) -> SQLAgentResponse:
        validated_sql = self.guardrails.validate(
            sql=sql_response.sql,
            authorized_tables=authorized_tables,
        )

        return SQLAgentResponse(
            sql=validated_sql,
            explanation=sql_response.explanation,
        )

    def generate_validated_sql(
        self,
        question: str,
        dataset_schema: DatasetSchema,
    ) -> SQLAgentResponse:
        response = self.generate_sql(
            question=question,
            dataset_schema=dataset_schema,
        )

        authorized_tables = {
            table.name
            for table in dataset_schema.tables
        }

        return self.validate_sql(
            sql_response=response,
            authorized_tables=authorized_tables,
        )

    def _build_schema_context(
        self,
        dataset_schema: DatasetSchema,
    ) -> str:
        lines: list[str] = [
            f"DATASET: {dataset_schema.dataset_name}",
            "",
        ]

        for table in dataset_schema.tables:
            lines.append(f"TABLE: {table.name}")
            lines.append(f"ROWS: {table.row_count}")
            lines.append("")
            lines.append("COLUMNS:")

            for column in table.columns:
                nullable = (
                    "NULLABLE"
                    if column.nullable
                    else "NOT NULL"
                )

                lines.append(
                    f"- {column.name}: "
                    f"{column.data_type} "
                    f"[{nullable}]"
                )

            lines.append("")

        return "\n".join(lines).strip()