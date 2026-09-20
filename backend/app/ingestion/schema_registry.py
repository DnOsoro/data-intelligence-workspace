from app.models.schema import DatasetSchema, TableSchema


class SchemaRegistry:
    def __init__(self) -> None:
        self._tables: dict[str, TableSchema] = {}

    def register_table(self, table_schema: TableSchema) -> None:
        self._tables[table_schema.name] = table_schema

    def get_table(self, table_name: str) -> TableSchema | None:
        return self._tables.get(table_name)

    def list_tables(self) -> list[TableSchema]:
        return list(self._tables.values())

    def build_dataset_schema(
        self,
        dataset_name: str,
    ) -> DatasetSchema:
        return DatasetSchema(
            dataset_name=dataset_name,
            tables=self.list_tables(),
        )

    def clear(self) -> None:
        self._tables.clear()