from app.core.sql_guardrails import SQLGuardrails
from app.database.duckdb_manager import DuckDBManager


class QueryExecutionError(RuntimeError):
    pass


class QueryExecutor:
    def __init__(
        self,
        database: DuckDBManager,
    ) -> None:
        self.database = database
        self.guardrails = SQLGuardrails()

    def execute(
        self,
        sql: str,
        authorized_tables: set[str],
    ) -> dict:
        validated_sql = self.guardrails.validate(
            sql=sql,
            authorized_tables=authorized_tables,
        )

        return self.execute_validated(
            validated_sql
        )

    def execute_validated(
        self,
        sql: str,
    ) -> dict:
        try:
            result = self.database.execute(sql)

            columns = [
                description[0]
                for description in result.description
            ]

            rows = [
                list(row)
                for row in result.fetchall()
            ]

            return {
                "columns": columns,
                "rows": rows,
            }

        except Exception as exc:
            raise QueryExecutionError(
                "Database query execution failed."
            ) from exc