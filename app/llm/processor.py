from app.domain.models import Tracker
from app.llm.models import Command, CommandType


class CommandProcessor:
    """将命令中的 Slot 写入 Tracker。"""

    def apply(self, command: Command, tracker: Tracker) -> None:
        if command.type == CommandType.provide_slot:
            for name, value in command.slots.items():
                tracker.set_slot(name, value)

