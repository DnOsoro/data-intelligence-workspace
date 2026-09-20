from app.agents.mock_domain_architect import MockDomainArchitect
from app.models.agent import DomainArchitectRequest, DomainArchitectResponse
from app.models.schema import (
    ColumnSchema,
    DatasetSchema,
    TableSchema,
)
from app.services.domain_architect_service import (
    DomainArchitectService,
)


def build_dataset_schema() -> DatasetSchema:
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


def test_domain_architect_service_selects_tables() -> None:
    service = DomainArchitectService(
        agent=MockDomainArchitect()
    )

    response = service.select_relevant_tables(
        question=(
            "Which country has the highest "
            "lifetime customer value?"
        ),
        dataset_schema=build_dataset_schema(),
    )

    table_names = {
        selection.table_name
        for selection in response.selected_tables
    }

    assert "customers" in table_names


def test_domain_architect_service_caches_identical_requests() -> None:
    class CountingDomainArchitect(MockDomainArchitect):
        def __init__(self) -> None:
            self.call_count = 0

        def select_tables(
            self, request: DomainArchitectRequest
        ) -> DomainArchitectResponse:
            self.call_count += 1
            return super().select_tables(request)

    agent = CountingDomainArchitect()

    service = DomainArchitectService(
        agent=agent
    )

    dataset_schema = build_dataset_schema()

    question = (
        "Which country has the highest "
        "lifetime customer value?"
    )

    first_response = service.select_relevant_tables(
        question=question,
        dataset_schema=dataset_schema,
    )

    second_response = service.select_relevant_tables(
        question=question,
        dataset_schema=dataset_schema,
    )

    assert first_response == second_response
    assert agent.call_count == 1
    assert service.cache.size() == 1