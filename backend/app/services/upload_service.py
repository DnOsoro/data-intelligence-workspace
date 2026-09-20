from pathlib import Path

from fastapi import UploadFile

from app.models.schema import DatasetSchema
from app.services.dataset_manager import DatasetManager


class DatasetUploadService:
    def __init__(
        self,
        dataset_manager: DatasetManager,
        upload_root: Path,
    ) -> None:
        self.dataset_manager = dataset_manager
        self.upload_root = upload_root.resolve()

        self.upload_root.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def upload_dataset(
        self,
        file: UploadFile,
    ) -> tuple[str, DatasetSchema]:
        if not file.filename:
            raise ValueError(
                "Uploaded file must have a filename."
            )

        original_name = Path(file.filename).name
        suffix = Path(original_name).suffix.lower()

        if suffix not in {".csv", ".parquet"}:
            raise ValueError(
                "Only CSV and Parquet files are supported."
            )

        dataset_directory = (
            self.upload_root / "pending"
        )

        dataset_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            dataset_directory / original_name
        )

        contents = await file.read()

        if not contents:
            raise ValueError(
                "Uploaded file is empty."
            )

        file_path.write_bytes(contents)

        table_name = self._build_table_name(
            original_name
        )

        dataset_name = Path(
            original_name
        ).stem

        try:
            dataset_id, schema = (
                self.dataset_manager.load_dataset(
                    file_path=file_path,
                    table_name=table_name,
                    dataset_name=dataset_name,
                )
            )

            return dataset_id, schema

        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

    @staticmethod
    def _build_table_name(
        filename: str,
    ) -> str:
        stem = Path(filename).stem

        table_name = "".join(
            character
            if character.isalnum() or character == "_"
            else "_"
            for character in stem
        )

        table_name = table_name.strip("_")

        if not table_name:
            table_name = "dataset"

        if table_name[0].isdigit():
            table_name = f"dataset_{table_name}"

        return table_name.lower()