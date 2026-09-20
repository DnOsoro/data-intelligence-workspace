from app.models.schema import DatasetSchema


class SchemaSerializer:
    def serialize(
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

                line = (
                    f"- {column.name}: "
                    f"{column.data_type} "
                    f"[{nullable}]"
                )

                if column.sample_values:
                    samples = ", ".join(
                        column.sample_values
                    )

                    line += f" SAMPLES: [{samples}]"

                lines.append(line)

            lines.append("")

        return "\n".join(lines).strip()