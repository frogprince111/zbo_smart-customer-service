from app.llm.models import Command, CommandType
from app.llm.prompt import PromptBuilder
from app.llm.provider import LLMProvider


class CommandParser:
    def __init__(self, llm: LLMProvider, prompt_builder: PromptBuilder | None = None):
        self.llm = llm
        self.prompt_builder = prompt_builder or PromptBuilder()

    async def parse(self, message: str) -> Command:
        prompt = self.prompt_builder.build_command_prompt(message)
        try:
            payload = await self.llm.complete_json(prompt)
            command = Command.model_validate(payload)
        except Exception:
            command = Command(type=CommandType.unknown, confidence=0.0)
        command.raw_text = message
        return command

