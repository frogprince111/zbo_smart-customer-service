from abc import ABC, abstractmethod
from uuid import uuid4


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
    def __init__(self, webhook_url: str, api_key: str):
        self.webhook_url = webhook_url
        self.api_key = api_key

    async def health_check(self) -> bool:
        return bool(self.webhook_url)

    async def create_ticket(self, sender_id: str, message: str) -> dict[str, str]:
        ticket_id = f"PENDING-{uuid4().hex[:8].upper()}"
        return {"ticket_id": ticket_id, "sender_id": sender_id, "message": message}

