from pathlib import Path

import pytest

from app.database.duckdb_manager import DuckDBManager
from app.ingestion.csv_loader import CSVLoader
from app.ingestion.parquet_loader import ParquetLoader
from app.ingestion.schema_context import SchemaContextBuilder
from app.ingestion.schema_profiler import SchemaProfiler
from app.ingestion.schema_registry import SchemaRegistry
from app.ingestion.schema_serializer import SchemaSerializer
from app.services.dataset_service import DatasetService


SAMPLES_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "samples"
)


def test_csv_ingestion_and_schema_profiling() -> None:
    database = DuckDBManager()

    loader = CSVLoader(database)
    profiler = SchemaProfiler(database)

    file_path = SAMPLES_DIR / "customers.csv"

    loader.load(
        file_path=file_path,
        table_name="customers",
    )

    schema = profiler.profile_table("customers")

    assert schema.name == "customers"
    assert schema.row_count == 8
    assert len(schema.columns) == 5

    customer_id = next(
        column
        for column in schema.columns
        if column.name == "customer_id"
    )

    assert customer_id.data_type == "BIGINT"


def test_parquet_ingestion_and_schema_profiling() -> None:
    database = DuckDBManager()

    loader = ParquetLoader(database)
    profiler = SchemaProfiler(database)

    file_path = SAMPLES_DIR / "customers.parquet"

    loader.load(
        file_path=file_path,
        table_name="customers_parquet",
    )

    schema = profiler.profile_table("customers_parquet")

    assert schema.name == "customers_parquet"
    assert schema.row_count == 8
    assert len(schema.columns) == 5

    customer_id = next(
        column
        for column in schema.columns
        if column.name == "customer_id"
    )

    assert customer_id.data_type == "BIGINT"


def test_invalid_table_name_is_rejected() -> None:
    database = DuckDBManager()

    loader = CSVLoader(database)

    file_path = SAMPLES_DIR / "customers.csv"

    with pytest.raises(ValueError):
        loader.load(
            file_path=file_path,
            table_name="customers; DROP TABLE customers",
        )


def test_missing_csv_file_is_rejected() -> None:
    database = DuckDBManager()

    loader = CSVLoader(database)

    missing_file = SAMPLES_DIR / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError):
        loader.load(
            file_path=missing_file,
            table_name="missing_customers",
        )


def test_schema_registry_registers_and_retrieves_tables() -> None:
    database = DuckDBManager()

    loader = CSVLoader(database)
    profiler = SchemaProfiler(database)
    registry = SchemaRegistry()

    file_path = SAMPLES_DIR / "customers.csv"

    loader.load(
        file_path=file_path,
        table_name="customers",
    )

    schema = profiler.profile_table("customers")

    registry.register_table(schema)

    registered = registry.get_table("customers")

    assert registered is not None
    assert registered.name == "customers"
    assert registered.row_count == 8


def test_schema_registry_builds_dataset_schema() -> None:
    database = DuckDBManager()

    loader = CSVLoader(database)
    profiler = SchemaProfiler(database)
    registry = SchemaRegistry()

    file_path = SAMPLES_DIR / "customers.csv"

    loader.load(
        file_path=file_path,
        table_name="customers",
    )

    schema = profiler.profile_table("customers")

    registry.register_table(schema)

    dataset_schema = registry.build_dataset_schema(
        dataset_name="customer_analytics"
    )

    assert dataset_schema.dataset_name == "customer_analytics"
    assert len(dataset_schema.tables) == 1
    assert dataset_schema.tables[0].name == "customers"


def test_schema_registry_can_register_multiple_tables() -> None:
    database = DuckDBManager()

    loader = CSVLoader(database)
    profiler = SchemaProfiler(database)
    registry = SchemaRegistry()

    csv_path = SAMPLES_DIR / "customers.csv"
    parquet_path = SAMPLES_DIR / "customers.parquet"

    loader.load(
        file_path=csv_path,
        table_name="customers",
    )

    parquet_loader = ParquetLoader(database)

    parquet_loader.load(
        file_path=parquet_path,
        table_name="customers_archive",
    )

    customers_schema = profiler.profile_table("customers")
    archive_schema = profiler.profile_table("customers_archive")

    registry.register_table(customers_schema)
    registry.register_table(archive_schema)

    tables = registry.list_tables()

    assert len(tables) == 2

    table_names = {table.name for table in tables}

    assert table_names == {
        "customers",
        "customers_archive",
    }


