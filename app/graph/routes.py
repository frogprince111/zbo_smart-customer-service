from app.policies.base import PolicyDecisionType


def route_by_decision(decision_type: PolicyDecisionType) -> str:
    return decision_type.value

