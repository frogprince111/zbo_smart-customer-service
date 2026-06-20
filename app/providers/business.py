from abc import ABC, abstractmethod

from app.core.errors import ProviderError


class BusinessProvider(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_order(self, order_id: str) -> dict[str, str]:
        raise NotImplementedError


class MockBusinessProvider(BusinessProvider):
    def __init__(self, fail: bool = False):
        self.fail = fail

    async def health_check(self) -> bool:
        return not self.fail

    async def get_order(self, order_id: str) -> dict[str, str]:
        if self.fail:
            raise ProviderError("模拟订单系统暂时不可用")
        if order_id == "10001":
            return {"order_id": "10001", "status": "已发货", "tracking_no": "SF10001"}
        return {"order_id": order_id, "status": "未找到", "tracking_no": ""}


class HttpBusinessProvider(BusinessProvider):
    def __init__(self, base_url: str, api_key: str, timeout: int):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    async def health_check(self) -> bool:
        return bool(self.base_url)

    async def get_order(self, order_id: str) -> dict[str, str]:
        raise ProviderError("HTTP 订单 Provider 已预留接口，请按真实协议实现适配器")

