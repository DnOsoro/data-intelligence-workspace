from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    data_type: str
    nullable: bool = True
    sample_values: list[str] = Field(default_factory=list)


class TableSchema(BaseModel):
    name: str
    row_count: int
    columns: list[ColumnSchema] = Field(default_factory=list)


class DatasetSchema(BaseModel):
    dataset_name: str
    tables: list[TableSchema] = Field(default_factory=list)