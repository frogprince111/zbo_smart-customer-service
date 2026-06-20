from abc import ABC, abstractmethod

import httpx

from app.core.errors import ProviderError
from app.core.interface_config import OrderQueryConfig, get_by_path, render_template


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
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int,
        order_query_config: OrderQueryConfig | None = None,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.order_query_config = order_query_config or OrderQueryConfig()

    async def health_check(self) -> bool:
        return bool(self.base_url or self.order_query_config.url)

    async def get_order(self, order_id: str) -> dict[str, str]:
        if not self.order_query_config.enabled:
            raise ProviderError("订单 HTTP 接口未启用，请配置 external_interfaces.yaml 的 business.order_query.enabled")
        variables = {
            "order_id": order_id,
            "api_key": self.order_query_config.api_key or self.api_key,
        }
        url = render_template(self.order_query_config.url or self.base_url, variables)
        headers = render_template(self.order_query_config.headers, variables)
        body = render_template(self.order_query_config.body, variables)
        method = self.order_query_config.method.upper()
        try:
            async with httpx.AsyncClient(timeout=self.order_query_config.timeout or self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.request(method, url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            raise ProviderError(f"订单 HTTP 接口调用失败: {exc}") from exc

        mapping = self.order_query_config.response_mapping
        status = str(get_by_path(payload, mapping.get("status", ""), ""))
        normalized_status = self.order_query_config.status_mapping.get(status, status or "未找到")
        return {
            "order_id": str(get_by_path(payload, mapping.get("order_id", ""), order_id)),
            "status": normalized_status,
            "tracking_no": str(get_by_path(payload, mapping.get("tracking_no", ""), "")),
        }
