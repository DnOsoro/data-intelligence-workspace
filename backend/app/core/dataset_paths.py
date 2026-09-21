from pathlib import Path


class DatasetPathError(ValueError):
    pass


class DatasetPathValidator:
    def __init__(
        self,
        allowed_root: Path | None = None,
        allowed_roots: list[Path] | None = None,
    ) -> None:
        roots: list[Path] = []

        if allowed_root is not None:
            roots.append(allowed_root)

        if allowed_roots is not None:
            roots.extend(allowed_roots)

        if not roots:
            raise ValueError(
                "At least one allowed dataset root is required."
            )

        self.allowed_roots = [
            root.resolve()
            for root in roots
        ]

    def validate(
        self,
        file_path: Path,
    ) -> Path:
        resolved_path = file_path.resolve()

        is_allowed = any(
            resolved_path.is_relative_to(root)
            for root in self.allowed_roots
        )

        if not is_allowed:
            allowed_locations = ", ".join(
                str(root)
                for root in self.allowed_roots
            )

            raise DatasetPathError(
                "Dataset file must be located inside "
                f"one of: {allowed_locations}."
            )

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