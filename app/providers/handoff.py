from abc import ABC, abstractmethod
from uuid import uuid4

import httpx

from app.core.errors import ProviderError
from app.core.interface_config import HttpEndpointConfig, get_by_path, render_template


class HandoffProvider(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create_ticket(self, sender_id: str, message: str) -> dict[str, str]:
        raise NotImplementedError


class MockHandoffProvider(HandoffProvider):
    async def health_check(self) -> bool:
        return True

    async def create_ticket(self, sender_id: str, message: str) -> dict[str, str]:
        ticket_id = f"MOCK-{uuid4().hex[:8].upper()}"
        return {"ticket_id": ticket_id, "sender_id": sender_id, "message": message}


class WebhookHandoffProvider(HandoffProvider):
    def __init__(self, webhook_url: str, api_key: str, ticket_config: HttpEndpointConfig | None = None):
        self.webhook_url = webhook_url
        self.api_key = api_key
        self.ticket_config = ticket_config or HttpEndpointConfig()

    async def health_check(self) -> bool:
        return bool(self.webhook_url or self.ticket_config.url)

    async def create_ticket(self, sender_id: str, message: str) -> dict[str, str]:
        if not self.ticket_config.enabled:
            ticket_id = f"PENDING-{uuid4().hex[:8].upper()}"
            return {"ticket_id": ticket_id, "sender_id": sender_id, "message": message}
        variables = {
            "sender_id": sender_id,
            "message": message,
            "api_key": self.ticket_config.api_key or self.api_key,
        }
        url = render_template(self.ticket_config.url or self.webhook_url, variables)
        headers = render_template(self.ticket_config.headers, variables)
        body = render_template(self.ticket_config.body, variables)
        try:
            async with httpx.AsyncClient(timeout=self.ticket_config.timeout) as client:
                response = await client.request(self.ticket_config.method.upper(), url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"人工客服 Webhook 调用失败: {exc}") from exc
        ticket_id = str(get_by_path(payload, self.ticket_config.response_mapping.get("ticket_id", ""), ""))
        if not ticket_id:
            ticket_id = f"PENDING-{uuid4().hex[:8].upper()}"
        return {"ticket_id": ticket_id, "sender_id": sender_id, "message": message}
