from pydantic import BaseModel, Field

from app.models.schema import TableSchema


class DatasetLoadRequest(BaseModel):
    file_path: str
    table_name: str
    dataset_name: str


class DatasetResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    table_names: list[str] = Field(default_factory=list)
    tables: list[TableSchema] = Field(default_factory=list)