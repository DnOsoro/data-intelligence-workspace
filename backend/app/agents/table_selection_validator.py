from app.models.agent import DomainArchitectResponse, TableSelection
from app.models.schema import DatasetSchema


class TableSelectionValidator:
    def validate(
        self,
        response: DomainArchitectResponse,
        dataset_schema: DatasetSchema,
    ) -> DomainArchitectResponse:
        available_tables = {
            table.name
            for table in dataset_schema.tables
        }

        normalized_selections: list[TableSelection] = []

        for selection in response.selected_tables:
            table_name = self._normalize_table_name(
                selection.table_name,
                available_tables,
            )

            if table_name not in available_tables:
                raise ValueError(
                    "Agent selected an unauthorized table: "
                    f"{selection.table_name}"
                )

            normalized_selections.append(
                TableSelection(
                    table_name=table_name,
                    relevance_reason=selection.relevance_reason,
                )
            )

        if not 0.0 <= response.confidence <= 1.0:
            raise ValueError(
                "Agent confidence must be between 0.0 and 1.0."
            )

        return DomainArchitectResponse(
            selected_tables=normalized_selections,
            confidence=response.confidence,
        )

    @staticmethod
    def _normalize_table_name(
        table_name: str,
        available_tables: set[str],
    ) -> str:
        normalized_name = table_name.strip()

        if normalized_name in available_tables:
            return normalized_name

        if "." in normalized_name:
            candidate = normalized_name.rsplit(
                ".",
                maxsplit=1,
            )[1]

            if candidate in available_tables:
                return candidate

        return normalized_name