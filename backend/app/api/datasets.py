from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.runtime import runtime
from app.models.dataset import (
    DatasetLoadRequest,
    DatasetResponse,
)
from app.services.upload_service import DatasetUploadService


router = APIRouter(
    prefix="/api/datasets",
    tags=["datasets"],
)


@router.post(
    "/upload",
    response_model=DatasetResponse,
)
async def upload_dataset(
    file: UploadFile = File(...),
) -> DatasetResponse:
    try:
        upload_service = DatasetUploadService(
            dataset_manager=runtime.dataset_manager,
            upload_root=runtime.upload_root,
        )

        dataset_id, schema = (
            await upload_service.upload_dataset(
                file=file
            )
        )

        return DatasetResponse(
            dataset_id=dataset_id,
            dataset_name=schema.dataset_name,
            table_names=[
                table.name
                for table in schema.tables
            ],
            tables=schema.tables,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Dataset upload failed.",
        ) from exc


@router.post(
    "",
    response_model=DatasetResponse,
)
async def load_dataset(
    request: DatasetLoadRequest,
) -> DatasetResponse:
    try:
        dataset_id, schema = runtime.dataset_manager.load_dataset(
            file_path=Path(request.file_path),
            table_name=request.table_name,
            dataset_name=request.dataset_name,
        )

        return DatasetResponse(
            dataset_id=dataset_id,
            dataset_name=schema.dataset_name,
            table_names=[
                table.name
                for table in schema.tables
            ],
            tables=schema.tables,
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Dataset loading failed.",
        ) from exc


@router.get(
    "",
)
async def list_datasets() -> list[DatasetResponse]:
    datasets = runtime.dataset_manager.list_datasets()

    return [
        DatasetResponse(
            dataset_id=dataset_id,
            dataset_name=schema.dataset_name,
            table_names=[
                table.name
                for table in schema.tables
            ],
            tables=schema.tables,
        )
        for dataset_id, schema in datasets.items()
    ]


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponse,
)
async def get_dataset(
    dataset_id: str,
) -> DatasetResponse:
    schema = runtime.dataset_manager.get_dataset(
        dataset_id
    )

    if schema is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    return DatasetResponse(
        dataset_id=dataset_id,
        dataset_name=schema.dataset_name,
        table_names=[
            table.name
            for table in schema.tables
        ],
        tables=schema.tables,
    )


@router.delete(
    "/{dataset_id}",
)
async def remove_dataset(
    dataset_id: str,
) -> dict[str, str]:
    schema = runtime.dataset_manager.get_dataset(
        dataset_id
    )

    if schema is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    runtime.dataset_manager.remove_dataset(
        dataset_id
    )

    return {
        "status": "deleted",
        "dataset_id": dataset_id,
    }