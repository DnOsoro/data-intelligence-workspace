from pathlib import Path

import pytest

from app.core.dataset_paths import (
    DatasetPathError,
    DatasetPathValidator,
)


def test_validator_accepts_dataset_inside_allowed_root(
    tmp_path: Path,
) -> None:
    dataset_file = tmp_path / "customers.csv"
    dataset_file.write_text(
        "id,name\n1,Acme\n",
        encoding="utf-8",
    )

    validator = DatasetPathValidator(tmp_path)

    result = validator.validate(dataset_file)

    assert result == dataset_file.resolve()


def test_validator_rejects_path_outside_allowed_root(
    tmp_path: Path,
) -> None:
    allowed_root = tmp_path / "data"
    allowed_root.mkdir()

    outside_file = tmp_path / "secret.csv"
    outside_file.write_text(
        "secret\nvalue\n",
        encoding="utf-8",
    )

    validator = DatasetPathValidator(allowed_root)

    with pytest.raises(
        DatasetPathError,
        match="inside",
    ):
        validator.validate(outside_file)


def test_validator_rejects_missing_file(
    tmp_path: Path,
) -> None:
    validator = DatasetPathValidator(tmp_path)

    with pytest.raises(
        DatasetPathError,
        match="does not exist",
    ):
        validator.validate(
            tmp_path / "missing.csv"
        )


def test_validator_rejects_unsupported_format(
    tmp_path: Path,
) -> None:
    dataset_file = tmp_path / "customers.txt"
    dataset_file.write_text(
        "data",
        encoding="utf-8",
    )

    validator = DatasetPathValidator(tmp_path)

    with pytest.raises(
        DatasetPathError,
        match="Only CSV and Parquet",
    ):
        validator.validate(dataset_file)