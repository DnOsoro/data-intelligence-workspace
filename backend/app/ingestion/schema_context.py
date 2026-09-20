from app.models.schema import DatasetSchema, TableSchema


class SchemaContextBuilder:
    def build(
        self,
        dataset_schema: DatasetSchema,
        table_names: list[str] | None = None,
    ) -> DatasetSchema:
        if table_names is None:
            return dataset_schema

        requested_tables = set(table_names)

        selected_tables: list[TableSchema] = [
            table
            for table in dataset_schema.tables
            if table.name in requested_tables
        ]

        return DatasetSchema(
            dataset_name=dataset_schema.dataset_name,
            tables=selected_tables,
        )