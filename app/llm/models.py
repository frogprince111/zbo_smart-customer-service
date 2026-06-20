from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CommandType(str, Enum):
    start_flow = "start_flow"
    provide_slot = "provide_slot"
    knowledge_qa = "knowledge_qa"
    handoff = "handoff"
    cancel = "cancel"
    smalltalk = "smalltalk"
    unknown = "unknown"


class Command(BaseModel):
    type: CommandType
    name: str | None = None
    slots: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    raw_text: str = ""

