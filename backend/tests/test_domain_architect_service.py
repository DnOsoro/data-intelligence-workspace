from app.agents.domain_architect import DomainArchitect
from app.models.agent import (
    DomainArchitectRequest,
    DomainArchitectResponse,
    TableSelection,
)
from app.models.schema import (
    ColumnSchema,
    DatasetSchema,
    TableSchema,
)
from app.services.domain_architect_service import (
    DomainArchitectService,
)


class FakeDomainArchitect(DomainArchitect):
    def __init__(self) -> None:
        self.call_count = 0

    def select_tables(
        self,
        request: DomainArchitectRequest,
    ) -> DomainArchitectResponse:
        self.call_count += 1

        return DomainArchitectResponse(
            selected_tables=[
                TableSelection(
                    table_name="customers",
                    relevance_reason=(
                        "Customer lifetime value is "
                        "stored in this table."
                    ),
                )
            ],
            confidence=0.95,
        )


def build_dataset_schema() -> DatasetSchema:
    return DatasetSchema(
        dataset_name="customer_analytics",
        tables=[
            TableSchema(
                name="customers",
                row_count=3,
                columns=[
                    ColumnSchema(
                        name="customer_id",
                        data_type="INTEGER",
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


def test_domain_architect_service_returns_validated_response() -> None:
    agent = FakeDomainArchitect()

    service = DomainArchitectService(
        agent=agent
    )

    response = service.select_relevant_tables(
        question=(
            "Which country has the highest "
            "lifetime customer value?"
        ),
        dataset_schema=build_dataset_schema(),
    )

    assert response.selected_tables[0].table_name == (
        "customers"
    )
    assert response.confidence == 0.95
    assert agent.call_count == 1


def test_domain_architect_service_uses_cache() -> None:
    agent = FakeDomainArchitect()

    service = DomainArchitectService(
        agent=agent
    )

    schema = build_dataset_schema()

    first_response = service.select_relevant_tables(
        question="Which customers have the highest value?",
        dataset_schema=schema,
    )

    second_response = service.select_relevant_tables(
        question="Which customers have the highest value?",
        dataset_schema=schema,
    )

    assert first_response == second_response
    assert agent.call_count == 1