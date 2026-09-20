from pathlib import Path

from app.core.runtime import ApplicationRuntime


def test_runtime_shares_database_between_dataset_and_query_services() -> None:
    runtime = ApplicationRuntime()

    try:
        dataset_id, schema = runtime.dataset_manager.load_dataset(
            file_path=Path(
                "../data/samples/customers.csv"
            ),
            table_name="customers",
            dataset_name="customer-demo",
        )

        assert dataset_id
        assert schema.dataset_name == "customer-demo"

        stored_schema = runtime.dataset_manager.get_dataset(
            dataset_id
        )

        assert stored_schema is not None
        assert stored_schema.tables[0].name == "customers"

        result = runtime.database.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()

        assert result is not None
        assert result[0] == 8

    finally:
        runtime.close()