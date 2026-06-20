from pydantic import BaseModel


class Document(BaseModel):
    id: str
    text: str
    source: str


class Chunk(BaseModel):
    id: str
    text: str
    source: str
    score: float = 0.0


class Citation(BaseModel):
    source: str
    text: str

