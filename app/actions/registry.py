from app.actions.base import Action
from app.core.errors import ValidationError


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        self._actions[action.name] = action

    def get(self, name: str) -> Action:
        if name not in self._actions:
            raise ValidationError(f"Action 未注册: {name}")
        return self._actions[name]

    def names(self) -> list[str]:
        return sorted(self._actions)

