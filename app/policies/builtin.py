from app.domain.models import Tracker
from app.llm.models import Command, CommandType
from app.policies.base import Policy, PolicyDecision, PolicyDecisionType


class CommandPolicy(Policy):
    async def decide(self, command: Command, tracker: Tracker) -> PolicyDecision | None:
        if command.type == CommandType.cancel:
            return PolicyDecision(type=PolicyDecisionType.cancel)
        if command.type == CommandType.knowledge_qa:
            return PolicyDecision(type=PolicyDecisionType.rag)
        if command.type == CommandType.handoff:
            return PolicyDecision(type=PolicyDecisionType.handoff)
        if command.type == CommandType.start_flow and command.name:
            return PolicyDecision(type=PolicyDecisionType.start_flow, flow_id=command.name)
        if command.type == CommandType.provide_slot and tracker.stack.current():
            return PolicyDecision(type=PolicyDecisionType.continue_flow, flow_id=tracker.stack.current().flow_id)
        return None


class FallbackPolicy(Policy):
    async def decide(self, command: Command, tracker: Tracker) -> PolicyDecision | None:
        if tracker.stack.current():
            return PolicyDecision(type=PolicyDecisionType.continue_flow, flow_id=tracker.stack.current().flow_id)
        return PolicyDecision(type=PolicyDecisionType.fallback)

