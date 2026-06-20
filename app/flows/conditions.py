from typing import Any

from app.domain.models import Tracker


class ConditionEvaluator:
    """极简条件求值器，支持 slot.key、not slot.key 与等值判断。"""

    def evaluate(self, expression: str | None, tracker: Tracker) -> bool:
        if not expression:
            return True
        exp = expression.strip()
        if exp.startswith("not slot."):
            return not bool(tracker.slots.get(exp.removeprefix("not slot.")))
        if exp.startswith("slot.") and "==" in exp:
            left, right = [part.strip() for part in exp.split("==", 1)]
            key = left.removeprefix("slot.")
            expected: Any = right.strip("'\"")
            return str(tracker.slots.get(key)) == expected
        if exp.startswith("slot."):
            return bool(tracker.slots.get(exp.removeprefix("slot.")))
        return False

