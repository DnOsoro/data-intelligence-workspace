import pytest

from app.agents.table_selection_validator import (
    TableSelectionValidator,
)
from app.models.agent import (
    DomainArchitectResponse,
    TableSelection,
)
from app.models.schema import (
    ColumnSchema,
    DatasetSchema,
    TableSchema,
)


def create_dataset_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="customer_analytics",
        tables=[
            TableSchema(
                name="customers",
                row_count=8,
                columns=[
                    ColumnSchema(
                        name="customer_id",
                        data_type="BIGINT",
                    ),
                    ColumnSchema(
                        name="country",
                        data_type="VARCHAR",
                    ),
                    ColumnSchema(
                        name="lifetime_value",
                        data_type="DOUBLE",
                    ),
                ],
            )
        ],
    )


def test_validator_accepts_authorized_table() -> None:
    validator = TableSelectionValidator()

    response = DomainArchitectResponse(
        selected_tables=[
            TableSelection(
                table_name="customers",
                relevance_reason=(
                    "Contains customer country "
                    "and lifetime value."
                ),
            )
        ],
        confidence=0.95,
    )

    validated = validator.validate(
        response=response,
        dataset_schema=create_dataset_schema(),
    )

    assert len(validated.selected_tables) == 1
    assert validated.selected_tables[0].table_name == "customers"


def test_validator_rejects_unauthorized_table() -> None:
    validator = TableSelectionValidator()

    response = DomainArchitectResponse(
        selected_tables=[
            TableSelection(
                table_name="payments",
                relevance_reason=(
                    "Contains payment information."
                ),
            )
        ],
        confidence=0.90,
    )

    with pytest.raises(
        ValueError,
        match="unauthorized table",
    ):
        validator.validate(
            response=response,
            dataset_schema=create_dataset_schema(),
        )


def test_validator_accepts_empty_selection() -> None:
    validator = TableSelectionValidator()

    response = DomainArchitectResponse(
        selected_tables=[],
        confidence=0.0,
    )

    validated = validator.validate(
        response=response,
        dataset_schema=create_dataset_schema(),
    )

    assert validated.selected_tables == []


def test_validator_rejects_invalid_confidence() -> None:
    validator = TableSelectionValidator()

    response = DomainArchitectResponse(
        selected_tables=[],
        confidence=1.5,
    )

    with pytest.raises(
        ValueError,
        match="confidence",
    ):
        validator.validate(
            response=response,
            dataset_schema=create_dataset_schema(),
        )


def test_normalizes_qualified_table_name() -> None:
    validator = TableSelectionValidator()

    response = DomainArchitectResponse(
        selected_tables=[
            TableSelection(
                table_name="customer_analytics.customers",
                relevance_reason="Customer lifetime value analysis.",
            )
        ],
        confidence=0.95,
    )

    dataset_schema = DatasetSchema(
        dataset_name="customer_analytics",
        tables=[
            TableSchema(
                name="customers",
                row_count=8,
                columns=[],
            )
        ],
    )

    validated = validator.validate(
        response=response,
        dataset_schema=dataset_schema,
    )

    assert validated.selected_tables[0].table_name == "customers"