from pathlib import Path


class DatasetPathError(ValueError):
    pass


class DatasetPathValidator:
    def __init__(
        self,
        allowed_root: Path,
    ) -> None:
        self.allowed_root = allowed_root.resolve()

    def validate(
        self,
        file_path: Path,
    ) -> Path:
        resolved_path = file_path.resolve()

        try:
            resolved_path.relative_to(
                self.allowed_root
            )
        except ValueError as exc:
            raise DatasetPathError(
                "Dataset file must be located inside "
                f"{self.allowed_root}."
            ) from exc

        if not resolved_path.is_file():
            raise DatasetPathError(
                f"Dataset file does not exist: {resolved_path}"
            )

        if resolved_path.suffix.lower() not in {
            ".csv",
            ".parquet",
        }:
            raise DatasetPathError(
                "Only CSV and Parquet datasets are supported."
            )

        return resolved_path