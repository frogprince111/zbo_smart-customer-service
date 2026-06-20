from pydantic import BaseModel

from app.domain.models import Tracker
from app.llm.models import Command
from app.policies.base import PolicyDecision


class AgentState(BaseModel):
    tracker: Tracker
    message: str
    command: Command | None = None
    decision: PolicyDecision | None = None
    response: str = ""

