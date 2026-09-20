import duckdb


class DuckDBManager:
    def __init__(self) -> None:
        self.connection = duckdb.connect(database=":memory:")

    def execute(self, query: str) -> duckdb.DuckDBPyConnection:
        return self.connection.execute(query)

    def close(self) -> None:
        self.connection.close()