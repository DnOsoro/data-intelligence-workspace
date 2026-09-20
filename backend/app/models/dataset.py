from pydantic import BaseModel, Field


class DatasetLoadRequest(BaseModel):
    file_path: str
    table_name: str
    dataset_name: str


class DatasetResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    table_names: list[str] = Field(default_factory=list)