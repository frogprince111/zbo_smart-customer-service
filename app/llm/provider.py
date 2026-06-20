from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def complete_json(self, prompt: str) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def __init__(self, illegal_json: bool = False):
        self.illegal_json = illegal_json

    async def health_check(self) -> bool:
        return True

    async def complete_json(self, prompt: str) -> dict[str, Any]:
        if self.illegal_json:
            raise ValueError("LLM 返回非法 JSON")
        text = prompt.lower()
        if "转人工" in prompt or "人工客服" in prompt:
            return {"type": "handoff", "confidence": 1.0}
        if "取消" in prompt or "不用了" in prompt:
            return {"type": "cancel", "confidence": 1.0}
        if "七天" in prompt or "退货" in prompt:
            return {"type": "knowledge_qa", "confidence": 0.95}
        if "订单" in prompt:
            return {"type": "start_flow", "name": "query_order", "confidence": 0.95}
        digits = "".join(ch for ch in prompt if ch.isdigit())
        if digits:
            return {"type": "provide_slot", "slots": {"order_id": digits}, "confidence": 0.9}
        if "bad_json" in text:
            raise ValueError("LLM 返回非法 JSON")
        return {"type": "unknown", "confidence": 0.2}

