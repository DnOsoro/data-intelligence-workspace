import logging

from fastapi import APIRouter, HTTPException

from app.core.runtime import runtime
from app.models.query import (
    QueryExecutionResponse,
    QueryRequest,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["query"],
)


@router.post(
    "/query",
    response_model=QueryExecutionResponse,
)
async def execute_query(
    request: QueryRequest,
) -> QueryExecutionResponse:
    dataset_schema = runtime.dataset_manager.get_dataset(
        request.dataset_id
    )

    if dataset_schema is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    try:
        return runtime.query_orchestrator.execute(
            question=request.question,
            dataset_schema=dataset_schema,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception(
            "Query execution failed for dataset_id=%s",
            request.dataset_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Query execution failed.",
        ) from None