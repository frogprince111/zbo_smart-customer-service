from app.domain.models import Tracker
from app.llm.models import Command
from app.policies.base import Policy, PolicyDecision, PolicyDecisionType


class PolicyEnsemble:
    def __init__(self, policies: list[Policy]):
        self.policies = policies

    async def decide(self, command: Command, tracker: Tracker) -> PolicyDecision:
        for policy in self.policies:
            decision = await policy.decide(command, tracker)
            if decision is not None:
                return decision
        return PolicyDecision(type=PolicyDecisionType.fallback)

