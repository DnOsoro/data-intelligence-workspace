from sqlglot import exp, parse_one


class SQLGuardrailError(ValueError):
    pass


class SQLGuardrails:
    def validate(
        self,
        sql: str,
        authorized_tables: set[str],
    ) -> str:
        if not sql.strip():
            raise SQLGuardrailError(
                "SQL query cannot be empty."
            )

        try:
            expression = parse_one(
                sql,
                read="duckdb",
            )
        except Exception as exc:
            raise SQLGuardrailError(
                f"Invalid SQL: {exc}"
            ) from exc

        if not isinstance(expression, exp.Query):
            raise SQLGuardrailError(
                "Only read-only SQL queries are allowed."
            )

        forbidden_nodes = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Create,
            exp.Alter,
            exp.Merge,
        )

        for node_type in forbidden_nodes:
            if expression.find(node_type):
                raise SQLGuardrailError(
                    "Write or schema-modifying SQL is not allowed."
                )

        referenced_tables = {
            self._build_table_reference(table)
            for table in expression.find_all(exp.Table)
        }

        unauthorized_tables = {
            table_reference
            for table_reference in referenced_tables
            if not self._is_authorized_table(
                table_reference=table_reference,
                authorized_tables=authorized_tables,
            )
        }

        if unauthorized_tables:
            raise SQLGuardrailError(
                "SQL references unauthorized tables: "
                + ", ".join(sorted(unauthorized_tables))
            )

        return sql.strip()

    @staticmethod
    def _build_table_reference(
        table: exp.Table,
    ) -> str:
        parts = []

        if table.catalog:
            parts.append(table.catalog)

        if table.db:
            parts.append(table.db)

        parts.append(table.name)

        return ".".join(parts)

    @staticmethod
    def _is_authorized_table(
        table_reference: str,
        authorized_tables: set[str],
    ) -> bool:
        if table_reference in authorized_tables:
            return True

        if "." in table_reference:
            return False

        return table_reference in authorized_tables