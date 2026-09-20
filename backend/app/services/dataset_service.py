from pathlib import Path

from app.database.duckdb_manager import DuckDBManager
from app.ingestion.csv_loader import CSVLoader
from app.ingestion.parquet_loader import ParquetLoader
from app.ingestion.schema_profiler import SchemaProfiler
from app.ingestion.schema_registry import SchemaRegistry
from app.models.schema import DatasetSchema


class DatasetService:
    def __init__(self, database: DuckDBManager) -> None:
        self.database = database
        self.csv_loader = CSVLoader(database)
        self.parquet_loader = ParquetLoader(database)
        self.profiler = SchemaProfiler(database)
        self.registry = SchemaRegistry()

    def load_dataset(
        self,
        file_path: Path,
        table_name: str,
        dataset_name: str,
    ) -> DatasetSchema:
        suffix = file_path.suffix.lower()

        if suffix == ".csv":
            self.csv_loader.load(
                file_path=file_path,
                table_name=table_name,
            )

        elif suffix == ".parquet":
            self.parquet_loader.load(
                file_path=file_path,
                table_name=table_name,
            )

        else:
            raise ValueError(
                f"Unsupported dataset format: {suffix}"
            )

        table_schema = self.profiler.profile_table(
            table_name
        )

        self.registry.register_table(table_schema)

        return self.registry.build_dataset_schema(
            dataset_name=dataset_name
        )

    def get_dataset_schema(
        self,
        dataset_name: str,
    ) -> DatasetSchema:
        return self.registry.build_dataset_schema(
            dataset_name=dataset_name
        )