from pathlib import Path

from app.core.dataset_paths import DatasetPathValidator
from app.database.duckdb_manager import DuckDBManager
from app.services.dataset_manager import DatasetManager
from app.services.dataset_service import DatasetService


def test_dataset_manager_loads_and_retrieves_dataset() -> None:
    database = DuckDBManager()
    service = DatasetService(database)
    manager = DatasetManager(
        dataset_service=service,
        path_validator=DatasetPathValidator(
            Path("../data")
        ),
    )

    try:
        dataset_id, schema = manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.csv"
            ),
            table_name="customers",
            dataset_name="customer-demo",
        )

        assert dataset_id
        assert schema.dataset_name == "customer-demo"

        stored_schema = manager.get_dataset(
            dataset_id
        )

        assert stored_schema is not None
        assert stored_schema.dataset_name == "customer-demo"
        assert stored_schema.tables[0].name == "customers"

    finally:
        database.close()


def test_dataset_manager_returns_none_for_unknown_dataset() -> None:
    database = DuckDBManager()
    service = DatasetService(database)
    manager = DatasetManager(
        dataset_service=service,
        path_validator=DatasetPathValidator(
            Path("../data")
        ),
    )

    try:
        assert manager.get_dataset("unknown") is None
    finally:
        database.close()


def test_dataset_manager_removes_dataset() -> None:
    database = DuckDBManager()
    service = DatasetService(database)
    manager = DatasetManager(
        dataset_service=service,
        path_validator=DatasetPathValidator(
            Path("../data")
        ),
    )

    try:
        dataset_id, _ = manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.csv"
            ),
            table_name="customers",
            dataset_name="customer-demo",
        )

        manager.remove_dataset(dataset_id)

        assert manager.get_dataset(dataset_id) is None

    finally:
        database.close()


def test_dataset_manager_lists_loaded_datasets() -> None:
    database = DuckDBManager()
    service = DatasetService(database)
    manager = DatasetManager(
        dataset_service=service,
        path_validator=DatasetPathValidator(
            Path("../data")
        ),
    )

    try:
        first_id, _ = manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.csv"
            ),
            table_name="customers",
            dataset_name="customer-demo",
        )

        second_id, _ = manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.parquet"
            ),
            table_name="customers_archive",
            dataset_name="archive-demo",
        )

        datasets = manager.list_datasets()

        assert set(datasets.keys()) == {
            first_id,
            second_id,
        }

        assert (
            datasets[first_id].dataset_name
            == "customer-demo"
        )

        assert (
            datasets[second_id].dataset_name
            == "archive-demo"
        )

    finally:
        database.close()


def test_dataset_manager_clears_all_datasets() -> None:
    database = DuckDBManager()
    service = DatasetService(database)
    manager = DatasetManager(
        dataset_service=service,
        path_validator=DatasetPathValidator(
            Path("../data")
        ),
    )

    try:
        first_id, _ = manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.csv"
            ),
            table_name="customers",
            dataset_name="customer-demo",
        )

        second_id, _ = manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.parquet"
            ),
            table_name="customers_archive",
            dataset_name="archive-demo",
        )

        manager.clear()

        assert manager.list_datasets() == {}
        assert manager.get_dataset(first_id) is None
        assert manager.get_dataset(second_id) is None

    finally:
        database.close()