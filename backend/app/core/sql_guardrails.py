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
            table.name
            for table in expression.find_all(exp.Table)
        }

        unauthorized_tables = (
            referenced_tables - authorized_tables
        )

        if unauthorized_tables:
            raise SQLGuardrailError(
                "SQL references unauthorized tables: "
                + ", ".join(sorted(unauthorized_tables))
            )

        return sql.strip()