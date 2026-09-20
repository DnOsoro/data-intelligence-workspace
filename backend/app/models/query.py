from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str
    dataset_id: str


class QueryResult(BaseModel):
    columns: list[str] = Field(default_factory=list)
    rows: list[list[object]] = Field(default_factory=list)


class QueryExecutionMetadata(BaseModel):
    query_id: str
    selected_tables: list[str] = Field(default_factory=list)
    rows_returned: int = 0

    agent_1_duration_ms: float = 0.0
    agent_2_duration_ms: float = 0.0
    sql_validation_duration_ms: float = 0.0
    database_execution_duration_ms: float = 0.0
    total_duration_ms: float = 0.0


class QueryExecutionResponse(BaseModel):
    question: str
    selected_tables: list[str] = Field(default_factory=list)
    sql: str
    explanation: str
    result: QueryResult
    metadata: QueryExecutionMetadata