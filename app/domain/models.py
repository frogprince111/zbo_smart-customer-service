from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    user = "user"
    assistant = "assistant"
    action = "action"
    slot = "slot"
    command = "command"


class Event(BaseModel):
    type: EventType
    text: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Slot(BaseModel):
    name: str
    value: Any | None = None
    required: bool = False
    prompt: str | None = None

    @property
    def filled(self) -> bool:
        return self.value not in (None, "")


class StackFrame(BaseModel):
    flow_id: str
    step_index: int = 0
    slots: dict[str, Any] = Field(default_factory=dict)


class DialogueStack(BaseModel):
    frames: list[StackFrame] = Field(default_factory=list)

    def push(self, frame: StackFrame) -> None:
        self.frames.append(frame)

    def pop(self) -> StackFrame | None:
        return self.frames.pop() if self.frames else None

    def current(self) -> StackFrame | None:
        return self.frames[-1] if self.frames else None

    def clear(self) -> None:
        self.frames.clear()


class Tracker(BaseModel):
    sender_id: str
    session_id: str = Field(default_factory=lambda: uuid4().hex)
    slots: dict[str, Any] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)
    stack: DialogueStack = Field(default_factory=DialogueStack)

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def set_slot(self, name: str, value: Any) -> None:
        self.slots[name] = value
        current = self.stack.current()
        if current is not None:
            current.slots[name] = value
        self.add_event(Event(type=EventType.slot, data={"name": name, "value": value}))

