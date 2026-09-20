from app.database.duckdb_manager import DuckDBManager
from app.models.schema import ColumnSchema, TableSchema


class SchemaProfiler:
    def __init__(self, database: DuckDBManager) -> None:
        self.database = database

    def profile_table(self, table_name: str) -> TableSchema:
        columns_result = self.database.execute(
            f"DESCRIBE {table_name}"
        ).fetchall()

        row_count = self.database.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        columns: list[ColumnSchema] = []

        for column in columns_result:
            column_name = column[0]
            data_type = column[1]
            nullable = column[2] == "YES"

            sample_result = self.database.execute(
                f"""
                SELECT "{column_name}"
                FROM {table_name}
                WHERE "{column_name}" IS NOT NULL
                LIMIT 5
                """
            ).fetchall()

            sample_values = [
                str(row[0])
                for row in sample_result
            ]

            columns.append(
                ColumnSchema(
                    name=column_name,
                    data_type=data_type,
                    nullable=nullable,
                    sample_values=sample_values,
                )
            )

        return TableSchema(
            name=table_name,
            row_count=row_count,
            columns=columns,
        )