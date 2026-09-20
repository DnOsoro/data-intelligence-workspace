from pydantic import BaseModel, Field


class TableSelection(BaseModel):
    table_name: str
    relevance_reason: str


class DomainArchitectRequest(BaseModel):
    question: str
    schema_context: str


class DomainArchitectResponse(BaseModel):
    selected_tables: list[TableSelection] = Field(
        default_factory=list
    )
    confidence: float = 0.0