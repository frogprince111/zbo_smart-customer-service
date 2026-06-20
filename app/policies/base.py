from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel

from app.domain.models import Tracker
from app.llm.models import Command


class PolicyDecisionType(str, Enum):
    start_flow = "start_flow"
    continue_flow = "continue_flow"
    rag = "rag"
    handoff = "handoff"
    cancel = "cancel"
    fallback = "fallback"


class PolicyDecision(BaseModel):
    type: PolicyDecisionType
    flow_id: str | None = None


class Policy(ABC):
    @abstractmethod
    async def decide(self, command: Command, tracker: Tracker) -> PolicyDecision | None:
        raise NotImplementedError