def test_dataset_service_loads_csv_and_registers_schema() -> None:
    database = DuckDBManager()

    service = DatasetService(database)

    file_path = SAMPLES_DIR / "customers.csv"

    dataset_schema = service.load_dataset(
        file_path=file_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    assert dataset_schema.dataset_name == "customer_analytics"
    assert len(dataset_schema.tables) == 1

    table = dataset_schema.tables[0]

    assert table.name == "customers"
    assert table.row_count == 8
    assert len(table.columns) == 5


def test_dataset_service_loads_parquet_and_registers_schema() -> None:
    database = DuckDBManager()

    service = DatasetService(database)

    file_path = SAMPLES_DIR / "customers.parquet"

    dataset_schema = service.load_dataset(
        file_path=file_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    assert dataset_schema.dataset_name == "customer_analytics"
    assert len(dataset_schema.tables) == 1

    table = dataset_schema.tables[0]

    assert table.name == "customers"
    assert table.row_count == 8
    assert len(table.columns) == 5


def test_dataset_service_rejects_unsupported_format() -> None:
    database = DuckDBManager()

    service = DatasetService(database)

    file_path = SAMPLES_DIR / "customers.json"

    with pytest.raises(ValueError, match="Unsupported dataset format"):
        service.load_dataset(
            file_path=file_path,
            table_name="customers",
            dataset_name="customer_analytics",
        )


def test_schema_serializer_produces_deterministic_schema_context() -> None:
    database = DuckDBManager()

    service = DatasetService(database)
    serializer = SchemaSerializer()

    file_path = SAMPLES_DIR / "customers.csv"

    dataset_schema = service.load_dataset(
        file_path=file_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    serialized = serializer.serialize(dataset_schema)

    expected = """DATASET: customer_analytics

TABLE: customers
ROWS: 8

COLUMNS:
- customer_id: BIGINT [NULLABLE] SAMPLES: [1, 2, 3, 4, 5]
- name: VARCHAR [NULLABLE] SAMPLES: [Acme Corporation, Globex Industries, Northwind Traders, Contoso Ltd, Initech]
- country: VARCHAR [NULLABLE] SAMPLES: [Kenya, Uganda, Tanzania, Rwanda, Kenya]
- segment: VARCHAR [NULLABLE] SAMPLES: [Enterprise, Enterprise, SMB, SMB, Mid-Market]
- lifetime_value: DOUBLE [NULLABLE] SAMPLES: [125000.5, 98200.0, 45100.75, 38250.25, 67400.0]"""

    assert serialized == expected


def test_schema_serializer_supports_multiple_tables() -> None:
    database = DuckDBManager()

    service = DatasetService(database)
    serializer = SchemaSerializer()

    csv_path = SAMPLES_DIR / "customers.csv"
    parquet_path = SAMPLES_DIR / "customers.parquet"

    service.load_dataset(
        file_path=csv_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    dataset_schema = service.load_dataset(
        file_path=parquet_path,
        table_name="customers_archive",
        dataset_name="customer_analytics",
    )

    serialized = serializer.serialize(dataset_schema)

    assert "TABLE: customers" in serialized
    assert "TABLE: customers_archive" in serialized
    assert "customer_id" in serialized
    assert "lifetime_value" in serialized


def test_schema_context_builder_returns_full_schema_by_default() -> None:
    database = DuckDBManager()

    service = DatasetService(database)
    builder = SchemaContextBuilder()

    file_path = SAMPLES_DIR / "customers.csv"

    dataset_schema = service.load_dataset(
        file_path=file_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    filtered_schema = builder.build(dataset_schema)

    assert filtered_schema.dataset_name == "customer_analytics"
    assert len(filtered_schema.tables) == 1
    assert filtered_schema.tables[0].name == "customers"


def test_schema_context_builder_filters_tables() -> None:
    database = DuckDBManager()

    service = DatasetService(database)
    builder = SchemaContextBuilder()

    csv_path = SAMPLES_DIR / "customers.csv"
    parquet_path = SAMPLES_DIR / "customers.parquet"

    service.load_dataset(
        file_path=csv_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    dataset_schema = service.load_dataset(
        file_path=parquet_path,
        table_name="customers_archive",
        dataset_name="customer_analytics",
    )

    filtered_schema = builder.build(
        dataset_schema,
        table_names=["customers"],
    )

    assert filtered_schema.dataset_name == "customer_analytics"
    assert len(filtered_schema.tables) == 1
    assert filtered_schema.tables[0].name == "customers"


def test_schema_context_builder_ignores_unknown_tables() -> None:
    database = DuckDBManager()

    service = DatasetService(database)
    builder = SchemaContextBuilder()

    file_path = SAMPLES_DIR / "customers.csv"

    dataset_schema = service.load_dataset(
        file_path=file_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    filtered_schema = builder.build(
        dataset_schema,
        table_names=["does_not_exist"],
    )

    assert filtered_schema.dataset_name == "customer_analytics"
    assert filtered_schema.tables == []


def test_dataset_service_isolates_datasets() -> None:
    database = DuckDBManager()

    service = DatasetService(database)

    customers_path = SAMPLES_DIR / "customers.csv"
    archive_path = SAMPLES_DIR / "customers.parquet"

    customer_dataset = service.load_dataset(
        file_path=customers_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    archive_dataset = service.load_dataset(
        file_path=archive_path,
        table_name="customers_archive",
        dataset_name="archive_analytics",
    )

    assert customer_dataset.dataset_name == "customer_analytics"
    assert [
        table.name
        for table in customer_dataset.tables
    ] == ["customers"]

    assert archive_dataset.dataset_name == "archive_analytics"
    assert [
        table.name
        for table in archive_dataset.tables
    ] == ["customers_archive"]


def test_schema_profiler_handles_empty_columns() -> None:
    database = DuckDBManager()

    try:
        database.execute(
            """
            CREATE TABLE empty_column_test (
                id INTEGER,
                empty_value VARCHAR
            )
            """
        )

        database.execute(
            """
            INSERT INTO empty_column_test
            VALUES
                (1, NULL),
                (2, NULL),
                (3, NULL)
            """
        )

        profiler = SchemaProfiler(database)

        schema = profiler.profile_table(
            "empty_column_test"
        )

        assert schema.name == "empty_column_test"
        assert schema.row_count == 3
        assert len(schema.columns) == 2

        empty_column = next(
            column
            for column in schema.columns
            if column.name == "empty_value"
        )

        assert empty_column.sample_values == []

    finally:
        database.close()


def test_schema_profiler_collects_non_null_sample_values() -> None:
    database = DuckDBManager()

    try:
        database.execute(
            """
            CREATE TABLE sample_values_test (
                id INTEGER,
                category VARCHAR
            )
            """
        )

        database.execute(
            """
            INSERT INTO sample_values_test
            VALUES
                (1, 'Enterprise'),
                (2, NULL),
                (3, 'SMB'),
                (4, NULL),
                (5, 'Startup'),
                (6, 'Government'),
                (7, 'Education')
            """
        )

        profiler = SchemaProfiler(database)

        schema = profiler.profile_table(
            "sample_values_test"
        )

        category_column = next(
            column
            for column in schema.columns
            if column.name == "category"
        )

        assert len(category_column.sample_values) == 5

        assert all(
            isinstance(value, str)
            for value in category_column.sample_values
        )

        assert None not in category_column.sample_values

        assert set(
            category_column.sample_values
        ).issubset(
            {
                "Enterprise",
                "SMB",
                "Startup",
                "Government",
                "Education",
            }
        )

    finally:
        database.close()


def test_schema_context_builder_excludes_unknown_tables_from_mixed_selection() -> None:
    database = DuckDBManager()

    service = DatasetService(database)
    builder = SchemaContextBuilder()

    file_path = SAMPLES_DIR / "customers.csv"

    dataset_schema = service.load_dataset(
        file_path=file_path,
        table_name="customers",
        dataset_name="customer_analytics",
    )

    filtered_schema = builder.build(
        dataset_schema,
        table_names=[
            "customers",
            "payments",
            "internal_users",
        ],
    )

    assert filtered_schema.dataset_name == "customer_analytics"

    assert [
        table.name
        for table in filtered_schema.tables
    ] == ["customers"]