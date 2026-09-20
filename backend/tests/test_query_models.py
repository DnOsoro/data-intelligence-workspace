from pydantic import ValidationError

from app.models.query import (
    QueryExecutionMetadata,
    QueryExecutionResponse,
    QueryRequest,
    QueryResult,
)


def test_query_request_accepts_valid_request() -> None:
    request = QueryRequest(
        question="What are the top customers by lifetime value?",
        dataset_id="dataset-123",
    )

    assert request.question == (
        "What are the top customers by lifetime value?"
    )
    assert request.dataset_id == "dataset-123"


def test_query_request_rejects_missing_question() -> None:
    try:
        QueryRequest(
            dataset_id="dataset-123",
        )
    except ValidationError as exc:
        assert "question" in str(exc)
    else:
        raise AssertionError(
            "Expected ValidationError."
        )


def test_query_request_rejects_missing_dataset_id() -> None:
    try:
        QueryRequest(
            question="Show all customers",
        )
    except ValidationError as exc:
        assert "dataset_id" in str(exc)
    else:
        raise AssertionError(
            "Expected ValidationError."
        )


def test_query_result_defaults_to_empty_values() -> None:
    result = QueryResult()

    assert result.columns == []
    assert result.rows == []


def test_query_execution_metadata_defaults_to_zero_timings() -> None:
    metadata = QueryExecutionMetadata(
        query_id="query-123",
    )

    assert metadata.selected_tables == []
    assert metadata.rows_returned == 0
    assert metadata.agent_1_duration_ms == 0.0
    assert metadata.agent_2_duration_ms == 0.0
    assert metadata.sql_validation_duration_ms == 0.0
    assert metadata.database_execution_duration_ms == 0.0
    assert metadata.total_duration_ms == 0.0