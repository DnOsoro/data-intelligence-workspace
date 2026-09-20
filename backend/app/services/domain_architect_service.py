from app.agents.domain_architect import DomainArchitect
from app.agents.table_selection_validator import (
    TableSelectionValidator,
)
from app.core.agent_cache import InMemoryMD5Cache
from app.ingestion.schema_context import SchemaContextBuilder
from app.ingestion.schema_serializer import SchemaSerializer
from app.models.agent import (
    DomainArchitectRequest,
    DomainArchitectResponse,
)
from app.models.schema import DatasetSchema


class DomainArchitectService:
    def __init__(
        self,
        agent: DomainArchitect,
    ) -> None:
        self.agent = agent
        self.context_builder = SchemaContextBuilder()
        self.serializer = SchemaSerializer()
        self.validator = TableSelectionValidator()
        self.cache = InMemoryMD5Cache[DomainArchitectResponse]()

    def select_relevant_tables(
        self,
        question: str,
        dataset_schema: DatasetSchema,
    ) -> DomainArchitectResponse:
        context_schema = self.context_builder.build(
            dataset_schema
        )

        schema_context = self.serializer.serialize(
            context_schema
        )

        cached_response = self.cache.get(
            question=question,
            schema_context=schema_context,
        )

        if cached_response is not None:
            return cached_response

        request = DomainArchitectRequest(
            question=question,
            schema_context=schema_context,
        )

        response = self.agent.select_tables(request)

        validated_response = self.validator.validate(
            response=response,
            dataset_schema=dataset_schema,
        )

        self.cache.set(
            question=question,
            schema_context=schema_context,
            value=validated_response,
        )

        return validated_response