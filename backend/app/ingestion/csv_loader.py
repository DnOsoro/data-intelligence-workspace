from pathlib import Path

from app.core.sql_utils import validate_identifier
from app.database.duckdb_manager import DuckDBManager


class CSVLoader:
    def __init__(self, database: DuckDBManager) -> None:
        self.database = database

    def load(self, file_path: Path, table_name: str) -> None:
        validate_identifier(table_name)

        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        if file_path.suffix.lower() != ".csv":
            raise ValueError(
                f"Expected a CSV file, received: {file_path.suffix}"
            )

        escaped_path = str(file_path).replace("'", "''")

        query = f"""
        CREATE OR REPLACE TABLE "{table_name}" AS
        SELECT *
        FROM read_csv_auto('{escaped_path}')
        """

        self.database.execute(query)