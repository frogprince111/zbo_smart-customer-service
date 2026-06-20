from abc import ABC, abstractmethod
import json
from typing import Any

import httpx

from app.core.errors import ProviderError
from app.core.interface_config import LLMEndpointConfig, get_by_path, render_template


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


class HttpLLMProvider(LLMProvider):
    """通过 external_interfaces.yaml 调用 OpenAI 兼容或自定义大模型接口。"""

    def __init__(self, config: LLMEndpointConfig):
        self.config = config

    async def health_check(self) -> bool:
        return self.config.enabled and bool(self.config.url)

    async def complete_json(self, prompt: str) -> dict[str, Any]:
        if not self.config.enabled:
            raise ProviderError("HTTP LLM 接口未启用，请配置 external_interfaces.yaml 的 llm.enabled")
        variables = {
            "prompt": prompt,
            "api_key": self.config.api_key,
            "model": self.config.model,
        }
        url = render_template(self.config.url, variables)
        headers = render_template(self.config.headers, variables)
        body = render_template(self.config.body, variables)
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.request(self.config.method.upper(), url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"LLM HTTP 接口调用失败: {exc}") from exc

        content = get_by_path(payload, self.config.content_path, payload)
        if isinstance(content, dict):
            return content
        if not isinstance(content, str):
            raise ProviderError("LLM 返回内容不是 JSON 对象或 JSON 字符串")
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ProviderError("LLM 返回内容无法解析为 JSON") from exc
