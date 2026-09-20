from pathlib import Path
from uuid import uuid4

from app.core.dataset_paths import DatasetPathValidator
from app.models.schema import DatasetSchema
from app.services.dataset_service import DatasetService


class DatasetManager:
    def __init__(
        self,
        dataset_service: DatasetService,
        path_validator: DatasetPathValidator,
    ) -> None:
        self.dataset_service = dataset_service
        self.path_validator = path_validator
        self._datasets: dict[str, DatasetSchema] = {}

    def load_dataset(
        self,
        file_path: Path,
        table_name: str,
        dataset_name: str,
    ) -> tuple[str, DatasetSchema]:
        validated_path = self.path_validator.validate(
            file_path
        )

        dataset_schema = self.dataset_service.load_dataset(
            file_path=validated_path,
            table_name=table_name,
            dataset_name=dataset_name,
        )

        dataset_id = str(uuid4())

        self._datasets[dataset_id] = dataset_schema

        return dataset_id, dataset_schema

    def get_dataset(
        self,
        dataset_id: str,
    ) -> DatasetSchema | None:
        return self._datasets.get(dataset_id)

    def list_datasets(self) -> dict[str, DatasetSchema]:
        return self._datasets.copy()

    def remove_dataset(
        self,
        dataset_id: str,
    ) -> None:
        self._datasets.pop(dataset_id, None)

    def clear(self) -> None:
        self._datasets.clear()