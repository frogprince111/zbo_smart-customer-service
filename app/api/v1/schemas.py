from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    sender_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    sender_id: str
    message: str


class HealthResponse(BaseModel):
    status: str
    app: str

