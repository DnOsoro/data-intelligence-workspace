from pydantic import BaseModel


class SQLAgentRequest(BaseModel):
    question: str
    schema_context: str


class SQLAgentResponse(BaseModel):
    sql: str
    explanation: str