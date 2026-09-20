from pathlib import Path

from fastapi.testclient import TestClient

from app.core.runtime import runtime
from app.main import app
from app.services.upload_service import DatasetUploadService


SAMPLES_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "samples"
)


client = TestClient(app)


def test_load_dataset_returns_dataset_response() -> None:
    response = client.post(
        "/api/datasets",
        json={
            "file_path": str(
                SAMPLES_DIR / "customers.csv"
            ),
            "table_name": "customers_api_test",
            "dataset_name": "customer-api-demo",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["dataset_id"]
    assert payload["dataset_name"] == "customer-api-demo"
    assert payload["table_names"] == [
        "customers_api_test"
    ]

    assert len(payload["tables"]) == 1

    table = payload["tables"][0]

    assert table["name"] == "customers_api_test"
    assert table["row_count"] == 8

    assert [
        column["name"]
        for column in table["columns"]
    ] == [
        "customer_id",
        "name",
        "country",
        "segment",
        "lifetime_value",
    ]

    assert [
        column["data_type"]
        for column in table["columns"]
    ] == [
        "BIGINT",
        "VARCHAR",
        "VARCHAR",
        "VARCHAR",
        "DOUBLE",
    ]

    assert [
        column["nullable"]
        for column in table["columns"]
    ] == [
        True,
        True,
        True,
        True,
        True,
    ]

    assert table["columns"][0]["sample_values"] == [
        "1",
        "2",
        "3",
        "4",
        "5",
    ]

    assert table["columns"][2]["sample_values"] == [
        "Kenya",
        "Uganda",
        "Tanzania",
        "Rwanda",
        "Kenya",
    ]

    runtime.dataset_manager.remove_dataset(
        payload["dataset_id"]
    )


def test_get_unknown_dataset_returns_404() -> None:
    response = client.get(
        "/api/datasets/does-not-exist"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset not found."


def test_list_datasets_returns_loaded_datasets() -> None:
    response = client.post(
        "/api/datasets",
        json={
            "file_path": str(
                SAMPLES_DIR / "customers.csv"
            ),
            "table_name": "customers_list_test",
            "dataset_name": "customer-list-demo",
        },
    )

    assert response.status_code == 200

    dataset_id = response.json()["dataset_id"]

    try:
        response = client.get(
            "/api/datasets"
        )

        assert response.status_code == 200

        payload = response.json()

        matching = [
            dataset
            for dataset in payload
            if dataset["dataset_id"] == dataset_id
        ]

        assert len(matching) == 1
        assert matching[0]["dataset_name"] == (
            "customer-list-demo"
        )
        assert matching[0]["table_names"] == [
            "customers_list_test"
        ]

    finally:
        runtime.dataset_manager.remove_dataset(
            dataset_id
        )


def test_delete_dataset_returns_deleted_status() -> None:
    response = client.post(
        "/api/datasets",
        json={
            "file_path": str(
                SAMPLES_DIR / "customers.csv"
            ),
            "table_name": "customers_delete_test",
            "dataset_name": "customer-delete-demo",
        },
    )

    assert response.status_code == 200

    dataset_id = response.json()["dataset_id"]

    response = client.delete(
        f"/api/datasets/{dataset_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "deleted",
        "dataset_id": dataset_id,
    }

    response = client.get(
        f"/api/datasets/{dataset_id}"
    )

    assert response.status_code == 404


def test_upload_service_sanitizes_filename() -> None:
    table_name = DatasetUploadService._build_table_name(
        "../../Customer Sales 2026.csv"
    )

    assert table_name == "customer_sales_2026"


def test_upload_dataset_creates_dataset() -> None:
    file_path = (
        SAMPLES_DIR / "customers.csv"
    )

    with file_path.open("rb") as file:
        response = client.post(
            "/api/datasets/upload",
            files={
                "file": (
                    "customers-upload-test.csv",
                    file,
                    "text/csv",
                )
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["dataset_id"]
    assert payload["dataset_name"] == "customers-upload-test"
    assert payload["table_names"] == [
        "customers_upload_test"
    ]

    runtime.dataset_manager.remove_dataset(
        payload["dataset_id"]
    )


def test_upload_dataset_rejects_empty_file() -> None:
    response = client.post(
        "/api/datasets/upload",
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Uploaded file is empty."
    )


def test_upload_dataset_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/api/datasets/upload",
        files={
            "file": (
                "customers.json",
                b'{"customers": []}',
                "application/json",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Only CSV and Parquet files are supported."
    )