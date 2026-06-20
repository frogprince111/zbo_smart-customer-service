from app.actions.base import Action, ActionResult
from app.domain.models import Tracker
from app.providers.business import BusinessProvider
from app.providers.handoff import HandoffProvider


class QueryOrderAction(Action):
    name = "query_order"

    def __init__(self, business_provider: BusinessProvider):
        self.business_provider = business_provider

    async def run(self, tracker: Tracker, params: dict | None = None) -> ActionResult:
        order_id = str(tracker.slots.get("order_id") or "")
        try:
            order = await self.business_provider.get_order(order_id)
        except Exception:
            return ActionResult(text="订单系统暂时不可用，已为你保留查询请求，请稍后再试。", done=True)
        if order["status"] == "已发货":
            return ActionResult(text=f"订单已发货，物流单号为 {order['tracking_no']}", data=order)
        return ActionResult(text=f"未查询到订单 {order_id}，请核对订单号后再试。", data=order)


class HandoffAction(Action):
    name = "create_handoff_ticket"

    def __init__(self, handoff_provider: HandoffProvider):
        self.handoff_provider = handoff_provider

    async def run(self, tracker: Tracker, params: dict | None = None) -> ActionResult:
        ticket = await self.handoff_provider.create_ticket(tracker.sender_id, params.get("message", "") if params else "")
        return ActionResult(text=f"已创建模拟人工客服工单，工单号为 {ticket['ticket_id']}", data=ticket)

