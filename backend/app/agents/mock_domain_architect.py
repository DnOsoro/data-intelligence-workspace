from app.agents.domain_architect import DomainArchitect
from app.models.agent import (
    DomainArchitectRequest,
    DomainArchitectResponse,
    TableSelection,
)


class MockDomainArchitect(DomainArchitect):
    def select_tables(
        self,
        request: DomainArchitectRequest,
    ) -> DomainArchitectResponse:
        if "customers" in request.schema_context.lower():
            return DomainArchitectResponse(
                selected_tables=[
                    TableSelection(
                        table_name="customers",
                        relevance_reason=(
                            "The customers table is available "
                            "in the supplied schema context."
                        ),
                    )
                ],
                confidence=1.0,
            )

        return DomainArchitectResponse(
            selected_tables=[],
            confidence=0.0,
        )