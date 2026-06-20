from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from app.domain.models import Tracker


class ActionResult(BaseModel):
    text: str
    data: dict[str, Any] = Field(default_factory=dict)
    done: bool = True


class Action(ABC):
    name: str

    @abstractmethod
    async def run(self, tracker: Tracker, params: dict[str, Any] | None = None) -> ActionResult:
        raise NotImplementedError

