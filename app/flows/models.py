from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FlowStepType(str, Enum):
    slot = "slot"
    action = "action"
    message = "message"


class FlowStep(BaseModel):
    type: FlowStepType
    name: str | None = None
    slot: str | None = None
    prompt: str | None = None
    value_from: str | None = None
    text: str | None = None
    condition: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class Flow(BaseModel):
    id: str
    name: str
    description: str = ""
    trigger_commands: list[str] = Field(default_factory=list)
    steps: list[FlowStep]

